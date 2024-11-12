from unittest import TestCase
import time

from src.classes.applikationmodel import ApplikationModell
from src.classes.stoppuhr import FlexibleZeit, ZE
from src.classes.boardconnector import BoardConnector


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
        self.assertTrue(self.object.uhr.macht_pause())
        self.object.uhr = self.object.uhr.start(self.object.millis_jetzt())
        self.assertFalse(self.object.uhr.macht_pause())
        time.sleep(0.25)
        self.assertAlmostEqual(0.25, self.object.akuelle_zeit().als_s(), delta=0.01)