import csv
import datetime
import time
from typing import NamedTuple


LOG_FILE = '../../daten/log/trainer.log'


class LogZeile(NamedTuple):
    name: str
    datum: str
    uhrzeit: str
    dauer: str
    inhalt: str
    intervall_countdown: int
    cad: int
    cad_ziel: int
    unbekannt_eins: int
    cad_avg: float
    distanze: int
    distanze_intervall: int
    cad_avg_intervall: int
    herzschlaege: int
    puls_avg: int
    herzschlaege_intervall: int
    puls_avg_intervall: int
    pwm: float
    puls: int
    batterie_level_puls: int
    arduino_string: str
    ble_pulsdevice_string: str


def parse_trainingslog(dateiname: str) -> dict:
    with open(dateiname, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        start_zeit = datetime.datetime.strptime('0:00:01', '%H:%M:%S').time()
        result = {}
        for zeile in reader:
            obj = LogZeile(*zeile)

            # training, *_ = zeile
            trainingszeit = datetime.datetime.strptime(obj.dauer, '%H:%M:%S').time()
            # print(zeile)

            if trainingszeit == start_zeit:
                result = result | {f"{obj.datum} : {obj.name}": {}}
            # if obj.name == "G1 mit 15sek Sprints" and obj.inhalt == 'Intervall':
            #     print(f" {obj.intervall_countdown} {obj.pwm} {obj.cad} {obj.cad_avg_intervall}")

    return result


def extrahiere_intervalle_fuer_training(dateiname: str, trainings_string: str) -> dict:
    with open(dateiname, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        start_zeit = datetime.datetime.strptime('0:00:01', '%H:%M:%S').time()
        result = {}
        for zeile in reader:
            obj = LogZeile(*zeile)

            # training, *_ = zeile
            trainingszeit = datetime.datetime.strptime(obj.dauer, '%H:%M:%S').time()
            # print(zeile)

            schluessel = f"{obj.datum} : {obj.name}"
            if trainingszeit == start_zeit and schluessel == trainings_string:
                result = result | {schluessel: []}
            if schluessel == trainings_string and obj.inhalt == 'Intervall':
                result = result | {
                    schluessel: result.get(schluessel, []) + [
                            f"{obj.intervall_countdown}\t{obj.pwm}\t{obj.cad}\t{obj.cad_avg_intervall}"]}

    return result


def drucke_jeden_intervall(dateiname, training):
    for titel in parse_trainingslog(dateiname).keys():
        if titel.split(' : ')[1] == training:
            for datum, zeiten in extrahiere_intervalle_fuer_training(LOG_FILE, titel).items():
                print(f"{datum}")
                for zeile in zeiten:
                    print(f"\t{zeile}")


if __name__ == '__main__':

    for elem in parse_trainingslog(LOG_FILE).keys():
        print(f"{elem.split(' : ')[1]}")

    drucke_jeden_intervall(LOG_FILE, 'G1 mit 15sek Sprints')
