from unittest import TestCase
from unittest.mock import patch
import time

from applikationmodel import ApplikationModell
from stoppuhr import Stoppuhr, FlexibleZeit, ZE
from boardconnector import BoardConnector


class test_ApplikationModell(TestCase):

    def setUp(self):
        self.object = ApplikationModell(board=BoardConnector())

    def test_initialisation(self):
        for _ in range(1000):
            zeit1 = int(time.time()*1000)
            zeit2 = self.object.zeitfunktion(ZE.MS)
            zeit3 = self.object.millis_jetzt()
            self.assertLessEqual(zeit1, zeit2)
            self.assertAlmostEqual(zeit1, zeit2, delta=1)
            self.assertAlmostEqual(zeit2, zeit3, delta=1)
            self.assertLessEqual(zeit2, zeit3)
            self.assertTrue(self.object.uhr.macht_pause())

    def test_akuelle_zeit(self):
        self.assertIsInstance(self.object.akuelle_zeit(), FlexibleZeit)
        self.assertEqual(0, self.object.akuelle_zeit().als_s())
        self.object.uhr.start(self.object.millis_jetzt())
        self.assertEqual(0, self.object.akuelle_zeit().als_s())
        time.sleep(1)
        self.assertEqual(1, round(self.object.akuelle_zeit().als_s()))
        self.object.uhr.pause(self.object.millis_jetzt())
        time.sleep(1)
        self.assertEqual(1, round(self.object.akuelle_zeit().als_s()))
