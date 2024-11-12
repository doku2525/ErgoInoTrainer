import sys
from tkinter import simpledialog

from src.classes.applikationmodel import ApplikationModell
from src.classes.applikationcontroller import ApplikationController
from src.classes.applikationview import ApplikationView
from src.classes.flaskview import FlaskView
from src.classes.trainingsprogramm import Trainingsprogramm
from src.classes import trainingsprogramm as tp

meine_trainings_programme = [
    ("G1 locker", "erzeuge_trainingsprogramm_G1(dauer_in_minuten=95, pwm=34, cad=100)",
        tp.erzeuge_trainingsprogramm_G1(dauer_in_minuten=95, pwm=34, cad=100)),
    ("G1 schwer", "erzeuge_trainingsprogramm_G1(dauer_in_minuten=90, pwm=40, cad=100)",
        tp.erzeuge_trainingsprogramm_G1(dauer_in_minuten=90, pwm=40, cad=100)),
    ("G1 mit 15sek Sprints", "erzeuge_trainingsprogramm_G1_mit_sprints(pwm=(34,90), cad=(100,100), warmfahrzeit=10, dauer_in_minuten=75))",
        tp.erzeuge_trainingsprogramm_G1_mit_sprints(pwm=(34, 64), cad=(100, 100), warmfahrzeit=10,
                                                    dauer_in_minuten=75)),
    ("G2 aktuell", "erzeuge_trainingsprogramm_G2Intervall((37, 47), (100, 100))",
        tp.erzeuge_trainingsprogramm_G2Intervall((37, 47), (100, 100))),
    ("G2 Nextlevel", "erzeuge_trainingsprogramm_G2Intervall((38, 48), (98, 98))",
        tp.erzeuge_trainingsprogramm_G2Intervall((38, 48), (98, 98))),
    ("Tabata 20min", "erzeuge_trainingsprogramm_Tabata((34, 54), (100, 100))",
        tp.erzeuge_trainingsprogramm_Tabata((34, 54), (100, 100), warmfahrzeit=10, ausfahrzeit=6)),
    ("Tabata 15min", "erzeuge_trainingsprogramm_Tabata((34, 54), (100, 100))",
        tp.erzeuge_trainingsprogramm_Tabata((34, 54), (100, 100), warmfahrzeit=8, ausfahrzeit=3)),
    ("Test Intervall", "erzeuge_trainingsprogramm_Tabata((34, 54), (100, 100))",
        tp.erzeuge_trainingsprogramm_Tabata((1, 10), (90, 100), warmfahrzeit=0.25, ausfahrzeit=0.25))
]


def waehle_trainingsprogramm_tkinter(meine_programme: list[(str, str, Trainingsprogramm)]) -> (Trainingsprogramm, int):
    auswahl_text = [f"{index} : {element[0]} \t-> \t{element[1]}" for index, element in enumerate(meine_programme)]
    eingabe = simpledialog.askinteger("Waehle Trainingsprogramm", "\t\n".join(auswahl_text + ["-1 : Beenden\n"]))
    if eingabe in [-1, None]:
        sys.exit()
    return (meine_programme[eingabe][2], eingabe) if eingabe in range(len(meine_programme)) else (meine_programme[0][2],
                                                                                                  0)


def waehle_trainingsprogramm_commandline(meine_programme: list[(str, str, Trainingsprogramm)]) -> Trainingsprogramm:
    for index, element in enumerate(meine_programme):
        print(f"{index} : {element[0]} -> {element[1]}")
    eingabe = int(input("Waehle Programm: "))
    return meine_programme[eingabe][2] if eingabe in range(len(meine_programme)) else meine_programme[0][2]


def log_file_warnung_tkinter(log_files: list[str]) -> str | None:
    auswahl_text = [f"{index} : {str(file)}" for index, file in enumerate(log_files)]
    eingabe = simpledialog.askinteger("Waehle Logfile", "\t\n".join(auswahl_text))
    return log_files[eingabe] if eingabe in range(len(log_files)) else sys.exit()


def main():

    log_files = [
        'daten/trainer.log',
        'daten/trainer.tmp',
        None
    ]
    log_file = log_files[2]

    mein_modell = ApplikationModell()   # Als Standard wird ArduinoBoard in ApplikationModell initialisiert
    mein_modell.trainingsprogramm, eingabe = waehle_trainingsprogramm_tkinter(meine_programme=meine_trainings_programme)
    if not meine_trainings_programme[eingabe][0][:4] == 'Test' and log_file is None:
        log_file = log_file_warnung_tkinter(log_files=log_files)
    elif meine_trainings_programme[eingabe][0][:4] == 'Test' and log_file and log_file[-3:] == "log":
        log_file = log_file_warnung_tkinter(log_files=log_files)

    # Initialisiere die einzelnen Views und erzeuge Liste mir den noetigen
    pygame_view = ApplikationView()
    flask_view = FlaskView()
    meine_views = [pygame_view]

    # Starte den Flask-Server im Hintergrund
    flask_view.start_server() if flask_view in meine_views else None

    controller = ApplikationController(model=mein_modell, views=meine_views, log_file=log_file)
    controller.programm_loop(fps=100)
    mein_modell.board.sendeUndLeseWerte(neuer_bremswert=0)


if __name__ == '__main__':
    main()
