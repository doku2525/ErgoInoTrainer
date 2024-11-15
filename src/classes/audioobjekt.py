from dataclasses import dataclass, field


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