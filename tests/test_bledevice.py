from unittest import TestCase
from unittest.mock import patch, Mock
from src.classes.bledevice import PulsmesserBLEDevice, BLEHeartRateData

class test_PulsmesserBLEDevice(TestCase):

    @patch('pexpect.spawn')
    def test_connect(self, mock_spawn):
        device = PulsmesserBLEDevice()
        mock_spawn.return_value.sendline.side_effect = None
        mock_spawn.return_value.expect.side_effect = [1]
        self.assertTrue(device.connect(), "Erfolgreich Verbunden!")
        mock_spawn.return_value.expect.side_effect = [0]
        self.assertFalse(device.connect(), "Timoutfehler!")

    @patch('pexpect.spawn')
    def test_lese_batterie_level(self, mock_spawn):
        device = PulsmesserBLEDevice()
        mock_spawn.return_value.sendline.side_effect = None
        mock_spawn.return_value.expect.side_effect = [0]
        self.assertEqual(0, device.lese_batterie_level(), "Timeoutfehler!")
        mock_spawn.return_value.expect.side_effect = [1]
        mock_spawn.return_value.match.group.return_value = "0x32"
        self.assertEqual(50, device.lese_batterie_level(), "BLE-Device hat '0x32'(=50) als Wert geliefert!")

#    @patch('pexpect.spawn')
#    def test_interpretiere_herzfrequenz(self):
#        device = PulsmesserBLEDevice()
#        pass

    def test_ble_heartrate_data(self):
        obj = BLEHeartRateData.from_raw_data(b'10 4e ba 03 9f 03')
        self.assertEqual(16, obj.bit_flag)
        self.assertEqual(78, obj.herzfrequenz)
        self.assertEqual(2, len(obj.rr_intervall))
        self.assertEqual([954, 927], obj.rr_intervall)
        self.assertEqual('10 4e ba 03 9f 03', obj.als_raw_hex_datastring())

        obj = BLEHeartRateData.from_raw_data(b'10 4e')
        self.assertEqual(16, obj.bit_flag)
        self.assertEqual(78, obj.herzfrequenz)
        self.assertEqual(0, len(obj.rr_intervall))
