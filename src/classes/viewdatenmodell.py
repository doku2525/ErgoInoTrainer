from collections import namedtuple
import datetime

daten_field_names = ['trainings_name',
                     'trainings_inhalt',
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
        "{0}".format("herzwert")
        ]
    return join_string.join(result)
