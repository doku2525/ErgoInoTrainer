from unittest import TestCase

from src.utils.netzwerk import ermittle_ip_adresse

class test_Netzwerk(TestCase):

    def test_ermittle_ip_adresse(self):
        result = ermittle_ip_adresse()
        self.assertNotEqual('', result)
        self.assertIsInstance(result, str)
        self.assertEqual("192.168.2", result[:9])
        self.assertEqual(4, len(result.split('.')))
