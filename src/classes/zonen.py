import copy
from src.classes.stoppuhr import FlexibleZeit


class Zonen:
    def __init__(self):
        self.zonen = {}
        self.tachoWerte = {'dist': [0, 0, 0], 'zeit': [0, 0, 0], 'herz': [0, 0, 0]}
        self.daten = {}
        self.__pwm = 0

    def updateZone(self, pwm: int, zeit: FlexibleZeit, dist: int, herz: int = 0) -> None:
        lokale_zeit = zeit.als_s()
        self.updateTacho(lokale_zeit, dist, herz)
        if len(self.zonen.keys()) == 0:
            self.__pwm = pwm
        if pwm not in self.zonen.keys():
            self.zonen[pwm] = {'zeit': [0, lokale_zeit], 'dist': [0, dist], 'herz': [0, herz]}
        if self.__pwm == pwm:
            self.tachoWerte['zeit'][0] = lokale_zeit
            self.tachoWerte['dist'][0] = dist
            self.tachoWerte['herz'][0] = herz
        else:
            self.zonen[self.__pwm]['zeit'][0] += lokale_zeit - self.zonen[self.__pwm]['zeit'][1]
            self.zonen[self.__pwm]['dist'][0] += dist - self.zonen[self.__pwm]['dist'][1]
            self.zonen[self.__pwm]['herz'][0] += herz - self.zonen[self.__pwm]['herz'][1]
            if self.zonen[self.__pwm]['zeit'][0] == 0:
                self.zonen.pop(self.__pwm, None)
            self.zonen[pwm]['zeit'][1] = lokale_zeit
            self.zonen[pwm]['dist'][1] = dist
            self.zonen[pwm]['herz'][1] = herz
            self.__pwm = pwm

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

    def calcPowerGesamt(self):
        return sum(map(lambda a: a['all'], self.calcPowerProZone().values()))

    def calcPowerDurchschnitt(self):
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
