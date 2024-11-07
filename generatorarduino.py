from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import copy


sekunden_pro_minute = 60


@dataclass(frozen=True)
class GeneratorArduino:
    cad: int = field(default=0)
    dist: int = field(default=0)
    start_punkt: int = field(default=0)
    messwerte: list[int] = field(default_factory=list)
    position: int = field(default=0)
    anzahl_messwerte: int = field(default=4)

    def simuliere_fahrt(self, zeit_dauer: int, cad: int = None) -> GeneratorArduino:
        pass

    def berechne_distanze(self, zeitdauer: int) -> int:
        return int(zeitdauer / sekunden_pro_minute * self.cad)

    def erzeuge_messwerte(self, zeitdauer: int) -> list[float]:
        if not self.sekunden_pro_umdrehung():
            return []
        return [(x+1) * self.sekunden_pro_umdrehung() for x in range(self.berechne_distanze(zeitdauer))]

    def sekunden_pro_umdrehung(self) -> float:
        return sekunden_pro_minute / self.cad if not self.cad == 0 else None

    def berechne_zeiger_position(self, zeitdauer: int) -> int:
        # Berechne die aktueller Position in der Liste, in die der letzte Messwert geschrieben werden muss.
        if zeitdauer == 0:
            return self.position
        return (self.berechne_distanze(zeitdauer) - 1 + self.position) % self.anzahl_messwerte

    def konvertiere_liste_zu_slot(self, liste: list[Any], slot: list[Any, Any, Any, Any], position: int) -> list[Any, Any, Any, Any]:
        def build_slots(pos: int) -> list[int]:
            index = list(reversed([x % 4 for x in range(10)])).index(pos)
            return list(reversed([x % 4 for x in range(10)]))[index:index+4]

        if not liste: return slot
        slot_indices = build_slots(position)
        # zipped_data = sorted((list(zip( slot_indices, reversed(liste[-4:])))),key=lambda tupel: tupel[0])
        zipped_data = zip( slot_indices, reversed( liste[-4:]))
        print(list(zipped_data))
        # return [value if index in slot_indices else old_value
        #         for old_value in slot
        #         for index, (slot_index, value) in enumerate(zipped_data)]
        slot_liste = list(slot)
        for index, element in zipped_data:
            slot_liste[index] = element

        return slot_liste