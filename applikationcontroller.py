from __future__ import annotations
import copy
from typing import Callable
import sys
import pygame
import datetime
import time

from applikationmodel import ApplikationModell
from applikationview import ApplikationView
from datenprozessor import DatenProcessor
from stoppuhr import FlexibleZeit, ZE
from viewdatenmodell import ViewDatenModell
import viewdatenmodell


def update_daten_modell(daten_modell: ViewDatenModell = ViewDatenModell(), status: Status = None) -> ViewDatenModell:
    def berechne_zeit_timer() -> int:
        # Gibt die Zeit in Sekunden zurueck
        berechnete_zeit = int(status.modell.trainingsprogramm.fuehre_aus(status.gestoppte_zeit.als_ms()).dauer() -
                              status.modell.trainingsprogramm.
                              trainingszeit_dauer_aktueller_inhalt(status.gestoppte_zeit.als_ms()))
        if berechnete_zeit == status.modell.trainingsprogramm.fuehre_aus(status.gestoppte_zeit.als_ms()).dauer():
            return int(berechnete_zeit / 1000)
        else:
            return int(berechnete_zeit / 1000) + 1

    if status is None:
        return daten_modell

    berechneter_zeit_timer = berechne_zeit_timer()
    return daten_modell._replace(**{
        'zeit_gesamt': str(datetime.timedelta(seconds=int(status.gestoppte_zeit.als_s()))),
        'zeit_timer': abs(berechneter_zeit_timer),
        'zeit_timer_string': str(datetime.timedelta(seconds=abs(berechneter_zeit_timer))),
        'cad_frequenz': status.modell.ergo.lese_cadence(),
        'cad_durchschnitt': status.modell.ergo.calc_cad_durchschnitt(status.modell.akuelle_zeit().als_ms(), 1),
        'cad_aktuell': status.werte_nach_trainngsplan[2],
        'cad_differenz': status.modell.ergo.lese_cadence() - status.werte_nach_trainngsplan[2],
        'pwm_wert': status.werte_nach_trainngsplan[1] / 100.0,
        'distanze': status.modell.ergo.lese_distance(),
        'distanze_am_ziel': status.modell.ergo.calc_distanze_am_ende(status.gestoppte_zeit.als_ms(),
                                                                     status.modell.trainingsprogramm.
                                                                     trainingszeit_dauer_gesamt()),
        'power_aktuell': status.modell.ergo.calc_power_index(2),
        'power_gesamt': status.modell.zonen.calcPowerGesamt(),
        'power_durchschnitt': status.modell.zonen.calcPowerDurchschnitt(),
        'power_watt': status.modell.ergo.calc_power_watt(),
        'werte_und_power': status.modell.zonen.mergeWerteAndPower(),
        'device_werte': str(status.modell.board.device_daten.__dict__),
        'trainings_name': status.modell.trainingsprogramm.name,
        'trainings_inhalt': status.modell.trainingsprogramm.fuehre_aus(status.gestoppte_zeit.als_ms()).name,
        'intervall_distanze': status.modell.trainingsprogramm.berechne_distanze_aktueller_inhalt(),
        'intervall_cad': round(status.modell.trainingsprogramm.berechne_distanze_aktueller_inhalt() * 60 /
                               (status.modell.trainingsprogramm.trainingszeit_dauer_aktueller_inhalt(
                                   status.gestoppte_zeit.als_ms() + 1) / 1000)),
        'intervall_tabelle': [[dist, int(dist * 60 // (zeit / 1000)), 0, 0, farbe]
                              for dist, zeit, farbe in
                              zip(status.modell.trainingsprogramm.berechne_distanze_pro_fertige_inhalte(),
                                  [elem.dauer() for elem in status.modell.trainingsprogramm.inhalte],
                                  [ApplikationView.farbe_rot if elem.name == 'Intervall' else
                                   ApplikationView.farbe_gruen
                                   for elem in status.modell.trainingsprogramm.inhalte])
                              ],
        'anzahl_sets':
            len(list(filter(lambda elem: elem.name == 'Intervall', status.modell.trainingsprogramm.inhalte))),
        'anzahl_fertige_sets':
            len(list(filter(lambda elem: elem.name == 'Intervall', status.modell.trainingsprogramm.inhalte))) -
            len(list(filter(lambda elem: elem.name == 'Intervall',
                            [elem
                             for _, elem
                             in zip(status.modell.trainingsprogramm.berechne_distanze_pro_fertige_inhalte(),
                                    status.modell.trainingsprogramm.inhalte)]))),
        'intervall_farbe': ApplikationView.farbe_rot if status.modell.trainingsprogramm.fuehre_aus(
            status.gestoppte_zeit.als_ms()).name == 'Intervall' else ApplikationView.farbe_gruen})


class Status:
    def __init__(self, modell: ApplikationModell, schleifen_zeit_in_ms: int = 1000):
        self.gedrueckte_taste = ''
        self.modell: ApplikationModell = modell
        self.gestoppte_zeit: FlexibleZeit = self.modell.akuelle_zeit()
        self.schleifen_zeit: FlexibleZeit = FlexibleZeit.create_from_millis(schleifen_zeit_in_ms)
        self.zeit_fuer_naechstes_update: FlexibleZeit = self.gestoppte_zeit + self.schleifen_zeit
        self.werte_nach_trainngsplan = None

    def programm_beenden(self) -> bool:
        return self.gedrueckte_taste == 'QUIT'

    def update_zeit(self) -> Status:
        self.gestoppte_zeit = self.modell.akuelle_zeit()
        return self

    def es_ist_zeit_fuer_update(self) -> bool:
        # !!! Bei (not gestoppte_zeit > self.zeit_fuer_naechstes_update) manchmal 2 Zeiten pro sek im Timer
        # Z.B. 9 8 8 6 5 4 4 2
        return self.gestoppte_zeit > self.zeit_fuer_naechstes_update

    def berechne_neue_updatezeit(self) -> Status:
        self.zeit_fuer_naechstes_update = self.zeit_fuer_naechstes_update + self.schleifen_zeit
        return self

    def update_werte_nach_trainingsplan(self) -> Status:
        self.werte_nach_trainngsplan = (self.modell.trainingsprogramm.
                                        fuehre_aus(self.gestoppte_zeit.als_ms()).
                                        berechne_werte(self.gestoppte_zeit.als_ms()))
        return self


class ApplikationController:

    def __init__(self, model: ApplikationModell | None = None, views: list[ApplikationView] | None = None,
                 log_file: str = None):
        self.modell: ApplikationModell = model
        self.views: list[ApplikationView] = views
        self.daten: DatenProcessor = DatenProcessor()
        self.log_file: str = log_file

    @staticmethod
    def key_mapper(key: int) -> str:
        key_bindings = {
            pygame.K_LEFT: "PWM-",
            pygame.K_RIGHT: "PWM+",
            pygame.K_UP: "PWM++",
            pygame.K_DOWN: "PWM--",
            pygame.K_q: "QUIT",
            pygame.K_p: "PAUSE",
        }
        return key_bindings.get(key, "")

    def command_mapper(self, command: str) -> Callable:
        def pause_mit_zeit():
            if self.modell.uhr.macht_pause():
                self.modell.uhr = self.modell.uhr.start(self.modell.millis_jetzt())
            else:
                self.modell.uhr = self.modell.uhr.pause(self.modell.millis_jetzt())

        # TODO Benutze folgendes System, um auch Argumente mit den Funktionen zu uebergeben
        #   Im Dict als Tuple speichern (self.modell.ergo.bremsePlusPlus, {'start_value': 50})
        #  Das Tupel dann wie folgt bearbeiten:
        #   funktion, argumente = command_map[command]
        #   funktion(**argumente)
        #     P.S. Das funktioniert auch fuer lambda-Funktionen
        command_map = {
            "QUIT": self.beende_programm,
            "PWM++": self.modell.ergo.bremsePlusPlus,
            "PWM+": self.modell.ergo.bremsePlus,
            "PWM--": self.modell.ergo.bremseMinusMinus,
            "PWM-": self.modell.ergo.bremseMinus,
            "PAUSE": pause_mit_zeit
        }
        return command_map.get(command, lambda: None)

    def beende_programm(self) -> None:
        self.modell.board.sendeUndLeseWerte(0)  # Bremse auf 0 um das PWM-Summen an der Bremse zu stoppen

    def process_tastatureingabe(self, status: Status = None) -> Status:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.beende_programm()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                status.gedrueckte_taste = ApplikationController.key_mapper(event.key)
                if status.gedrueckte_taste:
                    # Fuehrt Befehl aus.
                    self.command_mapper(status.gedrueckte_taste)()

        return status

    def update_ergometer(self, status: Status) -> None:
        self.modell.ergo.bremse = status.werte_nach_trainngsplan[1]
        self.modell.ergo.update_device_werte(self.modell.board.device_daten)

    def update_daten(self, status: Status, daten_modell: ViewDatenModell) -> tuple[Status, ViewDatenModell]:
        status.update_werte_nach_trainingsplan()
        status.modell.trainingsprogramm.verarbeite_messwerte(status.gestoppte_zeit.als_ms(),
                                                             status.modell.ergo.lese_distance())
        self.update_ergometer(status)
        status.modell.zonen.updateZone(pwm=status.modell.ergo.bremse / 100, zeit=status.gestoppte_zeit,
                                       dist=status.modell.ergo.lese_distance(), herz=0)
        neue_daten = update_daten_modell(daten_modell=daten_modell, status=status)
        return status, neue_daten

    def zeichne_view_und_log(self, status: Status, daten_modell: ViewDatenModell) -> None:
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
            if hasattr(v, 'browser_key'):
                print(f"Browserkey: {v.browser_key}")
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
        status = Status(modell=self.modell)
        daten_modell = ViewDatenModell()

        # *******
        # Aktualisiere Trainingsplanwerte, Ergometerklasse
        status.update_werte_nach_trainingsplan()
        self.update_ergometer(status)

        while not status.programm_beenden():
            # ********
            # Eingabe Zeit, Devices, Tastatur
            status.update_zeit()
            self.modell.board.sendeUndLeseWerte(status.werte_nach_trainngsplan[1])   # ErgometerDevice
            # TODO Implementiere Eingabe Herzfrequenz
            status = self.process_tastatureingabe(status)

            # ********
            # Aktualisiere die Trainingsplanwerte, Ergometerklasse, Zonenklasse und Daten
            status, daten_modell = self.update_daten(status, daten_modell)

            # ********
            # Zeichne/Schreibe Logdatei
            self.zeichne_view_und_log(status, daten_modell)

            # ********
            # Setze MEINEN 1-Sekunden-Timer
            if status.es_ist_zeit_fuer_update():
                status.berechne_neue_updatezeit()
            # Setze Framerate
            clock.tick(fps)

        self.beende_programm()
        pygame.quit()
