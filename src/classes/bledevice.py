from abc import ABC, abstractmethod
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


class Pulsmesser(BLEDevice):

    def __init__(self, blt_addresse: str = "E4:B2:5F:32:5C:AF", ):
        self.__bltAddr = "E4:B2:5F:32:5C:AF"
        self.__hrCtlHandle = "0x000c"
        self.__hrHandle = "0x000b"
        self.__gattool = pexpect.spawn("gatttool" + " -b " + self.__bltAddr + " -t random --interactive")
        self.__herzFreq = 0
        self.__herzWert = False
        self.__batterieLevel = 0
        self.__connected = False
        self.__hfDaten = deque([], maxlen=1)
        self.__hfStart = True
        self.__thread = 0

    def batterieLevel(self):
        if (not self.__connected):
            return 0
        else:
            return batterieLevel

    def letzteHF(self):
        if (not self.__connected):
            return 0
        else:
            return int(herzwert["herzfrequenz"])

    def connect(self):
        self.__gattool.sendline("connect")
        self.__gattool.expect("Connection successful", timeout=5)
        print("Mit BLE Verbunden!")
        self.__gattool.sendline("char-read-uuid 00002a19-0000-1000-8000-00805f9b34fb")
        self.__gattool.expect("handle: 0x0011 \t value: ([0-9a-f]+)", timeout=10)
        self.__batterieLevel = int(gattool.match.group(1), 16)
        self.__connected = True

    def startHF(self):
        if (not self.__connected):
            return 0
        else:
            self.__gattool.sendline("char-write-req " + self.__hrCtlHandle + " 0100")
            self.__thread = Thread(target=self.leseHF)
            self.__thread.start()

    def interpretiereHF(self, data, zeitpunkt):
        """
        data is a list of integers corresponding to readings from the BLE HR monitor
        """
        byte0 = data[0]
        res = {}
        res["zeit"] = zeitpunkt
        res["rr_interval"] = ((byte0 >> 4) & 1) == 1
        res["herzfrequenz"] = data[1]
        i = 2
        if res["rr_interval"]:
            res["rr"] = []
            while i < len(data):
                # Note: Need to divide the value by 1024 to get in seconds
                res["rr"].append((data[i + 1] << 8) | data[i])
                i += 2
        return res

    def leseHF(self):
        while self.__hfStart:
            self.__hrExpect = "Notification handle = " + self.__hrHandle + " value: ([0-9a-f ]+)"
            self.__gattool.expect(self.__hrExpect)
            datahex = self.__gattool.match.group(1).strip()
            zeit = time.time()
            data = map(lambda x: int(x, 16), datahex.split(b' '))
            self.__hfDaten.append(interpretiere_herzfrequenz(list(data), zeit))

    def updateHF(self):
        if (len(self.__hfdaten) > 0): self.__herzWert = self.__hfdaten.pop()
        return self.__herzWert

    def stopHF(self):
        self.__gattool.sendline("quit")
        print("Beende BLE-Connection!")
