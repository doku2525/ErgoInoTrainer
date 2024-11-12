from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from src.classes.ergometerdevice import ArduinoDevice


@dataclass(frozen=True)
class DeviceDatenModell(ABC):
    runtime: int = 0
    pwm: int = 0
    cad: int = 0
    distanze: int = 0

    @abstractmethod
    def verarbeite_messwerte(self, messwerte_als_string: str | bytes) -> DeviceDatenModell:
        pass

    @staticmethod
    def erzeuge_device_daten_modell(device):
        if isinstance(device, ArduinoDevice):
            return ArduinoDatenModell()
        else:
            return None
#            raise TypeError("Unbekannter Gerätetyp")


@dataclass(frozen=True)
class ArduinoDatenModell(DeviceDatenModell):
    undef1: int = 0
    undef2: int = 0
    runtime_pro_tritt: tuple[int, int, int, int] = field(default=(0, 0, 0, 0))

    def verarbeite_messwerte(self, messwerte_als_string: str | bytes) -> DeviceDatenModell:
        liste = messwerte_als_string.decode().split(',')
        return ArduinoDatenModell(
            runtime=int(liste[0].strip()),
            pwm=int(liste[1].strip()),
            cad=int(liste[2].strip()),
            distanze=int(liste[3].strip()),
            undef1=int(liste[4].strip()),
            undef2=int(liste[5].strip()),
            runtime_pro_tritt=(int(liste[6].strip()), int(liste[7].strip()),
                               int(liste[8].strip()), int(liste[9].strip()))
        )
