import csv
import datetime
import time
from typing import NamedTuple


LOG_FILE = '../../daten/log/trainer.log'


class LogZeile(NamedTuple):
    name: str
    datum: datetime.date
    uhrzeit: datetime.time
    dauer: datetime.time
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
            #if obj.name == "G1 mit 15sek Sprints" and obj.inhalt == 'Intervall':
            #    print(f" {obj.intervall_countdown} {obj.pwm} {obj.cad} {obj.cad_avg_intervall}")

    return result


if __name__ == '__main__':

    for elem in parse_trainingslog(LOG_FILE).keys():
        print(f"{elem}")
