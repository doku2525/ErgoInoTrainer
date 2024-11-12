from unittest import TestCase
from unittest.mock import patch
import serial
from src.classes.boardconnector import BoardConnector, suche_ports
from src.classes.ergometerdevice import ArduinoSimulator, ArduinoDevice
from src.classes.devicedatenmodell import ArduinoDatenModell


class test_ArduinoBoard(TestCase):

    def setUp(self):
        self.board = BoardConnector()

    def test_suche_ports(self):
        with patch('os.path.exists') as mock_exists:
            # Keiner der Ports existiert
            mock_exists.return_value = False
            ports = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
            result = suche_ports(ports)
            self.assertEqual([], result)
            self.assertFalse(result)

            # Der erste Port existiert
            mock_exists.side_effect = [True, False]
            ports = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
            result = suche_ports(ports)
            self.assertEqual(result[0], "/dev/ttyUSB0")
            self.assertTrue(result)

            # Der zweite Port existiert
            mock_exists.side_effect = [False, True]
            ports = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
            result = suche_ports(ports)
            self.assertEqual(result[0], "/dev/ttyUSB1")
            self.assertTrue(result)

            # Meherer Ports existiert
            mock_exists.side_effect = [True, True]
            ports = ["/dev/ttyUSB0", "/dev/ttyUSB1"]
            result = suche_ports(ports)
            self.assertEqual(result[0], "/dev/ttyUSB0")
            self.assertTrue(result)

    def test_create_objekt(self):
        obj = BoardConnector()
        self.assertEqual(None, obj.device)
        self.assertFalse(obj.device)
        obj = BoardConnector(device=ArduinoSimulator(lambda: None))
        self.assertIsInstance(obj.device, ArduinoSimulator)
        self.assertTrue(obj.device)
        obj = BoardConnector(device=ArduinoDevice(serial.Serial()))
        self.assertTrue(obj.device)
        self.assertIsInstance(obj.device, ArduinoDevice)

    def test_create_device_daten(self):
        obj = BoardConnector(device=ArduinoDevice(serial.Serial()))
        self.assertIsInstance(obj.device, ArduinoDevice)
        self.assertIsInstance(obj.device_daten, ArduinoDatenModell)

    def test_sende_pwm_an_device(self):
        assert True

    def test_empfange_messwerte_von_device(self):
        assert True

    def test_berechne_pwm(self):
        self.assertEqual(0, self.board.berechne_pwm(100))
        self.board.device = ArduinoSimulator(lambda: None)
        self.assertEqual(255, self.board.berechne_pwm(100))
        self.assertEqual(0, self.board.berechne_pwm(0))
        self.assertEqual(128, self.board.berechne_pwm(50))
        self.assertLess(128, self.board.berechne_pwm(51))

    def test_lauf_zeit(self):
        assert True

    def test_sende_und_lese_werte(self):
        assert True

    def test_drucke_deviceinfo(self):
        obj = BoardConnector(device=ArduinoSimulator(lambda: None))
        self.assertTrue(callable(obj.device.port))
        self.assertTrue(obj.drucke_deviceinfo())
        obj = BoardConnector(device=ArduinoDevice(serial.Serial()))
        self.assertFalse(obj.drucke_deviceinfo())
