from __future__ import annotations
from typing import Callable
import sys
import pygame
import datetime
import jsonpickle

from src.classes.applikationmodel import ApplikationModell
from src.classes.applikationview import ApplikationView
from src.classes.datenprozessor import DatenProcessor
from src.classes.stoppuhr import FlexibleZeit
from src.classes.viewdatenmodell import ViewDatenModell
import src.classes.viewdatenmodell as viewdatenmodell
from src.modules import audiomodul


def update_daten_modell(daten_modell: ViewDatenModell = ViewDatenModell(), status: Status = None) -> ViewDatenModell:
    def berechne_zeit_timer() -> int:
        # Gibt die Zeit in Sekunden zurueck
        berechnete_zeit = int(status.modell.trainingsprogramm.fuehre_aus(status.gestoppte_zeit.als_ms()).dauer() -
                              status.modell.trainingsprogramm.
                              trainingszeit_dauer_aktueller_inhalt(status.gestoppte_zeit.als_ms()))
        if berechnete_zeit == status.modell.trainingsprogramm.fuehre_aus(status.gestoppte_zeit.als_ms()).dauer():
            return int(berechnete_zeit / 1000)
        if berechnete_zeit < 0:     # Verhindert, dass am Ende des Trainings 2, 1, 1, 0, -1 gezaehlt wird
            return int(berechnete_zeit / 1000)
        return int(berechnete_zeit / 1000) + 1

    if status is None:
        return daten_modell

    berechneter_zeit_timer = berechne_zeit_timer()
    return daten_modell._replace(**{
        'zeit_gesamt': str(datetime.timedelta(seconds=int(status.gestoppte_zeit.als_s()))),
        'zeit_timer': abs(berechneter_zeit_timer),
        'zeit_timer_string': (str(
            datetime.timedelta(seconds=abs(berechneter_zeit_timer))) +
            ('\u2297' if status.pause_nach_aktuellem_inhalt else '')),
        'cad_frequenz': status.modell.ergo.lese_cadence(),
        'cad_durchschnitt': status.modell.ergo.calc_cad_durchschnitt(status.modell.akuelle_zeit().als_ms(), 1),
        'cad_aktuell': status.werte_nach_trainngsplan[2],
        'cad_differenz': status.modell.ergo.lese_cadence() - status.werte_nach_trainngsplan[2],
        'pwm_wert': status.berechne_pwm_wert() / 100.0,
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
        'trainings_gesamtzeit': (str(
            datetime.timedelta(milliseconds=status.modell.trainingsprogramm.trainingszeit_dauer_gesamt())) +
            (' ∞' if status.modell.trainingsprogramm.unendlich else ' \u2297')),
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
    def __init__(self, modell: ApplikationModell, schleifen_zeit_in_ms: int = 1000,
                 pause_nach_aktuellem_inhalt: bool = False):
        self.gedrueckte_taste = ''
        self.modell: ApplikationModell = modell
        self.gestoppte_zeit: FlexibleZeit = self.modell.akuelle_zeit()
        self.schleifen_zeit: FlexibleZeit = FlexibleZeit.create_from_millis(schleifen_zeit_in_ms)
        self.zeit_fuer_naechstes_update: FlexibleZeit = self.gestoppte_zeit + self.schleifen_zeit
        self.werte_nach_trainngsplan = None
        self.audio_playlist = audiomodul.build_playlist(trainingsplan=modell.trainingsprogramm,
                                                        audio_objekte=audiomodul.MEINE_AUDIO_OBJEKTE)
        self.pause_nach_aktuellem_inhalt = pause_nach_aktuellem_inhalt

    def programm_beenden(self) -> bool:
        return self.gedrueckte_taste == 'QUIT'

    def update_zeit(self) -> Status:
        self.gestoppte_zeit = self.modell.akuelle_zeit()
        return self

    def es_ist_zeit_fuer_update(self) -> bool:
        # !!! Bei (not gestoppte_zeit > self.zeit_fuer_naechstes_update) manchmal 2 Zeiten pro sek im Timer
        # Z.B. 9 8 8 6 5 4 4 2  TODO Den Kommentar irgendwann loeschen
        return self.gestoppte_zeit > self.zeit_fuer_naechstes_update

    def berechne_neue_updatezeit(self) -> Status:
        self.zeit_fuer_naechstes_update = self.zeit_fuer_naechstes_update + self.schleifen_zeit
        return self

    def update_werte_nach_trainingsplan(self) -> Status:
        self.werte_nach_trainngsplan = (self.modell.trainingsprogramm.
                                        fuehre_aus(self.gestoppte_zeit.als_ms()).
                                        berechne_werte(self.gestoppte_zeit.als_ms()))
        return self

    def berechne_pwm_wert(self) -> int:
        return self.modell.ergo.berechne_korigierten_bremswert(ausgangs_wert=self.werte_nach_trainngsplan[1],
                                                               name=self.werte_nach_trainngsplan[0])

    def trainingsende_pause_machen(self) -> bool:
        return (self.es_ist_zeit_fuer_update() and
                self.modell.trainingsprogramm.trainingszeit_dauer_gesamt() < self.gestoppte_zeit.als_ms() and
                not self.modell.trainingsprogramm.unendlich)

    def pause_am_ende_des_aktuellen_inahlts(self) -> bool:
        berechnete_zeit = (self.modell.trainingsprogramm.
                           trainingszeit_dauer_aktueller_inhalt(self.gestoppte_zeit.als_ms()))
        return (self.es_ist_zeit_fuer_update() and
                self.pause_nach_aktuellem_inhalt and
                self.modell.trainingsprogramm.trainingszeit_dauer_aktueller_inhalt(self.gestoppte_zeit.als_ms()) < 100)


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

    def command_mapper(self, status: Status) -> Callable:
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

    def process_tastatureingabe(self, status: Status = None) -> Status:
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

    def update_ergometer(self, status: Status) -> None:
        status.modell.ergo = (self.modell.ergo.
                              setBremse(status.werte_nach_trainngsplan[1]).
                              update_device_werte(self.modell.board.device_daten))

    @staticmethod
    def update_musik(status: Status) -> None:
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

    def update_daten(self, status: Status, daten_modell: ViewDatenModell) -> tuple[Status, ViewDatenModell]:
        # TODO Unterteile in Updates, die waherend der Pause nicht durchgefuehrt werden muessen und staendigen
        status.update_werte_nach_trainingsplan()
        status.modell.trainingsprogramm.verarbeite_messwerte(status.gestoppte_zeit.als_ms(),
                                                             status.modell.ergo.lese_distance())
        self.update_musik(status)
        self.update_ergometer(status)
        if not status.modell.uhr.macht_pause():
            status.modell.zonen.updateZone(pwm=status.berechne_pwm_wert() / 100, zeit=status.gestoppte_zeit,
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
