from unittest import TestCase
from src.classes.zonen import Zonen, Tachowerte
from src.classes.stoppuhr import FlexibleZeit

class test_Zonen(TestCase):

    def setUp(self):
        self.test_zonen = (Zonen().updateZone(0.3, FlexibleZeit.create_from_sekunden(0), 0, 0).
                           updateZone(0.6, FlexibleZeit.create_from_sekunden(60), 100, 120).
                           updateZone(0.3, FlexibleZeit.create_from_sekunden(120), 150, 300).
                           updateZone(0.6, FlexibleZeit.create_from_sekunden(180), 250, 420))

    def test_tacho_werte(self):
        werte = Tachowerte()
        self.assertEqual(0, werte.zeit)
        self.assertEqual(0, werte.dist)
        self.assertEqual(0, werte.herz)
        werte = Tachowerte(100, 200, 1)
        self.assertEqual(200, werte.zeit)
        self.assertEqual(100, werte.dist)
        self.assertEqual(1, werte.herz)
        werte = Tachowerte(herz=100)
        self.assertEqual(0, werte.zeit)
        self.assertEqual(0, werte.dist)
        self.assertEqual(100, werte.herz)
        werte = Tachowerte(herz=100, dist=200, zeit=1)
        self.assertEqual(1, werte.zeit)
        self.assertEqual(200, werte.dist)
        self.assertEqual(100, werte.herz)
        werte = Tachowerte(herz=100, dist=200, zeit=1) - Tachowerte(herz=50, dist=100, zeit=1)
        self.assertEqual(0, werte.zeit)
        self.assertEqual(100, werte.dist)
        self.assertEqual(50, werte.herz)
        werte = Tachowerte(herz=100, dist=200, zeit=1) + Tachowerte(herz=50, dist=100, zeit=1)
        self.assertEqual(2, werte.zeit)
        self.assertEqual(300, werte.dist)
        self.assertEqual(150, werte.herz)
        werte += Tachowerte(herz=100, dist=200, zeit=1)
        self.assertEqual(3, werte.zeit)
        self.assertEqual(500, werte.dist)
        self.assertEqual(250, werte.herz)

    def test_update_zone(self):
        zonen = Zonen().updateZone(0.0, FlexibleZeit.create_from_sekunden(0), 0, 0)
        self.assertEqual(0, zonen.zonen[0.0].gesamt.dist)
        self.assertEqual(0, zonen.zonen[0.0].gesamt.herz)
        self.assertEqual(0, zonen.zonen[0.0].neuer_calc_punkt.dist)
        self.assertEqual(0, zonen.zonen[0.0].neuer_calc_punkt.herz)
        zonen = Zonen().updateZone(0.1, FlexibleZeit.create_from_sekunden(0), 0, 0)
        self.assertEqual(0, zonen.zonen[0.1].gesamt.dist)
        self.assertEqual(0, zonen.zonen[0.1].gesamt.herz)
        self.assertEqual(0, zonen.zonen[0.1].neuer_calc_punkt.dist)
        self.assertEqual(0, zonen.zonen[0.1].neuer_calc_punkt.herz)
        zonen = zonen.updateZone(0.2, FlexibleZeit.create_from_sekunden(20), 200, 100)
        self.assertEqual(200, zonen.zonen[0.1].gesamt.dist)
        self.assertEqual(100, zonen.zonen[0.1].gesamt.herz)
        self.assertEqual(200, zonen.zonen[0.1].neuer_calc_punkt.dist)
        self.assertEqual(100, zonen.zonen[0.1].neuer_calc_punkt.herz)
        self.assertEqual(0, zonen.zonen[0.2].gesamt.dist)
        self.assertEqual(0, zonen.zonen[0.2].gesamt.herz)
        self.assertEqual(200, zonen.zonen[0.2].neuer_calc_punkt.dist)
        self.assertEqual(100, zonen.zonen[0.2].neuer_calc_punkt.herz)
        zonen = zonen.updateZone(0.1, FlexibleZeit.create_from_sekunden(30), 250, 150)
        self.assertEqual(200, zonen.zonen[0.1].gesamt.dist)
        self.assertEqual(100, zonen.zonen[0.1].gesamt.herz)
        self.assertEqual(250, zonen.zonen[0.1].neuer_calc_punkt.dist)
        self.assertEqual(150, zonen.zonen[0.1].neuer_calc_punkt.herz)
        self.assertEqual(50, zonen.zonen[0.2].gesamt.dist)
        self.assertEqual(50, zonen.zonen[0.2].gesamt.herz)
        self.assertEqual(200, zonen.zonen[0.2].neuer_calc_punkt.dist)
        self.assertEqual(100, zonen.zonen[0.2].neuer_calc_punkt.herz)

    def test_calc_werte_pro_zone(self):
        result = self.test_zonen.calcWerteProZone()
        self.assertEqual(2 * 60, result[0.3]['zeit'])
        self.assertEqual(2 * 100, result[0.3]['dist'])
        self.assertEqual(2 * 120, result[0.3]['herz'])
        self.assertEqual(100, result[0.3]['cad'])
        self.assertEqual(120, result[0.3]['bpm'])
        self.assertEqual(1 * 60, result[0.6]['zeit'])
        self.assertEqual(1 * 50, result[0.6]['dist'])
        self.assertEqual(1 * 180, result[0.6]['herz'])
        self.assertEqual(50, result[0.6]['cad'])
        self.assertEqual(180, result[0.6]['bpm'])

    def test_calc_power_pro_zone(self):
        result = self.test_zonen.calcPowerProZone()
        self.assertEqual(0.3*2*100, result[0.3]['all'], "Powerindex accumuliert")
        self.assertEqual(0.3*100, result[0.3]['dur'], "Powerindex / Minute")
        self.assertEqual(0.6*1*50, result[0.6]['all'], "Powerindex accumuliert")
        self.assertEqual(0.6*50, result[0.6]['dur'], "Powerindex / Minute")

    def test_calc_power_gesamt(self):
        result = self.test_zonen.calcPowerGesamt()
        self.assertEqual(0.3 * 2 * 100 + 0.6 * 1 * 50, result)

    def test_calc_power_durchschnitt(self):
        result = self.test_zonen.calcPowerDurchschnitt()
        self.assertEqual((0.3 * 2 * 100 + 0.6 * 1 * 50) / 3, result)

    def test_merge_werte_and_power(self):
        # merge_werte_and_powerist eigentlich nur calcWerteProZone() + calcPowerProZone()
        result = self.test_zonen.mergeWerteAndPower()
        # Tests einfach von obigen tests kopiert.
        self.assertEqual(2 * 60, result[0.3]['zeit'])
        self.assertEqual(2 * 100, result[0.3]['dist'])
        self.assertEqual(2 * 120, result[0.3]['herz'])
        self.assertEqual(100, result[0.3]['cad'])
        self.assertEqual(120, result[0.3]['bpm'])
        self.assertEqual(1 * 60, result[0.6]['zeit'])
        self.assertEqual(1 * 50, result[0.6]['dist'])
        self.assertEqual(1 * 180, result[0.6]['herz'])
        self.assertEqual(50, result[0.6]['cad'])
        self.assertEqual(180, result[0.6]['bpm'])
        self.assertEqual(0.3*2*100, result[0.3]['all'], "Powerindex accumuliert")
        self.assertEqual(0.3*100, result[0.3]['dur'], "Powerindex / Minute")
        self.assertEqual(0.6*1*50, result[0.6]['all'], "Powerindex accumuliert")
        self.assertEqual(0.6*50, result[0.6]['dur'], "Powerindex / Minute")
