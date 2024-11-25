from __future__ import annotations
from dataclasses import dataclass, field
import json
import os


@dataclass(frozen=True)
class AudioObjekt:
    filename: str = ''                                          # Z.B. tabata.mp3
    trainingsplan: list[str] = field(default_factory=list)      # Bei welchen Traingsprogramm.name ausfuehren
    trainingsinhalt: list[str] = field(default_factory=list)    # Bei welchem Trainingsinhalt.name ausfuehren
    zeit_start: int = 0                                         # Startzeit (z.B. auch -10s, wenn vor dem Inhalt
    dauer: int = 0                                              # Wann beenden 0 = ausspielen lassen
    prioritaet: tuple[int, int] = field(default_factory=tuple)   # Bei hoher Prioritaet werden andere AudObj gestoppt
    loops: int = 0

# TODO Der Wert fuer dauer sollte evtl. die laenge der Audiodatei beinhalten? Zur Zeit wird die Audiodatei
#   solange wiederholt, bis dauer erreicht wurde.
# TODO Oder noch ein Attribut datei_laenge_in_ms hinzufuegen.


# Funktion zum Laden einer Liste von AudioObjekten aus einer JSON-Datei
def load_audio_objekte(json_file: str) -> list[AudioObjekt]:
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            data = json.load(f)
            return [AudioObjekt(**obj) for obj in data]
    else:
        # Wenn die Datei nicht existiert, gib leere Liste zurück oder handle den Fehler anders
        return []


def save_audio_objekte(json_file: str, liste_mit_objekten: list[AudioObjekt]):
    with open(json_file, 'w') as file:
        data = [obj.__dict__ for obj in liste_mit_objekten]
        json.dump(data, file, indent=4)
