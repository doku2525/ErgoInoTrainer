from __future__ import annotations
from typing import Tuple
from dataclasses import dataclass, field
from src.classes.bledevice import BLEHeartRateData


@dataclass
class Pulsmesser:
    herzfrequenz: int = field(default_factory=int)
    herzschlaege: int = field(default_factory=int)      # Anzahl der Herzschlaege insgesamt (== len(rr_intervall))
    rr_intervall: Tuple[int] = field(default_factory=tuple)
    last_raw_data: BLEHeartRateData = field(default=None)

    def verarbeite_device_werte(self, neue_werte: BLEHeartRateData) -> Pulsmesser:
        return Pulsmesser(
            herzfrequenz=neue_werte.herzfrequenz,
            herzschlaege=self.herzschlaege + len(neue_werte.rr_intervall),
            rr_intervall=self.rr_intervall + tuple(neue_werte.rr_intervall),
            last_raw_data=neue_werte
        )

    def calc_puls_durchschnitt(self, zeit_in_millis: int) -> int:
        # Schlaege pro Minute
        return round(self.herzschlaege * 1000 * 60 / zeit_in_millis) if zeit_in_millis != 0 else 0
