from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, replace


class ZE(Enum):
    MS = 1
    SEK = 1000
    MIN = 1000*60
    H = 1000*60*60


@dataclass(frozen=True)
class FlexibleZeit:
    zeitspanne_in_ms: int = 0         # Zeitspanne in Millisekunden

    def __lt__(self, other: FlexibleZeit) -> bool:
        return self.zeitspanne_in_ms < other.zeitspanne_in_ms

    def __eq__(self, other: FlexibleZeit) -> bool:
        return self.zeitspanne_in_ms == other.zeitspanne_in_ms

    def __le__(self, other: FlexibleZeit) -> bool:
        return self.zeitspanne_in_ms <= other.zeitspanne_in_ms

    def __ne__(self, other: FlexibleZeit) -> bool:
        return self.zeitspanne_in_ms != other.zeitspanne_in_ms

    def __add__(self, other: FlexibleZeit) -> FlexibleZeit:
        return replace(self, zeitspanne_in_ms=self.zeitspanne_in_ms + other.zeitspanne_in_ms)

    def als(self, einheit: ZE) -> int | float:
        return self.zeitspanne_in_ms / einheit.value

    def als_ms(self) -> int:
        return self.zeitspanne_in_ms

    def als_s(self) -> int | float:
        return self.als(ZE.SEK)

    def als_min(self) -> int | float:
        return self.als(ZE.MIN)

    def als_h(self) -> int | float:
        return self.als(ZE.H)

    @classmethod
    def create_from_minuten(cls, zeit: int | float = 0) -> FlexibleZeit:
        return cls.create(minuten=zeit)

    @classmethod
    def create_from_sekunden(cls, zeit: int | float = 0) -> FlexibleZeit:
        return cls.create(sekunden=zeit)

    @classmethod
    def create_from_stunden(cls, zeit: int | float) -> FlexibleZeit:
        return cls.create(stunden=zeit)

    @classmethod
    def create_from_millis(cls, zeit: int | float) -> FlexibleZeit:
        return cls.create(millisekunden=int(zeit))

    @classmethod
    def create(cls, millisekunden: int | float = 0, sekunden: int | float = 0, minuten: int | float = 0,
               stunden: int | float = 0) -> FlexibleZeit:
        zeitspanne = None
        # !!! VORSICHT !!! vor Rechenfehlern by floats! Z.B. 1.001 * 1000 = 1000.9999999999999.
        # Deshalb Zahlen mit vielen Nachkommastellen moeglichst vermeiden. Es koennten unerwartet Ergbnisse auftreten!
        if millisekunden > 0 and zeitspanne is None:
            return cls(zeitspanne_in_ms=round(millisekunden))
        elif sekunden > 1 and zeitspanne is None:
            return cls(zeitspanne_in_ms=round(sekunden * 1000))
        elif minuten > 0 and zeitspanne is None:
            return cls(zeitspanne_in_ms=round(minuten * 60 * 1000))
        elif stunden > 0 and zeitspanne is None:
            return cls(zeitspanne_in_ms=round(stunden * 60 * 60 * 1000))
        else:
            return cls(zeitspanne_in_ms=0)


@dataclass(frozen=True)
class Stoppuhr:
    startzeit: int = 0
    pausenzeit: int = 0
    isPause: bool = True
    sekunden: int = 0
    alt: int = 0

    def pause(self, aktuelle_zeit: int) -> Stoppuhr:
        if not self.macht_pause():
            return replace(self, pausenzeit=aktuelle_zeit, isPause=True)
        return self

    def start(self, aktuelle_zeit: int) -> Stoppuhr:
        if self.macht_pause():
            pausen_laenge = aktuelle_zeit - self.pausenzeit
            return replace(self, startzeit=self.startzeit + pausen_laenge, isPause=False)
        return self

    def zeit(self, aktuelle_zeit: int) -> int:
        if self.macht_pause():
            pausen_laenge = aktuelle_zeit - self.pausenzeit
            return aktuelle_zeit - self.startzeit - pausen_laenge
        else:
            return aktuelle_zeit - self.startzeit

    def macht_pause(self) -> bool:
        return self.isPause

    def reset(self, aktuelle_zeit: int) -> Stoppuhr:
        if self.macht_pause():
            return replace(self, startzeit=aktuelle_zeit, pausenzeit=aktuelle_zeit)
        else:
            return replace(self, startzeit=aktuelle_zeit, pausenzeit=0)

    @classmethod
    def factory(cls, aktuelle_zeit: int) -> Stoppuhr:
        return cls(startzeit=aktuelle_zeit, pausenzeit=aktuelle_zeit, isPause=True, sekunden=0, alt=0)
