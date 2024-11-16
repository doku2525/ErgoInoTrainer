from unittest import TestCase
from unittest.mock import patch, Mock
import time
from src.classes.bledevice import PulsmesserBLEDevice, BLEHeartRateData


class test_PulsmesserBLEDevice(TestCase):

    @patch('pexpect.spawn')
    def test_zeitstempel(self, mock_spawn):
        device = PulsmesserBLEDevice()
        zeit1 = time.time()
        zeit2 = device.zeitstempel_funktion()
        self.assertAlmostEqual(zeit1, zeit2, delta=0.01)

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

    @patch('pexpect.spawn')
    @patch('time.sleep')
    def test_lese_ble_device(self, mock_sleep, mock_spawn):
        device = PulsmesserBLEDevice()
        mock_spawn.return_value.sendline.side_effect = None
        mock_spawn.return_value.expect.side_effect = [0]
        mock_spawn.return_value.match.group.return_value = b'10 4e ba 03 9f 03'
        device.connected = True
        # TODO Funktioniert nicht ohne das print-statement in lese_ble_device()
        # Starte den Thread
        self.assertTrue(device.starte_lese_ble_device_loop())
        time.sleep(1)
        # Überprüfe, ob der Thread läuft
        self.assertTrue(device.thread.is_alive())
        # Simuliere das Beenden des Threads
        device.lese_device_loop_flag = False
        mock_sleep.assert_called_once()  # Sicherstellen, dass sleep aufgerufen wurde
        # Warte, bis der Thread beendet ist
        device.thread.join()
        self.assertFalse(device.thread.is_alive())
        self.assertEqual(1, len(device.messdaten_queue))

        mein_ble_objekt = device.messdaten_queue.pop()
        self.assertEqual(b'10 4e ba 03 9f 03', mein_ble_objekt.ble_objekt.als_raw_hex_datastring().encode())
        self.assertEqual(78, mein_ble_objekt.ble_objekt.herzfrequenz)
        self.assertEqual(2, len(mein_ble_objekt.ble_objekt.rr_intervall))
        self.assertEqual(0, len(device.messdaten_queue))

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
