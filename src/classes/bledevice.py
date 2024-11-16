from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import Thread
from collections import deque
import pexpect
import time


class BLEDevice(ABC):

    @abstractmethod
    def lese_messwerte(self) -> str:
        pass

    @abstractmethod
    def sende_befehl(self,befehl: str) -> None:
        pass

    @abstractmethod
    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass


class PulsmesserBLEDevice(BLEDevice):
    """
    Fuer ein typisches Protokoll siehe auch https://gist.github.com/fphammerle/d758ecf1968c0708eca66b5e9e5347d1
    """
    def __init__(self, blt_addresse: str = "E4:B2:5F:32:5C:AF", hrCtlHandle: str = "0x000c",
                 hrHandle: str = "0x000b", queue_maxlen: int = 1):
        self.bltAddr = blt_addresse
        self.hrCtlHandle = hrCtlHandle
        self.hrHandle = hrHandle
        self.gattool = pexpect.spawn("gatttool" + " -b " + self.bltAddr + " -t random --interactive")
        self.herzfrequenz = 0                   # TODO Funktion in Pulsmesser-Klasse auslagern
        self.device_messwerte: dict = dict()    # TODO Funktion in Pulsmesser-Klasse auslagern.
        self.batterie_level = 0
        self.connected = False
        self.messdaten_queue = deque([], maxlen=queue_maxlen)
        self.lese_bledevice_loop_flag = True
        self.thread = None
#        self.connect()
#        self.starte_lese_bledevice_loop()

    def lese_messwerte(self) -> str:
        raise NotImplementedError

    def sende_befehl(self,befehl: str) -> None:
        raise NotImplementedError

    def connect(self) -> bool:
        self.gattool.sendline("connect")
        antwort = self.gattool.expect([pexpect.TIMEOUT, "Connection successful"], timeout=5)
        if antwort == 1:
            print(f"Mit BLE Verbunden!")
            return True
        else:
            print(f"Timout. Kein Verbindung mit BLE!")
            return False

    def lese_batterie_level(self) -> int:
        self.gattool.sendline("char-read-uuid 00002a19-0000-1000-8000-00805f9b34fb")
        antwort = self.gattool.expect([pexpect.TIMEOUT, "handle: 0x0011 \t value: ([0-9a-f]+)"], timeout=10)
        if antwort == 1:
            self.batterie_level = int(self.gattool.match.group(1), 16)
            return self.batterie_level
        else:
            return 0

    def disconnect(self) -> None:
        self.gattool.sendline("quit")
        print("Beende BLE-Connection!")

    def starte_lese_bledevice_loop(self) -> bool:
        if (not self.connected):
            return False
        else:
            self.gattool.sendline("char-write-req " + self.hrCtlHandle + " 0100")
            self.thread = Thread(target=self.lese_bledevice)
            self.thread.start()
            return True

    def letzteHF(self):
        if not self.connected:
            return 0
        else:
            return int(herzwert["herzfrequenz"])

    @staticmethod
    def interpretiere_herzfrequenz(self, raw_messwerte: list[int], aktuelle_zeit: float) -> dict:
        """
        data is a list of integers corresponding to readings from the BLE HR monitor
        """
        # TODO Resultwert nicht als Dictionary, sondern eigenen Datentypen zurueckgeben
        byte0 = raw_messwerte[0]
        result = {"zeit": aktuelle_zeit,
                  "rr_interval": ((byte0 >> 4) & 1) == 1,
                  "herzfrequenz": raw_messwerte[1]}
        i = 2
        if result["rr_interval"]:
            result["rr"] = []
            while i < len(raw_messwerte):
                # Note: Need to divide the value by 1024 to get in seconds
                result["rr"].append((raw_messwerte[i + 1] << 8) | raw_messwerte[i])
                i += 2
            # TODO Schreibe while-Schleife als list comprehension
            #   [(raw_messwerte[index + 1] << 8) | raw_messwerte[index]) for index in range(2,len(raw_messwerte), 2)]
        return result

    def lese_bledevice(self):
        # Lese die Daten in einer Schleife vom Geraet
        # Typischer Ruecggabewert ist wie folgt: "Notification handle = 0x0010 value: 10 4e ba 03 9f 03"
        while self.lese_bledevice_loop_flag:
            hr_expect = "Notification handle = " + self.hrHandle + " value: ([0-9a-f ]+)"
            self.gattool.expect(hr_expect)
            datahex = self.gattool.match.group(1).strip()
            aktuelle_zeit = time.time()
            raw_messwerte_als_liste = list(map(lambda x: int(x, 16), datahex.split(b' ')))
            # Verarbeite Daten und setze das Ergebnis ans Ende des Queues mit den Messdaten
            self.messdaten_queue.append(interpretiere_herzfrequenz(raw_messwerte_als_liste, aktuelle_zeit))

    def updateHF(self):
        if (len(self.hfdaten) > 0): self.device_messwerte = self.hfdaten.pop()
        return self.device_messwerte


@dataclass(frozen=True)
class BLEHeartRateData:
    bit_flag: int               # Zeigt an, ob Werte 16bit sind. bit_flag == 16
    herzfrequenz: int
    rr_intervall: list[int]

    @classmethod
    def from_raw_data(cls, raw_hex_datastring: bytes) -> BLEHeartRateData:
        def bytes_zu_int(x: int, y: int) -> int:
            return (y << 8) | x

        als_liste_mit_int = list(map(lambda x: int(x, 16), raw_hex_datastring.split(b' ')))
        return BLEHeartRateData(bit_flag= als_liste_mit_int[0],
                                herzfrequenz=als_liste_mit_int[1],
                                rr_intervall=[bytes_zu_int(als_liste_mit_int[index], als_liste_mit_int[index + 1])
                                              for index
                                              in range(2, len(als_liste_mit_int) - 1, 2)])

    def als_raw_hex_datastring(self) -> str:
        def int_zu_bytes(zahl: int) -> tupel[int, int]:
            return zahl & 0xFF, (zahl >> 8) & 0xFF
        hex_values = [
                f"{self.bit_flag:02x}",
                f"{self.herzfrequenz:02x}",
                *[f"{wertx:02x} {werty:02x}" for wertz in self.rr_intervall for wertx, werty in [int_zu_bytes(wertz)]]
            ]
        return " ".join(hex_values)