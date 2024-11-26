from __future__ import annotations
from typing import TYPE_CHECKING
import copy
if TYPE_CHECKING:
    from src.classes.stoppuhr import FlexibleZeit


class Zonen:
    def __init__(self):
        self.zonen = {}     # dict[pwmwert]['zeit'|'dist'|'herz][bisherGesamt, aktuellerStart]
        self.tachoWerte = {'dist': [0, 0, 0], 'zeit': [0, 0, 0], 'herz': [0, 0, 0]}   # Anscheinend wird nur [0] benutzt
        self.daten = {}     # Wird offensichtlich ueberhaupt nicht verwendet
        self.__pwm = 0      # letzter PWM-Wert

    def updateZone(self, pwm: int | float, zeit: FlexibleZeit, dist: int, herz: int = 0) -> None:
        lokale_zeit = zeit.als_s()
        self.updateTacho(lokale_zeit, dist, herz)
        if len(self.zonen.keys()) == 0:
            self.__pwm = pwm
        if pwm not in self.zonen.keys():  # Bisher unbekannter PWM-Wert
            self.zonen[pwm] = {'zeit': [0, lokale_zeit], 'dist': [0, dist], 'herz': [0, herz]}
        if self.__pwm == pwm:       # PWM hat sich seit letztem Aufruf nicht veranedert
            self.tachoWerte['zeit'][0] = lokale_zeit
            self.tachoWerte['dist'][0] = dist
            self.tachoWerte['herz'][0] = herz
        else:                       # PWM hat sich veranedert und die Werte des vorherigen PWM muss angepasst werden.
            # Berechne die Werte fuer den alten PWM-Wert
            # Position 2 beinhaltet die Werte bei Beginn Position 1 die bisher in dem PWM-Bereich gefahrenen Werte
            self.zonen[self.__pwm]['zeit'][0] += lokale_zeit - self.zonen[self.__pwm]['zeit'][1]
            self.zonen[self.__pwm]['dist'][0] += dist - self.zonen[self.__pwm]['dist'][1]
            self.zonen[self.__pwm]['herz'][0] += herz - self.zonen[self.__pwm]['herz'][1]
            if self.zonen[self.__pwm]['zeit'][0] == 0:
                self.zonen.pop(self.__pwm, None)
            # Setze die hintere (zonen[][][1]) Position auf die aktuellen Werte
            self.zonen[pwm]['zeit'][1] = lokale_zeit
            self.zonen[pwm]['dist'][1] = dist
            self.zonen[pwm]['herz'][1] = herz
            self.__pwm = pwm        # Setze den letzten PWM-Wert auf aktuellen PWM-Wert

    def updateTacho(self, zeit_in_s, dist, herz):
        self.tachoWerte['zeit'][0] = zeit_in_s
        self.tachoWerte['dist'][0] = dist
        self.tachoWerte['herz'][0] = herz

    def calcWerteProZone(self) -> dict:
        result = {}
        for pwm in self.zonen.keys():
            result[pwm] = {}
            if pwm == self.__pwm:
                for feld in self.zonen[pwm].keys():
                    result[pwm][feld] = self.zonen[pwm][feld][0] + self.tachoWerte[feld][0] - self.zonen[pwm][feld][
                        1]
            else:
                for feld in self.zonen[pwm].keys():
                    result[pwm][feld] = self.zonen[pwm][feld][0]
            result[pwm]['cad'] = 0 if result[pwm]['zeit'] == 0 else 60.0 * result[pwm]['dist'] / result[pwm]['zeit']
            result[pwm]['bpm'] = 0 if result[pwm]['zeit'] == 0 else 60.0 * result[pwm]['herz'] / result[pwm]['zeit']
        return result

    def calcPowerProZone(self):
        result = {}
        werte = self.calcWerteProZone()
        for pwm in werte.keys():
            result[pwm] = {}
            result[pwm]['all'] = werte[pwm]['dist'] * pwm
            result[pwm]['dur'] = 60.0 * result[pwm]['all'] / werte[pwm]['zeit'] if werte[pwm]['zeit'] > 0 else 0
        return result

    def calcPowerGesamt(self) -> int:
        return sum(map(lambda a: a['all'], self.calcPowerProZone().values()))

    def calcPowerDurchschnitt(self) -> float:
        if self.tachoWerte['zeit'][0] == 0:
            return 0
        else:
            return 60.0 * self.calcPowerGesamt() / self.tachoWerte['zeit'][0]

    def mergeWerteAndPower(self):
        result = {}
        werte = self.calcWerteProZone()
        power = self.calcPowerProZone()
        for pwm in werte.keys():
            result[pwm] = copy.copy(werte[pwm])
            result[pwm].update(power[pwm])
        return result
