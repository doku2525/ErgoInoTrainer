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


import numpy as np
import pandas as pd

def erzeuge_numpy_array(ergebnis_trainingseinheit: list[str]) -> np.ndarray:
    ergbnis_als_liste = [int(datensatz.split()[2]) for datensatz in ergebnis_trainingseinheit]
    mein_array = np.array(ergbnis_als_liste)
    return mein_array.reshape(8, 20)


def erzeuge_numpy_aller_intervalle(dateiname, training):
    return np.stack(
            [erzeuge_numpy_array(zeiten)
             for titel in parse_trainingslog(dateiname).keys() if titel.split(' : ')[1] == training
             for datum, zeiten
             in extrahiere_intervalle_fuer_training(LOG_FILE, titel).items()], axis=0)


if __name__ == '__main__':

    for elem in parse_trainingslog(LOG_FILE).keys():
        print(f"{elem.split(' : ')[1]}")

    result = erzeuge_numpy_aller_intervalle(LOG_FILE, 'Tabata')
    # print(result)
    print(result.shape)
    print(result)
    for i in range(len(result)):
        df = pd.DataFrame(result[i])
        column_means = df.mean(axis=0)
        df.loc['D'] = column_means
        row_means = df.mean(axis=1)
        df['D'] = row_means
        print(f"Matrix {i + 1}:")
        print(df)
        print("\n")
#        print(f"Durchschnitt: {np.average(result[i], axis=0)}\n")
