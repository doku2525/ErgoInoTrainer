from unittest import TestCase
from generatorarduino import GeneratorArduino
import copy

class test_GeneratorArduino(TestCase):

    def setUp(self):
        self.arduino = GeneratorArduino()

    def test_generator_arduino(self):
        self.assertEqual(0, self.arduino.cad)
        self.assertEqual(0, self.arduino.dist)
        self.assertEqual(0, self.arduino.start_punkt)
        self.assertEqual(0, self.arduino.position)
        self.assertEqual([], self.arduino.messwerte)
        self.assertEqual(100, GeneratorArduino(cad=100).cad)

    def test_simuliere_fahrt(self):
        assert True

    def test_berechne_distanze(self):
        # Bei Cad = 0 sollte unabhaengig von der Zeit immer 0 als Ergebnis kommen
        self.assertEqual(0, self.arduino.berechne_distanze(0))
        self.assertEqual(0, self.arduino.berechne_distanze(10000))
        # Bei Cad = 60 sollte pro sekunden 1 Umdrehung erfolgen
        self.arduino = GeneratorArduino(cad=60)
        self.assertEqual(0, self.arduino.berechne_distanze(0))
        self.assertEqual(1, self.arduino.berechne_distanze(1))
        self.assertEqual(60, self.arduino.berechne_distanze(60))
        self.arduino = GeneratorArduino(cad=59)
        self.assertEqual(0, self.arduino.berechne_distanze(0),)
        self.assertEqual(0, self.arduino.berechne_distanze(1))
        self.assertEqual(1, self.arduino.berechne_distanze(2))
        self.assertEqual(58, self.arduino.berechne_distanze(59))
        self.assertEqual(59, self.arduino.berechne_distanze(60))
        self.assertEqual(59, self.arduino.berechne_distanze(61))
        self.assertEqual(60, self.arduino.berechne_distanze(62))
        self.arduino = GeneratorArduino(cad=120)
        self.assertEqual(0, self.arduino.berechne_distanze(0))
        self.assertEqual(2, self.arduino.berechne_distanze(1))
        self.assertEqual(120, self.arduino.berechne_distanze(60))

    def test_erzeuge_messwerte(self):
        mein_delta = 0.01
        self.assertEqual([], self.arduino.erzeuge_messwerte(0))
        self.assertEqual([], self.arduino.erzeuge_messwerte(100))
        self.arduino = GeneratorArduino(cad=60)
        self.assertEqual([], self.arduino.erzeuge_messwerte(0))
        self.assertEqual([1], self.arduino.erzeuge_messwerte(1))
        self.assertEqual(list(range(1,61)), self.arduino.erzeuge_messwerte(60))
        self.arduino = GeneratorArduino(cad=120)
        self.assertEqual([], self.arduino.erzeuge_messwerte(0))
        self.assertEqual([0.5, 1], self.arduino.erzeuge_messwerte(1))
        self.assertEqual(list(map(lambda x: x/100, range(50, 6050, 50))), self.arduino.erzeuge_messwerte(60))
        self.arduino = GeneratorArduino(cad=59)
        self.assertEqual([], self.arduino.erzeuge_messwerte(0))
        self.assertEqual([], self.arduino.erzeuge_messwerte(1))
        self.assertAlmostEqual(1.01, self.arduino.erzeuge_messwerte(2)[0], delta=mein_delta)
        self.assertAlmostEqual(1.01, self.arduino.erzeuge_messwerte(2)[-1], delta=mein_delta)
        self.assertAlmostEqual(2.03, self.arduino.erzeuge_messwerte(3)[-1], delta=mein_delta)
        self.assertAlmostEqual(3.05, self.arduino.erzeuge_messwerte(4)[-1], delta=mein_delta)
        self.assertEqual(60, self.arduino.erzeuge_messwerte(60)[-1])
        self.assertAlmostEqual(57.96, self.arduino.erzeuge_messwerte(58)[-1], delta=mein_delta)
        self.assertEqual(60, self.arduino.erzeuge_messwerte(61)[-1])

    def test_berechne_zeiger_position(self):
        self.arduino = GeneratorArduino(cad=60)
        self.assertEqual(0, self.arduino.berechne_zeiger_position(0))
        self.assertEqual(0, self.arduino.berechne_zeiger_position(1))
        self.assertEqual(1, self.arduino.berechne_zeiger_position(2))
        self.assertEqual(2, self.arduino.berechne_zeiger_position(3))
        self.assertEqual(3, self.arduino.berechne_zeiger_position(4))
        self.assertEqual(0, self.arduino.berechne_zeiger_position(5))
        self.assertEqual(0, self.arduino.berechne_zeiger_position(9))
        self.arduino = GeneratorArduino(cad=60, position=1)
        self.assertEqual(1, self.arduino.berechne_zeiger_position(0))
        self.assertEqual(1, self.arduino.berechne_zeiger_position(1))
        self.assertEqual(2, self.arduino.berechne_zeiger_position(2))
        self.assertEqual(3, self.arduino.berechne_zeiger_position(3))
        self.assertEqual(0, self.arduino.berechne_zeiger_position(4))
        self.assertEqual(1, self.arduino.berechne_zeiger_position(5))
        self.assertEqual(1, self.arduino.berechne_zeiger_position(9))
        self.arduino = GeneratorArduino(cad=60, position=3)
        self.assertEqual(3, self.arduino.berechne_zeiger_position(1))
        self.assertEqual(0, self.arduino.berechne_zeiger_position(2))
        self.assertEqual(3, self.arduino.berechne_zeiger_position(9))

    def test_konvertiere_liste_zu_slot(self):
        slot = (0,0,0,0)
        daten = (10,20,30,40,50)

        self.assertEqual(slot, self.arduino.konvertiere_liste_zu_slot([], slot, 0))
#        self.assertEqual([10,20,30,40], self.arduino.konvertiere_liste_zu_slot(list(daten[:4]), list(slot), 0))
#        self.assertEqual([20,30,40,10], self.arduino.konvertiere_liste_zu_slot(list(daten[:4]), list(slot), 2))