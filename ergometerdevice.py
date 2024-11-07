from typing import Any, Callable
from abc import ABC, abstractmethod

import serial
from serial import Serial


def convert_to_arduino_command(kommando_string: str) -> bytes:
    return kommando_string.encode() if kommando_string.endswith("\n") else (kommando_string + "\n").encode()


class ErgometerDevice(ABC):

    @abstractmethod
    def empfange_daten_von_device(self) -> str:
        pass

    @abstractmethod
    def sende_daten_an_device(self, kommando_string: str = "0",
                              konverter: Callable[[str], bytes] = convert_to_arduino_command) -> bytes:
        pass

    @abstractmethod
    def lese_deviceinfos(self):
        pass


class ArduinoDevice(ErgometerDevice):

    def __init__(self, port: Serial, pwm_bitrate: int = 255, has_device_infos: bool = True):
        self.version: str = ""
        self.zeit_arduino: int = 0
        self.zeit_cadenze: int = 0
        self.port: Serial = port
        self.pwm_bitrate: int = pwm_bitrate
        self.has_device_infos: bool = has_device_infos

    def empfange_daten_von_device(self) -> bytes:
        return self.port.readline()

    def sende_daten_an_device(self, kommando_string: str = "0",
                              konverter: Callable[[str], bytes] = convert_to_arduino_command) -> bytes:
        self.port.write(konverter(kommando_string))
        return konverter(kommando_string)

    def lese_deviceinfos(self) -> None:
        if not self.version:      # Funktioniert nur beim ersten Aufruf. Danach kommen nur noch Messwerte.
            # Nano_Ergometer V0 hat 4 Infozeilen. Die 2. Zeile ist eine Leerzeile.
            lines = 4
            number_index = 2
            liste = [self.empfange_daten_von_device().decode().strip() for _ in range(lines)]

            if len(liste) == 4:
                self.version = liste[0]
                self.zeit_arduino, self.zeit_cadenze = [int(wert) for wert in liste[number_index:]]

    @classmethod
    def create_device(cls, ports: list[str] = None, baudrate: int = 57600) -> ErgometerDevice:
        return cls(port=serial.Serial(port=ports[0], baudrate=baudrate)) if ports else None


class ArduinoSimulator(ErgometerDevice):

    def __init__(self, port: Callable, cad: int = 60,  pwm_bitrate: int = 255,  has_device_infos: bool = True):
        self.version: str = ""
        self.zeit_arduino: int = 0
        self.zeit_cadenze: int = 0
        self.cad: int = cad
        self.port: Callable = port
        self.pwm_bitrate = pwm_bitrate
        self.has_device_infos: bool = has_device_infos

    def empfange_daten_von_device(self) -> bytes:
        if not self.port():
            return b'1000,10,20,30,40,50,900,920,940,950\r\n'
        else:
            return self.port()

    def sende_daten_an_device(self, kommando_string: str = "0",
                              konverter: Callable[[str], bytes] = convert_to_arduino_command) -> bytes:
        return konverter(kommando_string)

    def lese_deviceinfos(self) -> None:
        self.version: str = "Sketch: Simulator v0"
        self.zeit_arduino: int = 148803000
        self.zeit_cadenze: int = 14880250
