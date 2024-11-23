from unittest import TestCase
from src.classes.pulsmesser import Pulsmesser
from src.classes.bledevice import BLEHeartRateData

class test_Pulsmesser(TestCase):

    def test_initialization(self):
        obj = Pulsmesser()
        self.assertEqual(0, obj.herzfrequenz)
        self.assertEqual(0, obj.herzschlaege)
        self.assertEqual((), obj.rr_intervall)

    def test_verarbeite_device_werte(self):
        obj = Pulsmesser()
        device_data = BLEHeartRateData(16, 120, [500, 500])
        obj = obj.verarbeite_device_werte(device_data)
        self.assertEqual(120, obj.herzfrequenz)
        self.assertEqual(2, obj.herzschlaege)
        self.assertEqual((500, 500), obj.rr_intervall)
        obj = obj.verarbeite_device_werte(device_data)
        self.assertEqual(120, obj.herzfrequenz)
        self.assertEqual(4, obj.herzschlaege)
        self.assertEqual((500, 500)*2, obj.rr_intervall)
        device_data = BLEHeartRateData(16, 40, [])
        obj = obj.verarbeite_device_werte(device_data)
        self.assertEqual(40, obj.herzfrequenz)
        self.assertEqual(4, obj.herzschlaege)
        self.assertEqual((500, 500)*2, obj.rr_intervall)
        device_data = BLEHeartRateData(16, 60, [1000])
        obj = obj.verarbeite_device_werte(device_data)
        self.assertEqual(60, obj.herzfrequenz)
        self.assertEqual(5, obj.herzschlaege)
        self.assertEqual(((500, 500) * 2) + (1000,), obj.rr_intervall)

    def test_calc_puls_durchschnitt(self):
        obj = Pulsmesser(herzschlaege=60, herzfrequenz=120, rr_intervall=tuple(range(60)))
        self.assertEqual(0, obj.calc_puls_durchschnitt(0))
        obj = Pulsmesser(herzschlaege=60, herzfrequenz=120, rr_intervall=tuple(range(60)))
        self.assertEqual(120, obj.calc_puls_durchschnitt(30_000))
        obj = Pulsmesser(herzschlaege=59, herzfrequenz=120, rr_intervall=tuple(range(59)))
        self.assertEqual(118, obj.calc_puls_durchschnitt(30_000))
        obj = Pulsmesser(herzschlaege=479, herzfrequenz=120, rr_intervall=tuple(range(479)))
        self.assertEqual(120, obj.calc_puls_durchschnitt(240_000))
        obj = Pulsmesser(herzschlaege=481, herzfrequenz=120, rr_intervall=tuple(range(481)))
        self.assertEqual(120, obj.calc_puls_durchschnitt(240_000))