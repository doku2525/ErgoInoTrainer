from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import NewType, Callable


class BelastungTypen(Enum):
    Intervall = 1
    Erholung = 2
    G1 = 3
    G2 = 4
    K3 = 5


Trainingswerte = NewType("Trainingswerte", tuple[str, int, int])


@dataclass(frozen=True)
class Trainingsinhalt(ABC):
    name: str = field(default_factory=str)
    dauer_in_millis: int = field(default_factory=int)
    cad: int = field(default_factory=int)
    power: int = field(default_factory=int)
    typ: BelastungTypen = field(default_factory=BelastungTypen)
    logging: bool = field(default=True)

    @abstractmethod
    def dauer(self) -> int:
        pass

    @abstractmethod
    def distanze(self) -> int:
        pass

    @abstractmethod
    def berechne_werte(self, zeit: int) -> Trainingswerte:
        pass


@dataclass(frozen=True)
class Dauermethode(Trainingsinhalt):

    def dauer(self) -> int:
        return self.dauer_in_millis

    def distanze(self) -> int:
        return int(self.dauer_in_millis * self.cad / 60000)

    def berechne_werte(self, zeit: int) -> Trainingswerte:
        return Trainingswerte((self.name, self.power, self.cad))


@dataclass(frozen=True)
class Funktionsmethode(Trainingsinhalt):

    def dauer(self) -> int:
        return self.dauer_in_millis

    def distanze(self) -> int:
        pass

    def berechne_werte(self, zeit: int) -> Trainingswerte:
        return Trainingswerte((self.name, self.power(zeit), self.cad(zeit)))
