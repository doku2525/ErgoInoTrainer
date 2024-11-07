# import bangla
import pygame

from viewdatenmodell import ViewDatenModell


class ApplikationView:

    farbe_rot = (255, 0, 0)
    farbe_gruen = (0, 255, 0)
    farbe_schwarz = (0, 0, 0)
    farbe_weiss = (255, 255, 255)

    def __init__(self, breite: int = 760, hoehe: int = 455):
        pygame.init()
        self.hoehe = hoehe
        self.breite = breite
        self._screen = pygame.display.set_mode((breite, hoehe))
        self._font = pygame.font.SysFont("Arial", 24)
        self._screen.fill(self.farbe_weiss)
        self.daten = ViewDatenModell()
        self._text_farbe = self.farbe_gruen

    def draw_daten(self) -> None:
        self._screen.fill(self.farbe_weiss)
        for elem in self.build_elements():
            self.draw_element(elem)
        pygame.display.flip()

    def draw_element(self, element) -> None:
        (size, text, farbe, position) = element
        self._font = pygame.font.SysFont(None, size)
        if farbe:
            elem = self._font.render("{0}".format(text), True, farbe)
        else:
            elem = self._font.render("{0}".format(text), True, self._text_farbe)
        self._screen.blit(elem, position)

    def build_elements(self) -> list[list[int, str, (int, int, int), (int, int)]]:
        screen_hoehe = self.hoehe
        screen_breite = self.breite
        tmp = [(80, "{0}".format(self.daten.zeit_gesamt), False, (10, 5)),
           (120, self.daten.anzahl_fertige_sets, False, (10, 96 - 30)),
           (318, self.daten.zeit_timer, self.daten.intervall_farbe, (120 + 2, 96 - 50)),
           (170, "{: >3}".format(self.daten.herz_frequenz), False, (290, 315)),
           (36, self.daten.herz_durchschnitt, False, (350, screen_hoehe - 29)),
           (36, self.daten.herz_gesamt, False, (405, screen_hoehe - 29)),
           (36, self.daten.herz_batterielevel, False, (310, screen_hoehe - 31)),
           (96, "{0}".format(self.daten.zeit_timer_string), self.daten.intervall_farbe, (200 + 15, 320 - 70)),
           (80, "{:.2f}".format(self.daten.pwm_wert), self.daten.intervall_farbe, (screen_breite - 510, 5)),
           (170, "{: >3}".format(self.daten.cad_frequenz), (0, 0, 255), (95, 315)),
           (72, "{: >5}".format(self.daten.cad_durchschnitt), (0, 0, 255), (80, 320 - 50)),
           (92, "{: >4}".format(self.daten.power_aktuell), (0, 0, 255), (screen_breite - 280, 315)),
           (42, "{: >5}".format("{:.2f}".format(self.daten.power_durchschnitt)), (0, 0, 255), (screen_breite - 238,
                                                                                               315 + 60)),
           (42, "{: >5}".format(int(self.daten.power_gesamt)), (0, 0, 255), (screen_breite - 238, screen_hoehe - 52)),
           (42, "{: >3}W".format(self.daten.power_watt), (0, 0, 255), (screen_breite - 238, screen_hoehe - 31)),
           (60, self.daten.cad_aktuell, self.farbe_schwarz, (10, screen_hoehe - 75)),
           (80, self.daten.cad_differenz, self.farbe_schwarz, (10, screen_hoehe - 135)),
           (40, self.daten.cad_count, self.farbe_schwarz, (20, screen_hoehe - 31)),
           (40, self.daten.distanze, self.farbe_schwarz, (90, screen_hoehe - 31)),
           # (36, "{0} {1}".format(self.daten.distanze_am_ziel, calcCADFuerZiel()), self.farbe_schwarz, (160, screen_hoehe - 31)),
           (36, "{0} {1}".format(self.daten.distanze_am_ziel, 0), self.farbe_schwarz, (160, screen_hoehe - 31)),

           (80, self.daten.intervall_cad, False, (10, 96 + 45)),
           (40, self.daten.intervall_distanze, False, (10, 96 + 100)),
           (80, self.daten.intervall_zeit, False, (10, 200 + 25)),
           (40, self.daten.intervall_herz, False, (10, 200 + 80)),
           (32, "Intervall {0}".format(self.daten.intervall_zeit), self.farbe_rot, (screen_breite - 145,
                                                                                    screen_hoehe - 28)),
           (32, "Pause {0}".format(""), self.farbe_gruen, (screen_breite - 145, screen_hoehe - 54)),
           (32, "Sets {0}".format(self.daten.anzahl_sets), self.farbe_schwarz, (screen_breite - 145,
                                                                                screen_hoehe - 80)),
           (32, "Ziel {0}".format(8), self.farbe_schwarz, (screen_breite - 145, screen_hoehe - 106))]
        index = 0
        werte = self.daten.werte_und_power
        if type(werte) == int:
            werte = {}
        for key in sorted(werte.keys()):
            tmp.append((22, "{0}{1}{2}{3}".format(
                "{:.2f}".format(key),
                "{: >5}".format(werte[key]['dist']),
                "{: >5}".format(werte[key]['herz']),
                "{: >6}".format(int(werte[key]['all']))),
                        False, (screen_breite - 360, 1 + (index * 14))))
            index += 1
            tmp.append((22, "{0}{1}{2}{3}".format(
                "{: >6}".format(" "),
                "{: >5}".format("{:.1f}".format(werte[key]['cad'] % 100)),
                "{: >5}".format("{:.1f}".format(werte[key]['bpm'] % 100)),
                "{: >6}".format("{:.2f}".format(werte[key]['dur']))),
                        False, (screen_breite - 360, 1 + (index * 14))))
            index += 1
        for index in range(len(self.daten.intervall_tabelle)):
            tmp.append((26,
                       "{: >3}".format(self.daten.intervall_tabelle[index][0]),
                        self.daten.intervall_tabelle[index][4], (screen_breite - 182, 1 + (index * 17))))
            tmp.append((26,
                        "{: >4}".format(self.daten.intervall_tabelle[index][1]),
                        self.daten.intervall_tabelle[index][4], (screen_breite - 143, 1 + (index * 17))))
            tmp.append((26,
                        "{: >3}".format(self.daten.intervall_tabelle[index][2]),
                        self.daten.intervall_tabelle[index][4], (screen_breite - 91, 1 + (index * 17))))
            tmp.append((26,
                        "{: >4}".format(self.daten.intervall_tabelle[index][3]),
                        self.daten.intervall_tabelle[index][4], (screen_breite - 52, 1 + (index * 17))))
        return tmp
