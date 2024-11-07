from unittest import TestCase
from unittest.mock import patch
import serial
from ergometerdevice import ArduinoDevice, ArduinoSimulator, ErgometerDevice, convert_to_arduino_command


class test_ErgometerDevice(TestCase):

    def setUp(self):
        self.deviceAD = ArduinoDevice(port=None)
        self.deviceAS = ArduinoSimulator(port=lambda: None)

    def test_empfange_daten_von_device(self):
        self.assertEqual(b'1000,10,20,30,40,50,900,920,940,950\r\n', self.deviceAS.empfange_daten_von_device())
        liste = b'1000,0,0,0,0,0,0,0,0,0\r\n'
        self.deviceAS = ArduinoSimulator(port=lambda: liste)
        self.assertEqual(liste, self.deviceAS.empfange_daten_von_device())

    def test_sende_daten_an_device(self):
        with patch('serial.Serial.write') as mock_write:
            # Tests fuer ArduinoDevice
            self.deviceAD.port = serial.Serial
            self.deviceAD.sende_daten_an_device()
            mock_write.assert_called_once_with("0\n".encode())
            mock_write.reset_mock()
            self.deviceAD.sende_daten_an_device("")
            mock_write.assert_called_once_with("\n".encode())
            mock_write.reset_mock()
            self.deviceAD.sende_daten_an_device("", konverter=lambda x: "A".encode())
            mock_write.assert_called_once_with("A".encode())

            # Tests fuer ArduinoSimulator
            self.assertEqual("0\n".encode(), self.deviceAS.sende_daten_an_device())
            self.assertEqual("\n".encode(), self.deviceAS.sende_daten_an_device(""))
            self.assertEqual("A".encode(), self.deviceAS.sende_daten_an_device("",
                                                                               konverter=lambda x: "A".encode()))

    def test_lese_deviceinfos(self):
        with patch('ergometerdevice.ArduinoDevice.empfange_daten_von_device') as mock_empfange_von_device:

            # Simuliere die Rückgabewerte von empfange_von_device
            mock_empfange_von_device.side_effect = [
                b' Sketch: Nano_Ergometer v0\r\n',
                b' \r\n',
                b'148803000\r\n',
                b'14880250\r\n'
            ]

            self.assertEqual(self.deviceAD.version, "")
            self.assertEqual(self.deviceAD.zeit_arduino, 0)
            self.assertEqual(self.deviceAD.zeit_cadenze, 0)
            self.assertEqual(self.deviceAS.version, "")
            self.assertEqual(self.deviceAS.zeit_arduino, 0)
            self.assertEqual(self.deviceAS.zeit_cadenze, 0)

            # Rufe die zu testende Funktion auf
            self.deviceAD.lese_deviceinfos()
            self.deviceAS.lese_deviceinfos()

            # Assertions: Überprüfe, ob die Attribute korrekt gesetzt wurden
            self.assertEqual(self.deviceAD.version, "Sketch: Nano_Ergometer v0")
            self.assertEqual(self.deviceAD.zeit_arduino, 148803000)
            self.assertEqual(self.deviceAD.zeit_cadenze, 14880250)
            self.assertEqual(self.deviceAS.version, "Sketch: Simulator v0")
            self.assertEqual(self.deviceAS.zeit_arduino, 148803000)
            self.assertEqual(self.deviceAS.zeit_cadenze, 14880250)

    def test_convert_to_arduino_command(self):
        self.assertEqual("\n".encode(), convert_to_arduino_command(""))
        self.assertEqual("\n".encode(), convert_to_arduino_command("\n"))
        self.assertEqual("0\n".encode(), convert_to_arduino_command("0"))
