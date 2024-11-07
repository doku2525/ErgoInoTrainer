from abc import ABC, abstractmethod
from enum import Enum
from typing import NewType, Callable


class BelastungTypen(Enum):
    Intervall = 1
    Erholung = 2
    G1 = 3
    G2 = 4
    K3 = 5


Trainingswerte = NewType("Trainingswerte", tuple[str, int, int])


class Trainingsinhalt(ABC):
    @abstractmethod
    def dauer(self) -> int:
        pass

    @abstractmethod
    def distanze(self) -> int:
        pass

    @abstractmethod
    def berechne_werte(self, zeit: int) -> Trainingswerte:
        pass


class Dauermethode(Trainingsinhalt):
    def __init__(self, name: str, dauer_in_millis: int, cad: int, power: int, typ: BelastungTypen):
        self.name = name
        self.dauer_in_millis = dauer_in_millis
        self.cad = cad
        self.power = power
        self.type = typ

    def dauer(self) -> int:
        return self.dauer_in_millis

    def distanze(self) -> int:
        return int(self.dauer_in_millis * self.cad / 60000)

    def berechne_werte(self, zeit: int) -> Trainingswerte:
        return Trainingswerte((self.name, self.power, self.cad))


class Funktionsmethode(Trainingsinhalt):
    def __init__(self, name: str, dauer_in_millis: int, cad: Callable[[int], int], power: Callable[[int], int],
                 typ: BelastungTypen):
        self.name = name
        self.dauer_in_millis = dauer_in_millis
        self.cad = cad
        self.power = power
        self.belastung = belastung

    def dauer(self) -> int:
        return self.dauer_in_millis

    def distanze(self) -> int:
        pass

    def berechne_werte(self, zeit: int) -> Trainingswerte:
        return Trainingswerte((self.name, self.power(zeit), self.cad(zeit)))
