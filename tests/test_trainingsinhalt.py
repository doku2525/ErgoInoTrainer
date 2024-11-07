from unittest import TestCase

from trainingsinhalt import Trainingsinhalt, BelastungTypen, Dauermethode, Trainingswerte, Funktionsmethode

class test_Trainingsinhalt(TestCase):
    def setUp(self):
        self.parameter = {
            "dauer" : {"dauer_in_millis": 10000, "typ": BelastungTypen.Intervall, "cad": 100, "power": 40, "name": "G1"},
            "distanze_test": {"dauer_in_millis": 10*60000, "typ": BelastungTypen.Intervall, "cad": 100, "power": 40, "name": "G1"},
            "funk": {"dauer_in_millis": 10000, "typ": BelastungTypen.Intervall, "cad": lambda x: x * 2, "power": lambda x: x + 2, "name": "G1"}
        }

    def test_dauer_dauermethode(self):
        obj = Dauermethode(**self.parameter['dauer'])
        self.assertEqual(10000, obj.dauer())

    # def test_dauer_funktionsmethode(self):
    #     obj = Funktionsmethode(**self.parameter['funk'])
    #     self.assertEqual(10000, obj.dauer())

    def test_distanze(self):
        obj = Dauermethode(**self.parameter['distanze_test'])
        self.assertEqual(10*100, obj.distanze())

    def test_berechne_werte_dauermethode(self):
        obj = Dauermethode(**self.parameter['dauer'])
        self.assertEqual(("G1", 40, 100), obj.berechne_werte(5000))
        self.assertEqual(("G1", 40, 100), obj.berechne_werte(50000))

    # def test_berechne_werte_funktionsmethode(self):
    #     obj = Funktionsmethode(**self.parameter['funk'])
    #     self.assertEqual(("G1", 5002, 10000), obj.berechne_werte(5000))
    #     self.assertEqual(("G1", 50002, 100000), obj.berechne_werte(50000))
