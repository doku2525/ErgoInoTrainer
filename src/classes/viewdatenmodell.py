from collections import namedtuple
import datetime
from src.classes.controllerstatus import ControllerStatus


daten_field_names = ['trainings_name',
                     'trainings_inhalt',
                     'trainings_gesamtzeit',
                     'zeit_gesamt',
                     'zeit_timer',
                     'zeit_timer_string',
                     'sets_rest',
                     'herz_frequenz',
                     'herz_durchschnitt',
                     'herz_gesamt',
                     'herz_batterielevel',
                     'pwm_wert',
                     'cad_frequenz',
                     'cad_durchschnitt',
                     'cad_aktuell',
                     'cad_differenz',
                     'cad_count',
                     'cad_fuer_ziel',
                     'power_aktuell',
                     'power_durchschnitt',
                     'power_gesamt',
                     'power_watt',
                     'werte_und_power',
                     'distanze',
                     'distanze_device',
                     'distanze_am_ziel',
                     'intervall_cad',
                     'intervall_herz',
                     'intervall_distanze',
                     'intervall_zeit',
                     'intervall_puls',
                     'anzahl_sets',
                     'anzahl_fertige_sets',
                     'reps',
                     'zonen_tabelle',
                     'intervall_tabelle',
                     'device_werte',
                     'intervall_farbe'
                     ]

ViewDatenModell = namedtuple('ViewDatenModell',
                             daten_field_names,
                             defaults=[0] * len(daten_field_names))

farbe_rot = (255, 0, 0)
farbe_gruen = (0, 255, 0)


def berechne_ergometer_daten(daten_modell: ViewDatenModell = ViewDatenModell(),
                             status: ControllerStatus = None) -> ViewDatenModell:
    return daten_modell._replace(**{
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
    })


def berechne_intervall_daten(daten_modell: ViewDatenModell = ViewDatenModell(),
                             status: ControllerStatus = None) -> ViewDatenModell:
    return daten_modell._replace(**{
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


def berechne_puls_daten(daten_modell: ViewDatenModell = ViewDatenModell(),
                        status: ControllerStatus = None) -> ViewDatenModell:
    return daten_modell._replace(**{
        'herz_frequenz': status.modell.pulsmesser.herzfrequenz,
        'herz_gesamt': status.modell.pulsmesser.herzschlaege,
        'herz_durchschnitt': status.modell.pulsmesser.calc_puls_durchschnitt(status.modell.akuelle_zeit().als_ms()),
        'herz_batterielevel': status.modell.puls_device.batterie_level})


def update_daten_modell(daten_modell: ViewDatenModell = ViewDatenModell(),
                        status: ControllerStatus = None) -> ViewDatenModell:
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
    result_modell = berechne_ergometer_daten(daten_modell=daten_modell, status=status)
    result_modell = berechne_intervall_daten(daten_modell=result_modell, status=status)
    result_modell = berechne_puls_daten(daten_modell=result_modell, status=status)

    return result_modell._replace(**{
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


def erzeuge_log_string(mein_tuple: ViewDatenModell, join_string: str = "\t") -> str:
    now = datetime.datetime.now()
    result = [
        "{0}".format(mein_tuple.trainings_name),
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S.%f")[:-3],
        "{0}".format(mein_tuple.zeit_gesamt),
        "{0}".format(mein_tuple.trainings_inhalt),
        "{0}".format(mein_tuple.zeit_timer),
        "{0}".format(mein_tuple.cad_frequenz),
        "{0}".format(mein_tuple.cad_aktuell),
        "{0}".format(mein_tuple.distanze_device),
        "{0}".format(mein_tuple.cad_durchschnitt),
        "{0}".format(mein_tuple.distanze),
        "{0}".format(mein_tuple.intervall_distanze),
        "{0}".format(mein_tuple.intervall_cad),
        "{0}".format("herz_schlaege"),
        "{0}".format("calcPulsDurchschnitt"),
        "{0}".format("calcHerzschlaegeIntervall"),
        "{0}".format("calcPulsIntervall"),
        "{0}".format(mein_tuple.pwm_wert),
        "{0}".format("herz_freq"),
        "{0}".format("batterie_level"),
        "{0}".format(mein_tuple.device_werte),
        # {'zeit': 1722690179.975749, 'herzfrequenz': 122, 'rr': [498, 502], 'rr_interval': True}
        "{0}".format("herzwert")
        ]
    return join_string.join(result)
