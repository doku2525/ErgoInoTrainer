from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field, replace
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
                        defaults=[Tachowerte(), Tachowerte()])


@dataclass(frozen=True)
class Zonen:
    zonen: dict[int | float, ZonenWerte] = field(default_factory=dict)
    tachoWerte: Tachowerte = field(default_factory=Tachowerte)
    pwm: float | int = field(default_factory=float)

    def updateZone(self, pwm: int | float, zeit: FlexibleZeit, dist: int, herz: int = 0) -> Zonen:
        def calc_neue_gesamtwerte(objekt: Zonen) -> Tachowerte:
            return objekt.zonen[objekt.pwm].gesamt + objekt.tachoWerte - objekt.zonen[objekt.pwm].neuer_calc_punkt

        lokale_zeit = zeit.als_s()
        result = replace(self, tachoWerte=Tachowerte(zeit=lokale_zeit, dist=dist, herz=herz))

        if len(result.zonen.keys()) == 0:
            result = replace(result, pwm=pwm)
        if pwm not in result.zonen.keys():  # Bisher unbekannter PWM-Wert
            result = replace(result, zonen=result.zonen | {pwm: ZonenWerte(neuer_calc_punkt=result.tachoWerte)})

        if result.pwm != pwm:
            # PWM-Wert hat sich veraendert, berechne Werte fuer den alten PWM-Wert (neu = bisher + aktueller - start)
            result = replace(result,
                             zonen=result.zonen | {result.pwm:
                                                   result.zonen[pwm]._replace(gesamt=calc_neue_gesamtwerte(result))})
            result = replace(result,
                             zonen=result.zonen | {pwm: result.zonen[pwm]._replace(neuer_calc_punkt=result.tachoWerte)})

            if result.zonen[result.pwm].gesamt.zeit == 0:
                result = replace(result,
                                 zonen={key: value for key, value in result.zonen.items() if key != result.pwm})
            result = replace(result, pwm=pwm)

        return result

    def calcWerteProZone(self) -> dict:
        def calc_tachowerte(pwm: float | int) -> Tachowerte:
            return (self.zonen[pwm].gesamt + self.tachoWerte - self.zonen[pwm].neuer_calc_punkt if pwm == self.pwm
                    else self.zonen[pwm].gesamt)
        return {
            pwm: (tachowerte := calc_tachowerte(pwm))._asdict() | {
                'cad': (60.0 * tachowerte.dist / tachowerte.zeit) if tachowerte.zeit else 0,
                'bpm': (60.0 * tachowerte.herz / tachowerte.zeit) if tachowerte.zeit else 0
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
        """Liefer die Zonen als dict.
        Da Werte mit Bremse == 0 nur bei Pausen entstehen, koennen sie herausgefiltert werden."""
        return {
            pwm: werte | power
            for pwm, werte in self.calcWerteProZone().items() if pwm != 0.0
            for power in [self.calcPowerProZone()[pwm]]
        }
