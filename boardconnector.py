import serial
import os.path
import time
from ergometerdevice import ErgometerDevice, ArduinoDevice
from devicedatenmodell import DeviceDatenModell

meine_ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyUSB4"]


def suche_ports(ports: list[str]) -> list[str]:
    return [port for port in ports if os.path.exists(port)][:1]


class BoardConnector:
    def __init__(self, startzeit: int = 0, device: ErgometerDevice = None, bremswert_bereich: int = 100):
        self.startzeit = startzeit
        self.bremswert = 0                          # Der aktuelle Wert der Bremse zwischen 0 <= bremswert_bereich
        self.bremswert_bereich = bremswert_bereich  # 0 <= self.bremswert <= self.bremswert_bereich
        self.device = device
        self.return_string_vom_device = ""
        self.device_daten = DeviceDatenModell.erzeuge_device_daten_modell(self.device)
        self.drucke_deviceinfo()

    def lauf_zeit(self, aktuelle_zeit: int = None) -> int:
        # TODO Keine Ahnung, wofuer ich diese Funktion geplant hatte?
        if not aktuelle_zeit:
            return int(time.time()*1000) - self.startzeit
        else:
            return aktuelle_zeit - self.startzeit

    def sende_pwm_an_device(self) -> None:
        self.device.sende_daten_an_device(str(self.berechne_pwm(self.bremswert)))

    def empfange_messwerte_von_device(self) -> str:
        self.return_string_vom_device = self.device.empfange_daten_von_device()
        return self.return_string_vom_device

    def berechne_pwm(self, bremswert) -> int:
        # Rechne den Wert innerhalb des Bremswertbereiches in einen Wert des PWM-Bereichs des Devices um.
        # 0 <= bremswert <= self.bremswert_bereich
        if not self.device:
            return 0
        return int(round(self.device.pwm_bitrate * bremswert / self.bremswert_bereich))

    def sendeUndLeseWerte(self, neuer_bremswert: int = 0) -> None:
        # TODO Es waere schoen, wenn die Funktion einen Rueckgabewert haette. Z.B. den neuen Wert von device_daten
        # TODO Noch kein Test geschrieben
        self.bremswert = neuer_bremswert
        self.sende_pwm_an_device()
        self.empfange_messwerte_von_device()
        self.device_daten = self.device_daten.verarbeite_messwerte(self.return_string_vom_device)

    def drucke_deviceinfo(self) -> bool:
        def drucke() -> None:
            print(f"\n\n    Deviceinfo  -> *** {self.device.__class__.__name__} ***")
            print(f"    Version     ->   {self.device.version}")
            print(f"    Arduinozeit ->   {self.device.zeit_arduino}")
            print(f"    Cadzeit     ->   {self.device.zeit_cadenze}\n\n")

        if (self.device and isinstance(self.device.port, serial.Serial) and self.device.port.is_open
                and self.device.port.port):
            self.device.lese_deviceinfos()
            drucke()
            return True
        if self.device and callable(self.device.port):
            self.device.lese_deviceinfos()
            drucke()
            return True
        return False
