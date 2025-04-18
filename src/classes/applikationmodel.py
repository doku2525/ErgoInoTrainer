from __future__ import annotations
from typing import Callable, TYPE_CHECKING
import time
import serial
from src.classes.boardconnector import BoardConnector, suche_ports, meine_ports
from src.classes.ergometerdevice import ArduinoDevice
from src.classes.ergometer import Ergometer
from src.classes.pulsmesser import Pulsmesser
from src.classes.stoppuhr import Stoppuhr, FlexibleZeit, ZE
from src.classes.zonen import Zonen
if TYPE_CHECKING:
    from src.classes.bledevice import PulsmesserBLEDevice


class ApplikationModell:
    def __init__(self,
                 uhr: Stoppuhr = None,
                 zeitfunktion: Callable = time.time,
                 board: BoardConnector = None,
                 ble_pulsdevice: PulsmesserBLEDevice = None):
        self.ergo = Ergometer()
        self.zeitfunktion: Callable = lambda einheit: FlexibleZeit.create_from_sekunden(zeitfunktion()).als(einheit)
        self.millis_jetzt: Callable = lambda: self.zeitfunktion(ZE.MS)
        self.uhr = Stoppuhr.factory(self.zeitfunktion(ZE.MS)) if uhr is None else uhr
        self.zonen = Zonen()
        self.trainingsprogramm = None
        self.board = BoardConnector(startzeit=self.millis_jetzt(),
                                    device=ArduinoDevice.create_device(
                                        ports=suche_ports(meine_ports), baudrate=57600)) if board is None else board
        self.pulsmesser = Pulsmesser()
        self.puls_device = ble_pulsdevice

    def akuelle_zeit(self) -> FlexibleZeit:
        return FlexibleZeit.create_from_millis(self.uhr.zeit(self.millis_jetzt()))
