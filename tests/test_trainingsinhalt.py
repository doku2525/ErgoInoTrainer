from unittest import TestCase

from src.classes.trainingsinhalt import (Trainingsinhalt, BelastungTypen, Dauermethode,
                                         Funktionsmethode, CountdownBisStart)


class test_Trainingsinhalt(TestCase):
    def setUp(self):
        self.parameter = {
            "dauermethode": {"dauer_in_millis": 10000, "typ": BelastungTypen.Intervall, "cad": 100,
                             "power": 40, "name": "G1"},
            "distanze_test": {"dauer_in_millis": 10*60000, "typ": BelastungTypen.Intervall, "cad": 100,
                              "power": 40, "name": "G1"},
            "funkmethode": {"dauer_in_millis": 10000, "typ": BelastungTypen.Intervall, "cad": lambda x: x * 2,
                            "power": lambda x: x + 2, "name": "G1"}
        }

    def test_init_dauermethode(self):
        obj = Dauermethode()
        self.assertIsInstance(obj, Dauermethode)
        self.assertTrue(issubclass(type(obj), Trainingsinhalt))
        self.assertEqual('', obj.name)
        self.assertEqual(0, obj.dauer_in_millis)
        self.assertEqual(BelastungTypen.G1, obj.typ)
        self.assertEqual(0, obj.cad)
        self.assertEqual(0, obj.power)
        self.assertTrue(obj.logging)

    # def test_init_funktionsmethode(self):
    #     raise NotImplementedError

    def test_init_countdownbistart(self):
        obj = CountdownBisStart()
        self.assertIsInstance(obj, CountdownBisStart)
        self.assertTrue(issubclass(type(obj), Trainingsinhalt))
        self.assertEqual('Countdown', obj.name)
        self.assertEqual(15_000, obj.dauer_in_millis)
        self.assertEqual(BelastungTypen.COUNTDOWN, obj.typ)
        self.assertEqual(0, obj.cad)
        self.assertEqual(0, obj.power)
        self.assertFalse(obj.logging)

    def test_dauer_dauermethode(self):
        obj = Dauermethode(**self.parameter['dauermethode'])
        self.assertEqual(10000, obj.dauer())

    def test_dauer_countdownbistart(self):
        obj = CountdownBisStart(dauer_in_millis=20_000)
        self.assertEqual(20_000, obj.dauer())
        self.assertEqual(BelastungTypen.COUNTDOWN, obj.typ)
        self.assertFalse(obj.logging)

    # def test_dauer_funktionsmethode(self):
    #     obj = Funktionsmethode(**self.parameter['funk'])
    #     self.assertEqual(10000, obj.dauer())

    def test_distanze_dauermethode(self):
        obj = Dauermethode(**self.parameter['distanze_test'])
        self.assertEqual(10*100, obj.distanze())
        obj = CountdownBisStart()
        self.assertEqual(0, obj.distanze())

    def test_berechne_werte_dauermethode_dauermethode(self):
        obj = Dauermethode(**self.parameter['dauermethode'])
        self.assertEqual(("G1", 40, 100), obj.berechne_werte(5000))
        self.assertEqual(("G1", 40, 100), obj.berechne_werte(50000))

    # def test_berechne_werte_funktionsmethode(self):
    #     obj = Funktionsmethode(**self.parameter['funk'])
    #     self.assertEqual(("G1", 5002, 10000), obj.berechne_werte(5000))
    #     self.assertEqual(("G1", 50002, 100000), obj.berechne_werte(50000))
