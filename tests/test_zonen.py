from unittest import TestCase
from src.classes.zonen import Zonen
from src.classes.stoppuhr import FlexibleZeit

class test_Zonen(TestCase):

    def test_update_zone(self):
        zonen = Zonen()
        zonen.updateZone(0.1, FlexibleZeit.create_from_sekunden(0), 0, 0)
        self.assertEqual(0, zonen.zonen[0.1]['dist'][0])
        self.assertEqual(0, zonen.zonen[0.1]['herz'][0])
        self.assertEqual(0, zonen.zonen[0.1]['dist'][1])
        self.assertEqual(0, zonen.zonen[0.1]['herz'][1])
        zonen.updateZone(0.2, FlexibleZeit.create_from_sekunden(20), 200, 100)
        self.assertEqual(200, zonen.zonen[0.1]['dist'][0])
        self.assertEqual(100, zonen.zonen[0.1]['herz'][0])
        self.assertEqual(0, zonen.zonen[0.1]['dist'][1])
        self.assertEqual(0, zonen.zonen[0.1]['herz'][1])
        self.assertEqual(0, zonen.zonen[0.2]['dist'][0])
        self.assertEqual(0, zonen.zonen[0.2]['herz'][0])
        self.assertEqual(200, zonen.zonen[0.2]['dist'][1])
        self.assertEqual(100, zonen.zonen[0.2]['herz'][1])
        zonen.updateZone(0.1, FlexibleZeit.create_from_sekunden(30), 250, 150)
        self.assertEqual(200, zonen.zonen[0.1]['dist'][0])
        self.assertEqual(100, zonen.zonen[0.1]['herz'][0])
        self.assertEqual(250, zonen.zonen[0.1]['dist'][1])
        self.assertEqual(150, zonen.zonen[0.1]['herz'][1])
        self.assertEqual(50, zonen.zonen[0.2]['dist'][0])
        self.assertEqual(50, zonen.zonen[0.2]['herz'][0])
        self.assertEqual(200, zonen.zonen[0.2]['dist'][1])
        self.assertEqual(100, zonen.zonen[0.2]['herz'][1])

    def test_update_tacho(self):
        assert True

    def test_calc_werte_pro_zone(self):
        zonen = Zonen()
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(0), 0, 0)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(60), 100, 120)
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(120), 150, 300)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(180), 250, 420)
        result = zonen.calcWerteProZone()
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
        zonen = Zonen()
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(0), 0, 0)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(60), 100, 120)
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(120), 150, 300)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(180), 250, 420)
        result = zonen.calcPowerProZone()
        self.assertEqual(0.3*2*100, result[0.3]['all'], "Powerindex accumuliert")
        self.assertEqual(0.3*100, result[0.3]['dur'], "Powerindex / Minute")
        self.assertEqual(0.6*1*50, result[0.6]['all'], "Powerindex accumuliert")
        self.assertEqual(0.6*50, result[0.6]['dur'], "Powerindex / Minute")


    def test_calc_power_gesamt(self):
        zonen = Zonen()
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(0), 0, 0)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(60), 100, 120)
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(120), 150, 300)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(180), 250, 420)
        result = zonen.calcPowerGesamt()
        self.assertEqual(0.3 * 2 * 100 + 0.6 * 1 * 50, result)

    def test_calc_power_durchschnitt(self):
        zonen = Zonen()
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(0), 0, 0)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(60), 100, 120)
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(120), 150, 300)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(180), 250, 420)
        result = zonen.calcPowerDurchschnitt()
        self.assertEqual((0.3 * 2 * 100 + 0.6 * 1 * 50) / 3, result)

    def test_merge_werte_and_power(self):
        # merge_werte_and_powerist eigentlich nur calcWerteProZone() + calcPowerProZone()
        zonen = Zonen()
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(0), 0, 0)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(60), 100, 120)
        zonen.updateZone(0.3, FlexibleZeit.create_from_sekunden(120), 150, 300)
        zonen.updateZone(0.6, FlexibleZeit.create_from_sekunden(180), 250, 420)
        result = zonen.mergeWerteAndPower()
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

