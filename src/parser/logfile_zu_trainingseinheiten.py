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


def erzeuge_numpy_array(ergebnis_trainingseinheit: list[str], training: str) -> np.ndarray:
    ergbnis_als_liste = [int(datensatz.split()[2]) for datensatz in ergebnis_trainingseinheit]
    mein_array = np.array(ergbnis_als_liste)
    # Ersetze Null-Werte durch den Durchschnittswert der beiden Nachbarn
    print(f"Eleminiere Nullwerte")
    zero_indices = np.where(mein_array == 0)[0]
    for index in zero_indices:
        if index == 0:
            mein_array[index] = mein_array[index + 1]
        elif index == len(mein_array) - 1:
            mein_array[index] = mein_array[index - 1]
        else:
            mein_array[index] = (mein_array[index - 1] + mein_array[index + 1]) / 2
    if training == 'G2Intervall' and mein_array.shape[0] < 360:
        mein_array = np.pad(mein_array, (0, 360 - len(mein_array)), 'constant', constant_values=1)
    print(f"Erzeuge_Numpy_Array: {mein_array.shape = }")
    match training:
        case 'K3':
            # Bei vielen Werten fasse die Werte zu Zeiteinheiten zusammen.
            form = (3, 10)  # Bei 1min Steigerung kleinste moegl. Form (3,60)=5s/Block, (3,30)=10s, (3x15)=20s fuer 5min
            reshaped_array = mein_array.reshape(form[0], form[1], int(mein_array.size / (form[0] * form[1])))
            print(f" {reshaped_array.shape = }")
            return np.mean(reshaped_array, axis=2).reshape(form)  # Berechne den Durchschnitt fuer jede Zeile
        case 'Tabata': return np.round(mein_array.reshape(8, 20), 0)
        case 'G1 mit 15sek Sprints': return mein_array.reshape(4, 15)
        case 'G2Intervall': return (mein_array.reshape(6, 60) if len(mein_array) == 360 else
                                    np.pad(mein_array, (0, 360 - len(mein_array)), 'constant', constant_values=1))


def erzeuge_numpy_aller_intervalle(dateiname, training):
    return np.stack(
            [erzeuge_numpy_array(zeiten, training)
             for titel in parse_trainingslog(dateiname).keys() if titel.split(' : ')[1] == training
             for datum, zeiten
             in extrahiere_intervalle_fuer_training(LOG_FILE, titel).items()], axis=0)

def find_max_matrix(matrices):
  """
  Findet für jede Position in den Matrizen den maximalen Wert.

  Args:
    matrices: Eine Liste von Matrizen (NumPy-Arrays oder Listen von Listen).

  Returns:
    Eine Matrix, die an jeder Position den maximalen Wert enthält.
  """

  # Konvertiere die Matrizen in NumPy-Arrays für effizientere Berechnungen
  np_matrices = [np.array(matrix) for matrix in matrices]
  # Stapele die Matrizen entlang der dritten Achse (Tiefe)
  stacked_matrices = np.stack(np_matrices, axis=2)
  # Bestimme den Maximalwert entlang der dritten Achse
  max_matrix = np.max(stacked_matrices, axis=2)
  mean_matrix = np.mean(stacked_matrices, axis=2)
  return max_matrix, mean_matrix

if __name__ == '__main__':

    for elem in parse_trainingslog(LOG_FILE).keys():
        print(f"{elem.split(' : ')[1]}")
    verfuegbare_trainings = ['K3', 'Tabata', 'G1 mit 15sek Sprints', 'G2Intervall']
    result = erzeuge_numpy_aller_intervalle(LOG_FILE, verfuegbare_trainings[-1])
    # print(result)
    print(result.shape)
    print(np.round(result, 1))
    for i in range(len(result)):
        df = pd.DataFrame(result[i])
        column_means = df.mean(axis=0)
        df.loc['D'] = column_means
        row_means = df.mean(axis=1)
        df['D'] = row_means
        print(f"Matrix {i + 1}:")
        print(df.round(2))
        print("\n")
#        print(f"Durchschnitt: {np.average(result[i], axis=0)}\n")

    max_mat, mea_mat = find_max_matrix(result)
    df = pd.DataFrame(max_mat)
    column_means = df.mean(axis=0)
    df.loc['D'] = column_means
    row_means = df.mean(axis=1)
    df['D'] = row_means
    print(f"Maximalwerte\n{df.round(2)}")
    df = pd.DataFrame(mea_mat)
    column_means = df.mean(axis=0)
    df.loc['D'] = column_means
    row_means = df.mean(axis=1)
    df['D'] = row_means
    print(f"Durchschnittswerte\n{df.round(2)}")
