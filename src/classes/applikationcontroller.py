from __future__ import annotations
from typing import Callable
import sys
import pygame
import datetime
import jsonpickle

from src.classes.applikationmodel import ApplikationModell
from src.classes.applikationview import ApplikationView
from src.classes.controllerstatus import ControllerStatus
from src.classes.datenprozessor import DatenProcessor
from src.classes.stoppuhr import FlexibleZeit
from src.classes.viewdatenmodell import ViewDatenmodell
from src.classes.bledevice import PulswerteDatenObjekt, BLEHeartRateData
from src.modules import audiomodul
import src.classes.commandmapper as cmd


class ApplikationController:

    def __init__(self, model: ApplikationModell | None = None, views: list[ApplikationView] | None = None,
                 log_file: str = None):
        self.modell: ApplikationModell = model
        self.views: list[ApplikationView] = views
        self.daten: DatenProcessor = DatenProcessor()
        self.log_file: str = log_file

    def process_tastatureingabe(self, status: ControllerStatus = None) -> ControllerStatus:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cmd.beende_programm(status=status)
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Taste: {event.key} {event.mod}")  # TODO Zum Ermitteln eines Taste-CODES die Zeile auskommentieren
                status.gedrueckte_taste = cmd.key_mapper(event.key, event.mod)
                if status.gedrueckte_taste:
                    # Fuehre den zur gedrueckten Taste passenden Befehl aus.
                    funktion, argumente = cmd.command_mapper(status)
                    if isinstance(result := funktion(**argumente), self.modell.ergo.__class__):
                        status.modell.ergo = result
        return status

    def update_ergometer(self, status: ControllerStatus) -> None:
        status.modell.ergo = (self.modell.ergo.
                              setBremse(status.werte_nach_trainngsplan[1]).
                              update_device_werte(self.modell.board.device_daten))

    @staticmethod
    def update_musik(status: ControllerStatus) -> None:
        # TODO Evtl. Musik mit Pausenfunktion syncronisieren
        # TODO Zeige in GUI an, ob Playlist verfuegbar ist
        # TODO Sollte vielleicht in ControllerStatus ausgelagert werden?
        result = audiomodul.play_audio_schedule(playlist=status.audio_playlist,
                                                aktuelle_zeit_in_ms=status.gestoppte_zeit.als_ms(),
                                                busy_status=pygame.mixer.music.get_busy())
        audiomodul.AUDIOOBJEKT_AKTIVE, status.audio_playlist, (audiofunc, args) = result
        # Wenn Trainingszeit abgelaufen ist, lasse das letzte Lied auslaufen.
        if status.gestoppte_zeit.als_ms() >= status.modell.trainingsprogramm.trainingszeit_dauer_gesamt():
            return None
        audiofunc(**args)
        if audiofunc == audiomodul.fadeout_musik:   # FLAG um doppeltes fadeout zu verhindern
            audiomodul.AUDIO_VOLUME_FADINGOUT = True
        elif args:
            audiomodul.AUDIO_VOLUME_FADINGOUT = False

    def update_pulswerte(self, status: ControllerStatus) -> None:
        if status.modell.puls_device.connected:
            status.modell.pulsmesser = status.modell.pulsmesser.verarbeite_device_werte(
                status.modell.puls_device.lese_messwerte())
        else:
            if status.es_ist_zeit_fuer_update():
                status.modell.pulsmesser = status.modell.pulsmesser.verarbeite_device_werte(
                    PulswerteDatenObjekt(zeitstempel=0, ble_objekt=BLEHeartRateData(16, 0, [])).ble_objekt)

    def update_daten(self, status: ControllerStatus,
                     daten_modell: ViewDatenmodell) -> tuple[ControllerStatus, ViewDatenmodell]:
        # TODO Unterteile in Updates, die waherend der Pause nicht durchgefuehrt werden muessen und staendigen
        # TODO Herzwerte durch Dummy bzw. echte BLEDvice testen.
        status.update_werte_nach_trainingsplan()
        status.modell.trainingsprogramm.verarbeite_messwerte(status.gestoppte_zeit.als_ms(),
                                                             status.modell.ergo.lese_distance())
        self.update_musik(status)
        self.update_ergometer(status)
        self.update_pulswerte(status)
        if not status.modell.uhr.macht_pause():
            # TODO Herz = Gesamtzahl der Schlaege,[ herz += len(ble_heartrate_data.rr_intervall)];
            status.modell.zonen.updateZone(pwm=status.berechne_pwm_wert() / 100, zeit=status.gestoppte_zeit,
                                           dist=status.modell.ergo.lese_distance(),
                                           herz=status.modell.pulsmesser.herzschlaege)
        neue_daten = daten_modell.update_daten_modell(status=status)
        return status, neue_daten

    def zeichne_view_und_log(self, status: ControllerStatus, daten_modell: ViewDatenmodell) -> None:
        if status.es_ist_zeit_fuer_update():
            log_string = f"{daten_modell.erzeuge_log_string()}"
            print(log_string)
            if self.log_file is not None:
                with open(self.log_file, "a") as f:
                    f.write(f"{log_string}\n")

        # Zeichne/Schreibe View
        for v in self.views:            # Falls mehrere Views benutzt werden
            v.daten = daten_modell
            v.draw_daten()
            # TODO Folgende Textzeilen funktionieren nicht
            if hasattr(v, 'browser_key'):
                if v.browser_key is not None:
                    status.gedrueckte_taste = v.browser_key
                    v.browser_key = None
                    funktion, argumente = cmd.command_mapper(status)
                    print(f"Fehler: {funktion} {argumente}")
                    if isinstance(result := funktion(**argumente), self.modell.ergo.__class__):
                        status.modell.ergo = result
        pygame.event.pump()

    def programm_loop(self, fps: int = 50):
        # TODO Angeblich werden Spiele nach folgender LOGISCHEN REIHENFOLGE abgearbeitet:
        #   1. Eingabe verarbeiten: Hier werden Tastendrücke, Mausbewegungen usw. abgefragt.
        #   2. Spiellogik updaten: Positionen von Objekten werden aktualisiert, Kollisionen überprüft usw.
        #   3. Bildschirm zeichnen: Die aktuelle Spielszene wird auf dem Bildschirm dargestellt.
        #   4. Framerate begrenzen: Hier kommt clock.tick() ins Spiel. Es sorgt dafür, dass nicht mehr als die
        #           gewünschte Anzahl an Frames pro Sekunde berechnet wird.
        #   1. process: Zeit, Devices(Arduino), Tastatur.
        #   2. update: Zielwerte, Ergometer, Zonen, Daten.
        #   3. Zeichne/Schreibe Log, View
        #   4. Setze Timer, Framerate

        # *******
        # Eingabe Arduino, Pygame-Zeit und Tastur(= "")
        self.modell.board.sendeUndLeseWerte(0)
        clock = pygame.time.Clock()
        status = ControllerStatus(modell=self.modell)
        daten_modell = ViewDatenmodell()

        # *******
        # Aktualisiere Trainingsplanwerte, Ergometerklasse
        status.update_werte_nach_trainingsplan()
        self.update_ergometer(status)

        while not status.programm_beenden():
            # ********
            # Eingabe Zeit, Devices, Tastatur
            status.update_zeit()
            self.modell.board.sendeUndLeseWerte(            # Wenn pause sende 0 an Arduino, damit summen aufhoert
                status.berechne_pwm_wert() if not status.modell.uhr.macht_pause() else 0)     # ErgometerDevice

            # TODO Implementiere Eingabe Herzfrequenz
            status = self.process_tastatureingabe(status)

            # ********
            # Aktualisiere die Trainingsplanwerte, Ergometerklasse, Zonenklasse und Daten
            status, daten_modell = self.update_daten(status, daten_modell)

            # ********
            # Zeichne/Schreibe Logdatei
            self.zeichne_view_und_log(status, daten_modell)

            if status.trainingsende_pause_machen():
                status.gedrueckte_taste = "PAUSE"
                funct, args = cmd.command_mapper(status)
                funct(**args)
                status.modell.trainingsprogramm.unendlich = True

            if status.pause_am_ende_des_aktuellen_inhalts():
                status.gedrueckte_taste = "PAUSE"
                funct, args = cmd.command_mapper(status)
                funct(**args)
                status.pause_nach_aktuellem_inhalt = False

            # ********
            # Setze MEINEN 1-Sekunden-Timer
            if status.es_ist_zeit_fuer_update():
                status.berechne_neue_updatezeit()
            # Setze Framerate
            clock.tick(fps)

        cmd.beende_programm(status=status)
        pygame.quit()
