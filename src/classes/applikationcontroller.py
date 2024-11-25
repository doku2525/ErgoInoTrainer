from __future__ import annotations
from typing import Callable, TYPE_CHECKING
import sys
import pygame
import datetime

from src.classes.controllerstatus import ControllerStatus
from src.classes.viewdatenmodell import ViewDatenmodell
import src.classes.commandmapper as cmd
from src.classes.datenprozessor import DatenProcessor   # TODO Noch wurde DatenProcessor nicht implementiert!!!

if TYPE_CHECKING:
    from src.classes.applikationmodel import ApplikationModell
    from src.classes.applikationview import ApplikationView


class ApplikationController:

    def __init__(self, model: ApplikationModell | None = None, views: list[ApplikationView] | None = None,
                 log_file: str = None):
        self.modell: ApplikationModell = model
        self.views: list[ApplikationView] = views
        self.daten: DatenProcessor = DatenProcessor()       # TODO Noch wurde DatenProcessor nicht implementiert!!!
        self.log_file: str = log_file

    def process_tastatureingabe(self, status: ControllerStatus = None) -> ControllerStatus:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cmd.beende_programm(status=status)
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # print(f"Taste: {event.key} {event.mod}")  # TODO Zum Ermitteln einer Taste die Zeile auskommentieren
                status.gedrueckte_taste = cmd.key_mapper(event.key, event.mod)
                if status.gedrueckte_taste:
                    # Fuehre den zur gedrueckten Taste passenden Befehl aus.
                    funktion, argumente = cmd.command_mapper(status)
                    if isinstance(result := funktion(**argumente), self.modell.ergo.__class__):
                        status.modell.ergo = result
        return status

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
        status.update_ergometer()

        while not status.programm_beenden():
            # ********
            # Eingabe Zeit, Devices, Tastatur
            status.stoppe_zeit()
            self.modell.board.sendeUndLeseWerte(            # Wenn pause sende 0 an Arduino, damit summen aufhoert
                status.berechne_pwm_wert() if not status.modell.uhr.macht_pause() else 0)     # ErgometerDevice

            # TODO Implementiere Eingabe Herzfrequenz
            status = self.process_tastatureingabe(status)

            # ********
            # Aktualisiere die Trainingsplanwerte, Ergometerklasse, Zonenklasse und Daten
            status, daten_modell = status.update_daten(daten_modell)

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
