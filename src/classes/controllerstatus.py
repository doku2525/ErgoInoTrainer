from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
from src.classes.bledevice import PulswerteDatenObjekt, BLEHeartRateData
from src.classes.stoppuhr import FlexibleZeit
import src.modules.audiomodul as audiomodul
if TYPE_CHECKING:
    from src.classes.applikationmodel import ApplikationModell

from src.classes.trainingsinhalt import BelastungTypen

"""In einigen Funktionen [pause_am_ende_des_aktuellen_inhalts(), neuer_wert_pause_nach_aktuellem_inhalt()]
wird ein Zeitwert in Millisekunden benutzt, innerhalb dem eine Schleife mindestens einmal durchgelaufen sein sollte.
Falls es zu Timingproblemen bei aelteren Computern kommen sollte, kann ein goressere Wert fuer ZEIT_DELTA benutzt
werden. Eine Schleife sind 1000ms, deshalb sollte der Wert nicht groesser als 500ms sein.
Falls 500 nicht ausreicht, sollten einige Funktionen in der Schleife deaktiviert werden."""
ZEIT_DELTA = 100


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

    def stoppe_zeit(self) -> ControllerStatus:
        self.gestoppte_zeit = self.modell.akuelle_zeit()
        return self

    def pruefe_logging_status(self) -> bool:
        return self.modell.trainingsprogramm.fuehre_aus(self.gestoppte_zeit.als_ms()).logging

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
        # TODO der < - Vergleich sollte irgendwann evtl. durch die Zeitfunktion aus trainingsprogramm ersetzt werden
        # trainingszeit_dauer_gesamt(filter) < laufzeit_trainings_programm(self.gestoppte_zeit.als_ms())
        mein_filter = lambda x: x.typ != BelastungTypen.COUNTDOWN
        return (self.es_ist_zeit_fuer_update() and
                self.modell.trainingsprogramm.trainingszeit_dauer_gesamt() < self.gestoppte_zeit.als_ms() and
                not self.modell.trainingsprogramm.unendlich)

    def pause_am_ende_des_aktuellen_inhalts(self) -> bool:
        """Die Funktion prueft, ob in den Pausenmodus gewechselt werden soll.
            True bedeutet, der Inhalt ist beendet und es wird das Kommando Pause geschickt.
            !!! Die Funktion ist kein Test, ob am Ende des Inhalts in den Pausenmodus gewechselt wird."""
        self.pause_nach_aktuellem_inhalt = self.neuer_wert_pause_nach_aktuellem_inhalt()
        return (self.es_ist_zeit_fuer_update() and
                self.pause_nach_aktuellem_inhalt and
                self.modell.trainingsprogramm.trainingszeit_dauer_aktueller_inhalt_ohne_filter(
                    self.gestoppte_zeit.als_ms()) < ZEIT_DELTA)

    def neuer_wert_pause_nach_aktuellem_inhalt(self) -> bool:
        """Liefer den neuen Wert fuer das Attribut.
            ZEIT_DELTA steht in Verbindung mit der Funktion pause_am_ende_des_aktuellen_inhalts(), weil sonst das
            Programm in den Pausenmodus springt, wenn das Attribut innerhalb ZEIT_DELTA veraendert wird"""
        return (self.pause_nach_aktuellem_inhalt |
                (not self.modell.trainingsprogramm.unendlich and
                 self.modell.trainingsprogramm.ist_letzter_inhalt(self.gestoppte_zeit.als_ms()) and
                 self.modell.trainingsprogramm.trainingszeit_dauer_aktueller_inhalt_ohne_filter(
                     self.gestoppte_zeit.als_ms()) > ZEIT_DELTA))

    def update_ergometer(self) -> None:
        self.modell.ergo = (self.modell.ergo.
                            setBremse(self.werte_nach_trainngsplan[1]).
                            update_device_werte(self.modell.board.device_daten, pause=self.modell.uhr.macht_pause()))

    def update_musik(self) -> None:
        # TODO Evtl. Musik mit Pausenfunktion syncronisieren
        # TODO Zeige in GUI an, ob Playlist verfuegbar ist
        result = audiomodul.play_audio_schedule(playlist=self.audio_playlist,
                                                aktuelle_zeit_in_ms=self.gestoppte_zeit.als_ms(),
                                                busy_status=pygame.mixer.music.get_busy())
        audiomodul.AUDIOOBJEKT_AKTIVE, self.audio_playlist, (audiofunc, args) = result
        # Wenn Trainingszeit abgelaufen ist, lasse das letzte Lied auslaufen.
        # TODO Siehe Kommentar in trainingsende_pause_machen()
        if self.gestoppte_zeit.als_ms() >= self.modell.trainingsprogramm.trainingszeit_dauer_gesamt():
            return None
        audiofunc(**args)
        if audiofunc == audiomodul.fadeout_musik:   # FLAG um doppeltes fadeout zu verhindern
            audiomodul.AUDIO_VOLUME_FADINGOUT = True
        elif args:
            audiomodul.AUDIO_VOLUME_FADINGOUT = False

    def update_pulswerte(self) -> None:
        if self.modell.puls_device.connected:
            self.modell.pulsmesser = self.modell.pulsmesser.verarbeite_device_werte(
                self.modell.puls_device.lese_messwerte())
        else:
            if self.es_ist_zeit_fuer_update():
                self.modell.pulsmesser = self.modell.pulsmesser.verarbeite_device_werte(
                    PulswerteDatenObjekt(zeitstempel=0, ble_objekt=BLEHeartRateData(16, 0, [])).ble_objekt)

    def update_daten(self, daten_modell: ViewDatenmodell) -> tuple[ControllerStatus, ViewDatenmodell]:
        # TODO Unterteile in Updates, die waherend der Pause nicht durchgefuehrt werden muessen und staendigen
        # TODO Herzwerte durch Dummy bzw. echte BLEDvice testen.
        self.update_werte_nach_trainingsplan()
        self.modell.trainingsprogramm = (self.modell.trainingsprogramm.
                                         verarbeite_messwerte(self.gestoppte_zeit.als_ms(),
                                                              self.modell.ergo.lese_distance()))
        self.update_musik()
        self.update_ergometer()
        self.update_pulswerte()
        if not self.modell.uhr.macht_pause():
            # TODO Herz = Gesamtzahl der Schlaege,[ herz += len(ble_heartrate_data.rr_intervall)];
            self.modell.zonen = self.modell.zonen.updateZone(pwm=self.berechne_pwm_wert() / 100,
                                                             zeit=self.gestoppte_zeit,
                                                             dist=self.modell.ergo.lese_distance(),
                                                             herz=self.modell.pulsmesser.herzschlaege)

        neue_daten = daten_modell.update_daten_modell(status=self)
        return self, neue_daten

    def update_status(self) -> None:
        self.update_ergometer()
        self.update_musik()
        self.update_pulswerte()
