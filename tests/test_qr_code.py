from unittest import TestCase
from unittest.mock import patch, call

from src.modules.qr_code import beende_anzeige, generate_qr_code, show_qr_code_in_tkinter, zeige_qr_code_in_tkinter


class test_QRCode(TestCase):

    def test_beende_anzeige(self):
        self.assertEqual([], beende_anzeige)

    def test_generate_qr_code(self):
        from qrcode.image.pil import PilImage
        result = generate_qr_code('HalloWelt.com')
        self.assertIsInstance(result, PilImage)
        self.assertIsInstance(result.size, tuple)
        self.assertEqual((290, 290), result.size)
        result = generate_qr_code('')
        self.assertIsInstance(result, PilImage)
        self.assertIsInstance(result.size, tuple)
        self.assertEqual((290, 290), result.size)
        result = generate_qr_code('Ein ganz langer Text, der viele Woeter hat.')
        self.assertIsInstance(result, PilImage)
        self.assertIsInstance(result.size, tuple)
        self.assertLess((290, 290), result.size)
