from __future__ import annotations
from typing import Any
import copy
import datetime

from src.classes.stoppuhr import FlexibleZeit


class DatenProcessor:

    def __init__(self, zeit_timer: FlexibleZeit = FlexibleZeit.create_from_millis(0),
                 trainings_name: str = "",
                 trainings_inhalt: str = "",
                 cad_frequenz: int = 0,
                 cad_durchschnitt: float = 0,
                 cad_aktuell: int = 0,
                 pwm_wert: float = 0,
                 distanze: int = 0,
                 power_aktuell: float = 0,
                 power_gesamt: int = 0,
                 power_durchschnitt: float = 0,
                 power_watt: int = 0,
                 werte_und_power: dict[str] = None,
                 arduino_werte: list[Any] = None,
                 distanze_am_ziel: int = 0):

        self.__uhr_zeit = datetime.datetime.now()
        self.zeit_gesamt = zeit_timer
        self.zeit_timer = zeit_timer
        self.trainings_name = trainings_name
        self.trainings_inhalt = trainings_inhalt
        self.cad_frequenz = cad_frequenz
        self.cad_durchschnitt = cad_durchschnitt
        self.cad_aktuell = cad_aktuell
        self.pwm_wert = pwm_wert
        self.distanze = distanze
        self.power_aktuell = power_aktuell
        self.power_gesamt = power_gesamt
        self.power_durchschnitt = power_durchschnitt
        self.power_watt = power_watt
        self.werte_und_power = werte_und_power if werte_und_power is not None else {}
        self.arduino_werte = arduino_werte if arduino_werte is not None else []
        self.distanze_am_ziel = distanze_am_ziel

    def get_zeit_gesamt(self) -> str:
        return str(datetime.timedelta(seconds=self.zeit_gesamt.als_s()))

    def get_datum(self) -> str:
        return self.__uhr_zeit.strftime("%Y-%m-%d")

    def get_uhrzeit(self) -> str:
        return self.__uhr_zeit.strftime("%H:%M:%S.%f")[:-3]

    def get_cad_differenz(self) -> int:
        return self.cad_frequenz - self.cad_aktuell

    def process_zeit_gesamt(self, zeit_wert: FlexibleZeit | None = None) -> str:
        if zeit_wert is None:
            return ""
        result = copy.copy(self)
        result.zeit_gesamt = datetime.timedelta(seconds=int(zeit / 1000))     # TODO Noch nicht fertig implementiert
