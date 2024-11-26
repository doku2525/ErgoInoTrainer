from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field, replace
import datetime
if TYPE_CHECKING:
    from src.classes.controllerstatus import ControllerStatus


farbe_rot = (255, 0, 0)
farbe_gruen = (0, 255, 0)


@dataclass(frozen=True)
class ViewDatenmodell:
    trainings_name: str = field(default_factory=str)
    trainings_inhalt: str = field(default_factory=str)
    trainings_gesamtzeit: str = field(default_factory=str)
    zeit_gesamt: str = field(default_factory=str)
    zeit_timer: int = field(default_factory=int)
    zeit_timer_string: str = field(default_factory=str)
    sets_rest: int = field(default_factory=int)
    herz_frequenz: int = field(default_factory=int)
    herz_durchschnitt: int = field(default_factory=int)
    herz_gesamt: int = field(default_factory=int)
    herz_batterielevel: int = field(default_factory=int)
    pwm_wert: float = field(default_factory=float)
    cad_frequenz: int = field(default_factory=int)
    cad_durchschnitt: float = field(default_factory=float)
    cad_aktuell: int = field(default_factory=int)
    cad_differenz: int = field(default_factory=int)
    cad_count: int = field(default_factory=int)
    cad_fuer_ziel: int = field(default_factory=int)
    power_aktuell: float = field(default_factory=float)
    power_durchschnitt: float = field(default_factory=float)
    power_gesamt: int = field(default_factory=int)
    power_watt: int = field(default_factory=int)
    werte_und_power: dict = field(default_factory=dict)
    distanze: int = field(default_factory=int)
    distanze_device: int = field(default_factory=int)
    distanze_am_ziel: int = field(default_factory=int)
    intervall_cad: int = field(default_factory=int)
    intervall_herz: int = field(default_factory=int)
    intervall_distanze: int = field(default_factory=int)
    intervall_zeit: int = field(default_factory=int)
    intervall_puls: int = field(default_factory=int)
    anzahl_sets: int = field(default_factory=int)
    anzahl_fertige_sets: int = field(default_factory=int)
    reps: int = field(default_factory=int)
    # zonen_tabelle: dict = field(default_factory=dict)   # TODO Scheint ueberfluessig zu sein
    intervall_tabelle: list[list[int, int, int, int, (int, int, int)]] = field(default_factory=list)
    device_werte: str = field(default_factory=str)
    intervall_farbe: tuple[int, int, int] = field(default_factory=tuple)

    def berechne_ergometer_daten(self, status: ControllerStatus = None) -> ViewDatenmodell:
        return replace(self, **{
            'cad_frequenz': status.modell.ergo.lese_cadence(),
            'cad_durchschnitt': status.modell.ergo.calc_cad_durchschnitt(status.modell.akuelle_zeit().als_ms(), 1),
            'cad_aktuell': status.werte_nach_trainngsplan[2],
            'cad_differenz': status.modell.ergo.lese_cadence() - status.werte_nach_trainngsplan[2],
            'pwm_wert': status.berechne_pwm_wert() / 100.0,
            'distanze': status.modell.ergo.lese_distance(),
            'distanze_am_ziel': status.modell.ergo.calc_distanze_am_ende(status.gestoppte_zeit.als_ms(),
                                                                         status.modell.trainingsprogramm.
                                                                         trainingszeit_dauer_gesamt()),
            # TODO calc_power_index so schreiben, dass Ergometer gleich die richtigen Werte bekommt ohne Argument
            'power_aktuell': status.modell.ergo.calc_power_index(status.berechne_pwm_wert(), 2),
            'power_gesamt': status.modell.zonen.calcPowerGesamt(),
            'power_durchschnitt': status.modell.zonen.calcPowerDurchschnitt(),
            # TODO calc_power_watt so schreiben, dass Ergometer gleich die richtigen Werte bekommt ohne Argument
            'power_watt': status.modell.ergo.calc_power_watt(status.berechne_pwm_wert()),
        })

    def berechne_intervall_daten(self, status: ControllerStatus = None) -> ViewDatenmodell:
        return replace(self, **{
            'intervall_distanze': status.modell.trainingsprogramm.berechne_distanze_aktueller_inhalt(),
            'intervall_cad': round(status.modell.trainingsprogramm.berechne_distanze_aktueller_inhalt() * 60 /
                                   (status.modell.trainingsprogramm.trainingszeit_dauer_aktueller_inhalt(
                                       status.gestoppte_zeit.als_ms() + 1) / 1000)),
            'intervall_tabelle': [[dist, int(dist * 60 // (zeit / 1000)), 0, 0, farbe]
                                  for dist, zeit, farbe in
                                  zip(status.modell.trainingsprogramm.berechne_distanze_pro_fertige_inhalte(),
                                      [elem.dauer() for elem in status.modell.trainingsprogramm.inhalte],
                                      [farbe_rot if elem.name == 'Intervall' else
                                       farbe_gruen
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
            'intervall_farbe': farbe_rot if status.modell.trainingsprogramm.fuehre_aus(
                status.gestoppte_zeit.als_ms()).name == 'Intervall' else farbe_gruen})

    def berechne_puls_daten(self, status: ControllerStatus = None) -> ViewDatenmodell:
        return replace(self, **{
            'herz_frequenz': status.modell.pulsmesser.herzfrequenz,
            'herz_gesamt': status.modell.pulsmesser.herzschlaege,
            'herz_durchschnitt': status.modell.pulsmesser.calc_puls_durchschnitt(status.modell.akuelle_zeit().als_ms()),
            'herz_batterielevel': status.modell.puls_device.batterie_level})

    def update_daten_modell(self, status: ControllerStatus = None) -> ViewDatenmodell:
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
        result = (self.
                  berechne_ergometer_daten(status=status).
                  berechne_intervall_daten(status=status).
                  berechne_puls_daten(status=status))
        return replace(result, **{
            'zeit_gesamt': str(datetime.timedelta(seconds=int(status.gestoppte_zeit.als_s()))),
            'zeit_timer': abs(berechneter_zeit_timer),
            'zeit_timer_string': (str(
                datetime.timedelta(seconds=abs(berechneter_zeit_timer))) +
                ('\u2297' if status.pause_nach_aktuellem_inhalt else '')),
            'werte_und_power': status.modell.zonen.mergeWerteAndPower(),
            'device_werte': str(status.modell.board.device_daten.__dict__),
            'trainings_name': status.modell.trainingsprogramm.name,
            'trainings_inhalt': status.modell.trainingsprogramm.fuehre_aus(status.gestoppte_zeit.als_ms()).name,
            'trainings_gesamtzeit': (str(
                datetime.timedelta(milliseconds=status.modell.trainingsprogramm.trainingszeit_dauer_gesamt())) +
                (' ∞' if status.modell.trainingsprogramm.unendlich else ' \u2297'))})

    def erzeuge_log_string(self, join_string: str = "\t") -> str:
        now = datetime.datetime.now()
        result = [
            "{0}".format(self.trainings_name),
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S.%f")[:-3],
            "{0}".format(self.zeit_gesamt),
            "{0}".format(self.trainings_inhalt),
            "{0}".format(self.zeit_timer),
            "{0}".format(self.cad_frequenz),
            "{0}".format(self.cad_aktuell),
            "{0}".format(self.distanze_device),
            "{0}".format(self.cad_durchschnitt),
            "{0}".format(self.distanze),
            "{0}".format(self.intervall_distanze),
            "{0}".format(self.intervall_cad),
            "{0}".format("herz_schlaege"),
            "{0}".format("calcPulsDurchschnitt"),
            "{0}".format("calcHerzschlaegeIntervall"),
            "{0}".format("calcPulsIntervall"),
            "{0}".format(self.pwm_wert),
            "{0}".format("herz_freq"),
            "{0}".format("batterie_level"),
            "{0}".format(self.device_werte),
            # TODO
            # {'zeit': 1722690179.975749, 'herzfrequenz': 122, 'rr': [498, 502], 'rr_interval': True}
            "{0}".format("herzwert")
            ]
        return join_string.join(result)
