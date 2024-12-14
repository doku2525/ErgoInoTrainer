import csv
import datetime


LOG_FILE = '../../daten/log/trainer.log'


def parse_trainingslog(dateiname: str) -> dict:
    with open(dateiname, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        start_zeit = datetime.datetime.strptime('0:00:01', '%H:%M:%S').time()
        result = {}
        for zeile in reader:
            training, datum, uhrzeit, dauer, einheit_name, *_ = zeile
            # training, *_ = zeile
            trainingszeit = datetime.datetime.strptime(dauer, '%H:%M:%S').time()
            # print(zeile)

            if trainingszeit == start_zeit:
                result = result | {f"{datum} {training}": {}}

    return result


if __name__ == '__main__':

    for elem in parse_trainingslog(LOG_FILE).keys():
        print(f"{elem}")
