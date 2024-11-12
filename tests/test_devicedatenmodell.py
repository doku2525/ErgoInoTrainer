from unittest import TestCase
from src.classes.devicedatenmodell import ArduinoDatenModell

class test_DeviceDatenModell(TestCase):
    def setUp(self):
        self.arduinostring = b'1000,10,20,30,40,50,900,920,940,950\r\n'

    def test_verarbeite_messerte_arduinodatenmodell(self):
        obj = ArduinoDatenModell().verarbeite_messwerte(self.arduinostring)
        self.assertEqual(1000,obj.runtime)
        self.assertEqual(10, obj.pwm)
        self.assertEqual(50, obj.undef2)
        self.assertEqual((900,920,940,950), obj.runtime_pro_tritt)
