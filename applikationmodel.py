from typing import Callable
import time
import serial
from boardconnector import BoardConnector, suche_ports, meine_ports
from ergometerdevice import ArduinoDevice
from ergometer import Ergometer
from stoppuhr import Stoppuhr, FlexibleZeit, ZE
from zonen import Zonen


class ApplikationModell:
    def __init__(self,
                 uhr: Stoppuhr = None,
                 zeitfunktion: Callable = time.time,
                 board: BoardConnector = None):
        self.ergo = Ergometer()
        self.zeitfunktion: Callable = lambda einheit: FlexibleZeit.create_from_sekunden(zeitfunktion()).als(einheit)
        self.millis_jetzt: Callable = lambda: self.zeitfunktion(ZE.MS)
        self.uhr = Stoppuhr.factory(self.zeitfunktion(ZE.MS)) if uhr is None else uhr
        self.zonen = Zonen()
        self.trainingsprogramm = None
        self.board = BoardConnector(startzeit=self.millis_jetzt(),
                                    device=ArduinoDevice.create_device(
                                        ports=suche_ports(meine_ports), baudrate=57600)) if board is None else board

    def akuelle_zeit(self) -> FlexibleZeit:
        return FlexibleZeit.create_from_millis(self.uhr.zeit(self.millis_jetzt()))
