from __future__ import annotations
from typing import TYPE_CHECKING
from collections import namedtuple
import copy
if TYPE_CHECKING:
    from src.classes.stoppuhr import FlexibleZeit


TACHO_FIELD_NAMES = ['dist', 'zeit', 'herz']
Tachowerte = namedtuple('Tachowerte', TACHO_FIELD_NAMES, defaults=[0, 0, 0])

Tachowerte.__sub__ = lambda self, other: Tachowerte(dist=self.dist - other.dist,
                                                    zeit=self.zeit - other.zeit,
                                                    herz=self.herz - other.herz)

Tachowerte.__add__ = lambda self, other: Tachowerte(dist=self.dist + other.dist,
                                                    zeit=self.zeit + other.zeit,
                                                    herz=self.herz + other.herz)

ZonenWerte = namedtuple('ZonenWerte', ['gesamt', 'neuer_calc_punkt'],
                        defaults=[Tachowerte(),Tachowerte()])


def updateTacho(zeit_in_s: int, dist: int, herz: int) -> Tachowerte:
    return Tachowerte(zeit=zeit_in_s, dist=dist, herz=herz)


class Zonen:
    def __init__(self):
        self.zonen: dict[int | float, ZonenWerte] = {}     # dict[pwmwert] = ZonenWerte
        self.tachoWerte: Tachowerte = Tachowerte()
        # self.daten = {}     # Wird offensichtlich ueberhaupt nicht verwendet
        self.__pwm = 0      # letzter PWM-Wert

    def updateZone(self, pwm: int | float, zeit: FlexibleZeit, dist: int, herz: int = 0) -> None:
        lokale_zeit = zeit.als_s()
        self.tachoWerte = updateTacho(zeit_in_s=lokale_zeit, dist=dist, herz=herz)

        if len(self.zonen.keys()) == 0:
            self.__pwm = pwm

        if pwm not in self.zonen.keys():  # Bisher unbekannter PWM-Wert
            self.zonen[pwm] = ZonenWerte(neuer_calc_punkt=self.tachoWerte)

        if self.__pwm != pwm:
            # PWM-Wert hat sich veraendert, berechne Werte fuer den alten PWM-Wert (neu = bisher + aktueller - start)
            self.zonen[self.__pwm] = self.zonen[pwm]._replace(gesamt=self.zonen[self.__pwm].gesamt + self.tachoWerte -
                                                              self.zonen[self.__pwm].neuer_calc_punkt)
            self.zonen[pwm] = self.zonen[pwm]._replace(neuer_calc_punkt=self.tachoWerte)
            # Fuer pwm-Werte ohne Zeit wollen wir keine Werte. Z.B. beim Verstellen der Bremse wahrend der Pause.
            if self.zonen[self.__pwm].gesamt.zeit == 0:
                self.zonen.pop(self.__pwm, None)
            self.__pwm = pwm        # Setze den letzten PWM-Wert auf aktuellen PWM-Wert

    def calcWerteProZone(self) -> dict:
        def calc_tachowerte(pwm: float | int) -> Tachowerte:
            return (self.zonen[pwm].gesamt + self.tachoWerte - self.zonen[pwm].neuer_calc_punkt if pwm == self.__pwm
                    else self.zonen[pwm].gesamt)

        return {
            pwm: calc_tachowerte(pwm)._asdict() | {
                'cad': (60.0 * value.gesamt.dist / value.gesamt.zeit) if value.gesamt.zeit else 0,
                'bpm': (60.0 * value.gesamt.herz / value.gesamt.zeit) if value.gesamt.zeit else 0
            }
            for pwm, value in self.zonen.items()}  # value = [x, y]

    def calcPowerProZone(self) -> dict:
        return {
            pwm: {
                'all': value['dist'] * pwm,
                'dur': value['dist'] * pwm * 60 / value['zeit'] if value['zeit'] > 0 else 0
            }
            for pwm, value in self.calcWerteProZone().items()
        }

    def calcPowerGesamt(self) -> int:
        return sum(map(lambda a: a['all'], self.calcPowerProZone().values()))

    def calcPowerDurchschnitt(self) -> float:
        if self.tachoWerte.zeit == 0:
            return 0
        else:
            return 60.0 * self.calcPowerGesamt() / self.tachoWerte.zeit

    def mergeWerteAndPower(self) -> dict:
        return {
            pwm: werte | power
            for pwm, werte in self.calcWerteProZone().items()
            for power in [self.calcPowerProZone()[pwm]]
        }
