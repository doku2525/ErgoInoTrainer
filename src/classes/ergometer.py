from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional, TYPE_CHECKING

from src.classes.stoppuhr import FlexibleZeit
if TYPE_CHECKING:
    from src.classes.devicedatenmodell import DeviceDatenModell


def device_werte_distanze(device_werte: DeviceDatenModell | None) -> int:
    """Hilfsfunktion um None abzufangen am Start"""
    return device_werte.distanze if device_werte else 0


def device_werte_cad(device_werte: DeviceDatenModell | None) -> int:
    """Hilfsfunktion um None abzufangen am Start"""
    return device_werte.cad if device_werte else 0


@dataclass(frozen=True)
class Ergometer:
    bremse: int = 0
    distanze: int = 0
    max_anzahl_werte: int = 255
    device_werte: DeviceDatenModell | None = None
    cad_zeitenliste: list = field(default_factory=list)
    korrekturwerte_bremse: dict = field(default_factory=dict)
    im_pausen_modus: bool = field(default=False)
    distanze_waehrend_pause: int = 0
    cad_zeitenliste_waehrend_pause: list = field(default_factory=list)

    def setBremse(self, neuer_wert) -> Ergometer:
        return replace(self, bremse=min(max(neuer_wert, 0), 100))     # 0 <= x <= 100

    def korrigiere_bremswert(self, name: str | None = None, wert: int = 0) -> Ergometer:
        if name is None:
            return self.setBremse(wert)
        if not self.korrekturwerte_bremse:
            return replace(self, korrekturwerte_bremse={name: wert})
        return replace(self, korrekturwerte_bremse={name: wert} | {key: value + wert if key == name else value
                                                                   for key, value
                                                                   in self.korrekturwerte_bremse.items()})

    def loesche_bremswertkorrektur(self, name: str | None = '') -> Ergometer:
        """Um kein Loeschen aller Werte aus Faulheit, nicht None als default, sondern leerer String."""
        return replace(self, korrekturwerte_bremse={}) if name is None else replace(
            self,
            korrekturwerte_bremse={key: value for key, value in self.korrekturwerte_bremse.items() if name != key})

    def berechne_korigierten_bremswert(self, name: str = None, ausgangs_wert: int = 0) -> int:
        # Diese Funktion berechnet den eigentlich Wert, der ans Device gesendet wird
        return min(max(ausgangs_wert + self.korrekturwerte_bremse.get(name, 0), 0), 100)   # 0 <= x <= 100

    def bremseMinus(self, name: str | None = None) -> Ergometer:
        return self.korrigiere_bremswert(wert=self.bremse - 1 if name is None else -1, name=name)

    def bremseMinusMinus(self, name: str | None = None) -> Ergometer:
        return self.korrigiere_bremswert(wert=self.bremse - 5 if name is None else -5, name=name)

    def bremsePlus(self, name: str | None = None) -> Ergometer:
        return self.korrigiere_bremswert(wert=self.bremse + 1 if name is None else 1, name=name)

    def bremsePlusPlus(self, name: str | None = None) -> Ergometer:
        return self.korrigiere_bremswert(wert=self.bremse + 5 if name is None else 5, name=name)

    def lese_distance(self) -> int:
        return (self.distanze * self.max_anzahl_werte
                + device_werte_distanze(self.device_werte)
                - self.distanze_waehrend_pause)

    def lese_cadence(self) -> int:
        return device_werte_cad(self.device_werte)

    def calc_cad_durchschnitt(self, zeit_spanne_millis: int, komma_stellen: int = 0) -> float:
        wert = 0.000 if zeit_spanne_millis == 0 else self.lese_distance() * 60.0 * 1000 / zeit_spanne_millis
        return float(f"{wert:.{komma_stellen}f}")

    def calc_distanze_am_ende(self, dauer_absolviert_in_millis: int = 0, dauer_gesamt_in_millis: int = 0) -> int:
        return int(self.lese_distance() + (self.lese_cadence() *
                                           FlexibleZeit.create_from_millis(
                                               dauer_gesamt_in_millis - dauer_absolviert_in_millis).als_min()))

    def calc_power_index(self, bremse: int, komma_stellen: int = 2) -> float:
        # TODO Kein Test
        # TODO Urspruenglich self.lese_cadence() * self.bremse / 100, aber mit self.bremse hat nicht funktioniert
        wert = self.lese_cadence() * bremse / 100
        return float(f"{wert:.{komma_stellen}f}")

    # TODO Variablezeit_spanne_millis sieht ueberfluessig aus. Wird die gesamte Funktion ueberhaupt benutzt?
    def calc_power_index_durchschnitt(self, zeit_spanne_millis: int, komma_stellen: int = 2) -> float:
        # TODO Kein Test
        return float(f"{self.calc_power_index():.{komma_stellen}f}")

    def calc_power_watt(self, bremse: int) -> int:
        # TODO Kein Test
        # TODO Durch calc_power_index() beeinflusst. Sollte ohne Parameter fuktionieren.
        # Einen Powerindex von 34 habe ich als Wert fuer 200W festgelegt. Nur vom Gefuehl her.
        result = int(200 + ((self.calc_power_index(bremse) - 34) * 10))
        if result < 0:
            return 0
        else:
            return result

    def verarbeite_device_daten(self, neue_device_daten: DeviceDatenModell):
        # TODO Noch nicht vollstaendig implementiert
        # TODO Kein Test
        # TODO Funktion wird bisher nicht verwendet
        if hasattr(neue_device_daten, 'runtime_pro_tritte'):
            # TODO verarbeite das Datenfeld mit runtime_pro_tritte und fuege Elemente der Liste hinzu.
            self.update_cad_zeitenliste(zeiten=neue_device_daten.runtime_pro_tritte)
        self.update_device_werte(neue_device_daten=neue_device_daten)

    def update_device_werte(self, neue_device_daten: DeviceDatenModell, pause: bool = False) -> Ergometer:
        """Berechne Distanze und fuehre Logik fuer Pausenbehandlung aus. Rekursiv"""
        match (pause,
               self.im_pausen_modus,
               self.device_werte,
               int(neue_device_daten.distanze) < device_werte_distanze(self.device_werte)):
            case (True, _, _, _):       # Pause: Daten ignorieren, nur im_pausen_modus veraendern
                return replace(self, im_pausen_modus=pause)
            case (False, True, _, _):   # Pause wurde beendet, berechne Distanz waehrend Pause und pausen_modus = False
                return (replace(self,
                                im_pausen_modus=pause,
                                distanze_waehrend_pause=(self.distanze_waehrend_pause
                                                         + (neue_device_daten.distanze
                                                            - device_werte_distanze(self.device_werte))
                                                         % self.max_anzahl_werte)).
                        update_device_werte(neue_device_daten))     # Dann fuehre Funktion auf das neue Objekt aus.
            case (False, False, _, True):   # distanz in device_daten ist uebergelaufen, erhoehe distanz-Zahler
                return replace(self, distanze=self.distanze + 1, device_werte=neue_device_daten)
            case _:                         # Ersetze nur die alten Device_werte durch die Neuen
                return replace(self, device_werte=neue_device_daten)

    def update_cad_zeitenliste(self, zeiten: tuple[int, int, int, int]) -> Ergometer:
        # TODO Pausen-Funktionalitaet hinzufuegen
        # TODO Funktion wird bisher nicht aufgerufen
        set_mit_zeiten_ohne_nullen = set(zeiten) - {0}
        if neue_zeiten := sorted(set_mit_zeiten_ohne_nullen - set(self.cad_zeitenliste[-4:])):
            return replace(self, cad_zeitenliste=self.cad_zeitenliste[:] + neue_zeiten)
        return self
