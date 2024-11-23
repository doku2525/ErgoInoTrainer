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
from src.classes.viewdatenmodell import ViewDatenModell
from src.classes.bledevice import PulswerteDatenObjekt, BLEHeartRateData
import src.classes.viewdatenmodell as viewdatenmodell
from src.modules import audiomodul


class ApplikationController:

    def __init__(self, model: ApplikationModell | None = None, views: list[ApplikationView] | None = None,
                 log_file: str = None):
        self.modell: ApplikationModell = model
        self.views: list[ApplikationView] = views
        self.daten: DatenProcessor = DatenProcessor()
        self.log_file: str = log_file

    @staticmethod
    def key_mapper(key: int, modifier: int = 0) -> str:
        key_bindings_ohne_modifier = {
            pygame.K_LEFT: "PWM-",
            pygame.K_KP4: "PWM-",                       # Keypadtasten
            pygame.K_RIGHT: "PWM+",
            pygame.K_KP6: "PWM+",
            pygame.K_UP: "PWM++",
            pygame.K_KP8: "PWM++",
            pygame.K_DOWN: "PWM--",
            pygame.K_KP2: "PWM--",
            pygame.K_q: "QUIT",
            pygame.K_p: "PAUSE",
            pygame.K_SPACE: "PAUSE",
            pygame.K_KP_ENTER: "PAUSE",                 # Entertaste auf Keypad
            pygame.K_m: "MUSIK_MUTE",
            pygame.K_KP_PERIOD: "MUSIK_MUTE",           # DEL/.-Taste Nummernblock
            pygame.K_KP_MULTIPLY: "MUSIK_LAUTER",       # *-Taste Nummernblock
            pygame.K_KP_DIVIDE: "MUSIK_LEISER",         # /-Taste Nummernblock
            pygame.K_e: "PAUSE_NACH_INHALT"
        }
        key_bindings_mit_shift_modifier = {                      # Mit gedrueckter SHIFT-Taste
            pygame.K_e: "CHANGE_TRANINGSPROGRAMM_UNENDLICH"
        }
        match modifier:                     # NumLock => KMOD_NUM = 4096
            case pygame.KMOD_SHIFT | pygame.KMOD_LSHIFT | pygame.KMOD_RSHIFT:
                return key_bindings_mit_shift_modifier.get(key, "")
            case 0: return key_bindings_ohne_modifier.get(key, "")      # Ohne Modifier
            case _: ""                                                  # Noch nicht implementierte Modifier

    def command_mapper(self, status: ControllerStatus) -> Callable:
        def pause_mit_zeit():
            if self.modell.uhr.macht_pause():
                self.modell.uhr = self.modell.uhr.start(self.modell.millis_jetzt())
            else:
                self.modell.uhr = self.modell.uhr.pause(self.modell.millis_jetzt())

        def pause_nach_inhalt() -> None:
            status.pause_nach_aktuellem_inhalt = not status.pause_nach_aktuellem_inhalt

        def change_unendlich_status_in_trainingsprogramm() -> None:
            print(f"Status veraendert: {status.modell.trainingsprogramm.unendlich}")
            status.modell.trainingsprogramm.unendlich = not status.modell.trainingsprogramm.unendlich

        # Das Komando besteht aus einem tupel[Callable, dict[args]]
        command_map = {
            "QUIT": (self.beende_programm, {}),
            "PWM++": (self.modell.ergo.bremsePlusPlus, {'name': status.werte_nach_trainngsplan[0]}),
            "PWM+": (self.modell.ergo.bremsePlus, {'name': status.werte_nach_trainngsplan[0]}),
            "PWM--": (self.modell.ergo.bremseMinusMinus, {'name': status.werte_nach_trainngsplan[0]}),
            "PWM-": (self.modell.ergo.bremseMinus, {'name': status.werte_nach_trainngsplan[0]}),
            "PAUSE": (pause_mit_zeit, {}),
            "MUSIK_MUTE": (audiomodul.mute, {}),
            "MUSIK_LAUTER": (audiomodul.lauter, {}),
            "MUSIK_LEISER": (audiomodul.leiser, {}),
            "PAUSE_NACH_INHALT": (pause_nach_inhalt, {}),
            "CHANGE_TRANINGSPROGRAMM_UNENDLICH": (change_unendlich_status_in_trainingsprogramm, {})
        }
        return command_map.get(status.gedrueckte_taste, lambda: None)

    def beende_programm(self) -> None:
        # TODO Zum Debuggen. Spaeter entfernen.
        # with open('daten/log/viewelemente.log', 'w') as datei:
        #     for elem in self.views[0].debug_werte.items():
        #         datei.write(jsonpickle.encode(elem) + "\n")
        self.modell.board.sendeUndLeseWerte(0)  # Bremse auf 0 um das PWM-Summen an der Bremse zu stoppen

    def process_tastatureingabe(self, status: ControllerStatus = None) -> ControllerStatus:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.beende_programm()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                print(f"Taste: {event.key} {event.mod}")  # TODO Zum Ermitteln eines Taste-CODES die Zeile auskommentieren
                status.gedrueckte_taste = ApplikationController.key_mapper(event.key, event.mod)
                if status.gedrueckte_taste:
                    # Fuehre den zur gedrueckten Taste passenden Befehl aus.
                    funktion, argumente = self.command_mapper(status)
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
                     daten_modell: ViewDatenModell) -> tuple[ControllerStatus, ViewDatenModell]:
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
        neue_daten = viewdatenmodell.update_daten_modell(daten_modell=daten_modell, status=status)
        return status, neue_daten

    def zeichne_view_und_log(self, status: ControllerStatus, daten_modell: ViewDatenModell) -> None:
        if status.es_ist_zeit_fuer_update():
            log_string = f"{viewdatenmodell.erzeuge_log_string(daten_modell)}"
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
                    funktion, argumente = self.command_mapper(status)
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
        daten_modell = ViewDatenModell()

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
                funct, args = self.command_mapper(status)
                funct(**args)
                status.modell.trainingsprogramm.unendlich = True

            if status.pause_am_ende_des_aktuellen_inahlts():
                status.gedrueckte_taste = "PAUSE"
                funct, args = self.command_mapper(status)
                funct(**args)
                status.pause_nach_aktuellem_inhalt = False

            # ********
            # Setze MEINEN 1-Sekunden-Timer
            if status.es_ist_zeit_fuer_update():
                status.berechne_neue_updatezeit()
            # Setze Framerate
            clock.tick(fps)

        self.beende_programm()
        pygame.quit()
