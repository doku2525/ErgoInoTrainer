import trainingsinhalt
from trainingsinhalt import Trainingsinhalt


class Trainingsprogramm:
    def __init__(self, name: str, inhalte: list[Trainingsinhalt], ergebnisse: list = None, unendlich: bool = True):
        self.name = name
        self.inhalte = inhalte  # Liste von Phase-Objekten
        self.ergebnisse = [] if ergebnisse is None else ergebnisse
        self.unendlich = unendlich  # FALSE = Beende die Ausfuehrung nach erreichen der Gesamttrainingszeit

    # TODO self.unendlich wird noch nicht benutzt
    def fuehre_aus(self, zeit_in_ms: int) -> Trainingsinhalt:
        return self.inhalte[self.finde_index_des_aktuellen_inhalts(zeit_in_ms)]

    def verarbeite_messwerte(self, zeit_in_ms: int, distanze: int) -> list:
        # TODO Fuer funktionalen Stil nicht die Variable veraendern und die Liste senden,
        #   sondern neues Objekt mit veraenderter Liste senden.
        if self.finde_index_des_aktuellen_inhalts(zeit_in_ms) > len(self.ergebnisse)-1:
            self.ergebnisse = self.ergebnisse + [distanze]
        else:
            self.ergebnisse = self.ergebnisse[0:-1] + [distanze]
        return self.ergebnisse

    def berechne_distanze_pro_fertige_inhalte(self) -> list:
        if self.ergebnisse == []:
            return self.ergebnisse
        if len(self.ergebnisse) == 1:
            return self.ergebnisse[1:]
        else:
            return self.ergebnisse[:1] + [zweiter_wert - erster_wert
                                          for erster_wert, zweiter_wert
                                          in zip(self.ergebnisse, self.ergebnisse[1:])][:-1]

    def berechne_distanze_aktueller_inhalt(self) -> int:
        result = self.ergebnisse[-2:]
        if not result:
            return 0
        if len(result) == 1:
            return result[0]
        return result[1] - result[0]    # Fuer komplette Kurbelumdrehnungen im aktuellen Zeitfenster muss result[0] + 1 gerechnet werden

    def fuehre_naechstes_aus(self, zeit_in_ms: int) -> Trainingsinhalt:
        if rest_liste := self.inhalte[self.finde_index_des_aktuellen_inhalts(zeit_in_ms) + 1:]:
            return rest_liste[0]
        else:
            return self.inhalte[self.finde_index_des_aktuellen_inhalts(zeit_in_ms)]

    def trainingszeit_dauer_gesamt(self) -> int:
        return sum([element.dauer() for element in self.inhalte])

    def trainingszeit_rest_gesamt(self, zeit_in_ms: int) -> int:
        return self.trainingszeit_dauer_gesamt() - zeit_in_ms

    def trainingszeit_dauer_aktueller_inhalt(self, zeit_in_ms: int) -> int:
        return zeit_in_ms - self.trainingszeit_beendeter_inhalte(zeit_in_ms)

    def trainingszeit_beendeter_inhalte(self, zeit_in_ms: int) -> int:
        aktueller_index = self.finde_index_des_aktuellen_inhalts(zeit_in_ms)
        return sum([element.dauer() for element in self.inhalte[:aktueller_index]])

    def berechne_distanze_gesamt(self) -> int:
        print(f"{self.inhalte}")
        return sum([element.distanze() for element in self.inhalte])

    def finde_index_des_aktuellen_inhalts(self, zeit_in_ms: int) -> int:
        # 0 <= result < len(self.inhalte), also das erste Element liefert 0
        def suche_rekursiv(liste: tuple[Trainingsinhalt], zeit_tmp: int) -> int:
            if not liste:
                return -1
            if liste[0].dauer() > zeit_tmp:
                return 0
            if liste[0].dauer() == zeit_tmp:
                return 0
            if liste[0].dauer() < zeit_tmp:
                return 1 + suche_rekursiv(liste[1:], zeit_tmp - liste[0].dauer())

        return suche_rekursiv(tuple(self.inhalte), zeit_in_ms)


def erzeuge_trainingsprogramm_G1(dauer_in_minuten: int, pwm: int, cad: int,
                                 block_groesse: int = 5) -> Trainingsprogramm:
    plan = [trainingsinhalt.Dauermethode("G1", block_groesse * 60 * 1000, cad, pwm,
                                         trainingsinhalt.BelastungTypen.G1)
            for _ in range(int(dauer_in_minuten/block_groesse))]
    return Trainingsprogramm("G1", plan)


def erzeuge_trainingsprogramm_G2Intervall(pwm: tuple[int, int], cad: tuple[int, int], warmfahrzeit: int = 10,
                                          ausfahrzeit: int = 5, wiederholungen: int = 6) -> Trainingsprogramm:
    warmfahren = [
        trainingsinhalt.Dauermethode("Warmfahren", warmfahrzeit * 60 * 1000, cad[0], pwm[0],
                                     trainingsinhalt.BelastungTypen.G1),
    ]
    intervall = intervall_builder(dauer=(4, 1), pwm=pwm, cad=cad, name=("Pause", "Intervall"),
                                  wiederholungen=wiederholungen)
    ausfahren = [
        trainingsinhalt.Dauermethode("Ausfahren", ausfahrzeit * 60 * 1000, cad[0], pwm[0],
                                     trainingsinhalt.BelastungTypen.G1)
    ]
    return Trainingsprogramm("G2Intervall", warmfahren + intervall + ausfahren)


def erzeuge_trainingsprogramm_Tabata(pwm: tuple[int, int], cad: tuple[int, int], warmfahrzeit: int | float = 10,
                                     ausfahrzeit: int | float = 6) -> Trainingsprogramm:
    zeit_pause = 10 / 60
    zeit_intervall = 20 / 60
    to_millis = 60 * 1000

    warmfahren = [
        trainingsinhalt.Dauermethode("Warmfahren", warmfahrzeit * to_millis, cad[0], pwm[0],
                                     trainingsinhalt.BelastungTypen.G1),
    ]
    intervall = intervall_builder(dauer=(zeit_pause, zeit_intervall), pwm=pwm, cad=cad, name=("Pause", "Intervall"),
                                  wiederholungen=8)
    ausfahren = [
        trainingsinhalt.Dauermethode("Ausfahren", ausfahrzeit * to_millis, cad[0], pwm[0],
                                     trainingsinhalt.BelastungTypen.G1)
    ]
    return Trainingsprogramm("Tabata", warmfahren + intervall + ausfahren)


def erzeuge_trainingsprogramm_G1_mit_sprints(pwm: tuple[int, int], cad: tuple[int, int], warmfahrzeit: int = 10,
                                             dauer_in_minuten: int = 90, block_groesse: int = 5,
                                             sprints: int = 4) -> Trainingsprogramm:
    zeit_pause = 4.75
    zeit_intervall = 0.25
    set_zeit = zeit_pause + zeit_intervall

    grundlage_vor = [trainingsinhalt.Dauermethode("G1", 5 * 60 * 1000, cad[0], pwm[0],
                                                  trainingsinhalt.BelastungTypen.G1)
                     for _ in range(int(warmfahrzeit / block_groesse))]
    intervall = intervall_builder(dauer=(zeit_pause, zeit_intervall), pwm=pwm, cad=cad, name=("Pause", "Intervall"),
                                  wiederholungen=sprints)
    grundlage_danach = [trainingsinhalt.Dauermethode("G1", 5 * 60 * 1000, cad[0], pwm[0],
                                                     trainingsinhalt.BelastungTypen.G1)
                        for _
                        in range(int((dauer_in_minuten - warmfahrzeit - set_zeit * sprints) / block_groesse))]
    return Trainingsprogramm("G1 mit 15sek Sprints", grundlage_vor + intervall + grundlage_danach)


def intervall_builder(dauer: (int, int), pwm: (int, int), cad: (int, int), name: (str, str),
                      wiederholungen: int, ohne_letzte_pause=False) -> list[Trainingsinhalt]:
    intervall = trainingsinhalt.Dauermethode(name[1], dauer[1] * 60 * 1000, cad[1], pwm[1],
                                             trainingsinhalt.BelastungTypen.Intervall)
    pause = trainingsinhalt.Dauermethode(name[0], dauer[0] * 60 * 1000, cad[0], pwm[0],
                                         trainingsinhalt.BelastungTypen.G1)
    result = [intervall if not index % 2 else pause for index in range(wiederholungen*2)]
    return result[:-1] if ohne_letzte_pause else result
