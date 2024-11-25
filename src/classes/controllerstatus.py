from __future__ import annotations
from src.classes.applikationmodel import ApplikationModell
from src.classes.stoppuhr import FlexibleZeit
import src.modules.audiomodul as audiomodul


class ControllerStatus:
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

    def update_zeit(self) -> ControllerStatus:
        self.gestoppte_zeit = self.modell.akuelle_zeit()
        return self

    def es_ist_zeit_fuer_update(self) -> bool:
        # !!! Bei (not gestoppte_zeit > self.zeit_fuer_naechstes_update) manchmal 2 Zeiten pro sek im Timer
        # Z.B. 9 8 8 6 5 4 4 2  TODO Den Kommentar irgendwann loeschen
        return self.gestoppte_zeit > self.zeit_fuer_naechstes_update

    def berechne_neue_updatezeit(self) -> ControllerStatus:
        self.zeit_fuer_naechstes_update = self.zeit_fuer_naechstes_update + self.schleifen_zeit
        return self

    def update_werte_nach_trainingsplan(self) -> ControllerStatus:
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