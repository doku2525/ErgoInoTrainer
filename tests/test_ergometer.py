from unittest import TestCase
from dataclasses import replace
from src.classes.ergometer import Ergometer
from src.classes.devicedatenmodell import ArduinoDatenModell


class test_Ergometer(TestCase):

    def test_distanze_waehrend_pause_variable(self):
        ergo = Ergometer()
        self.assertEqual(0, ergo.distanze_waehrend_pause)
        ergo = Ergometer().update_device_werte(ArduinoDatenModell(distanze=0), pause=True)
        self.assertEqual(0,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=0), pause=True).distanze_waehrend_pause)
        self.assertEqual(0,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).distanze_waehrend_pause)
        self.assertEqual(10,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=10), pause=False).distanze_waehrend_pause)
        self.assertEqual(25,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=10), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=False).
                         distanze_waehrend_pause)
        self.assertEqual(30,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=10), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=4), pause=False).
                         distanze_waehrend_pause)

    def test_set_bremse(self):
        ergo = Ergometer()
        self.assertEqual(ergo.bremse, 0)
        self.assertEqual(ergo.setBremse(-1).bremse, 0)
        self.assertEqual(ergo.setBremse(0).bremse, 0)
        self.assertEqual(ergo.setBremse(1).bremse, 1)
        self.assertEqual(ergo.setBremse(99).bremse, 99)
        self.assertEqual(ergo.setBremse(100).bremse, 100)
        self.assertEqual(ergo.setBremse(101).bremse, 100)

    def test_bremse_minus(self):
        ergo = Ergometer()
        self.assertEqual(ergo.bremseMinus().bremse, 0)
        self.assertEqual(ergo.setBremse(1).bremseMinus().bremse, 0)
        self.assertEqual(ergo.setBremse(100).bremseMinus().bremse, 99)
        self.assertEqual(ergo.setBremse(50).bremseMinus().bremseMinus().bremse, 48)
        self.assertEqual(ergo.setBremse(1).bremseMinus().bremseMinus().bremse, 0)
        self.assertEqual(ergo.bremseMinus('Intervall').korrekturwerte_bremse, {'Intervall': -1})
        self.assertEqual(ergo.bremseMinus('Intervall').bremseMinus('Intervall').korrekturwerte_bremse,
                         {'Intervall': -2})

    def test_bremse_minus_minus(self):
        ergo = Ergometer()
        self.assertEqual(ergo.bremseMinusMinus().bremse, 0)
        self.assertEqual(ergo.setBremse(1).bremseMinusMinus().bremse, 0)
        self.assertEqual(ergo.setBremse(100).bremseMinusMinus().bremse, 95)
        self.assertEqual(ergo.setBremse(50).bremseMinusMinus().bremseMinusMinus().bremse, 40)
        self.assertEqual(ergo.setBremse(9).bremseMinusMinus().bremseMinusMinus().bremse, 0)
        self.assertEqual(ergo.bremseMinusMinus('Intervall').korrekturwerte_bremse, {'Intervall': -5})
        self.assertEqual(ergo.bremseMinusMinus('Intervall').bremseMinusMinus('Intervall').korrekturwerte_bremse,
                         {'Intervall': -10})

    def test_bremse_plus(self):
        ergo = Ergometer()
        self.assertEqual(ergo.bremsePlus().bremse, 1)
        self.assertEqual(ergo.setBremse(100).bremsePlus().bremse, 100)
        self.assertEqual(ergo.setBremse(99).bremsePlus().bremse, 100)
        self.assertEqual(ergo.setBremse(98).bremsePlus().bremsePlus().bremse, 100)
        self.assertEqual(ergo.setBremse(99).bremsePlus().bremsePlus().bremse, 100)
        self.assertEqual(ergo.bremsePlus('Intervall').korrekturwerte_bremse, {'Intervall': 1})
        self.assertEqual(ergo.bremsePlus('Intervall').bremsePlus('Intervall').korrekturwerte_bremse,
                         {'Intervall': 2})

    def test_bremse_plus_plus(self):
        ergo = Ergometer()
        self.assertEqual(ergo.bremsePlusPlus().bremse, 5)
        self.assertEqual(ergo.setBremse(100).bremsePlusPlus().bremse, 100)
        self.assertEqual(ergo.setBremse(99).bremsePlusPlus().bremse, 100)
        self.assertEqual(ergo.setBremse(94).bremsePlusPlus().bremsePlusPlus().bremse, 100)
        self.assertEqual(ergo.setBremse(50).bremsePlusPlus().bremsePlusPlus().bremse, 60)
        self.assertEqual(ergo.bremsePlusPlus('Intervall').korrekturwerte_bremse, {'Intervall': 5})
        self.assertEqual(ergo.bremsePlusPlus('Intervall').bremsePlusPlus('Intervall').korrekturwerte_bremse,
                         {'Intervall': 10})

    def test_lese_distance(self):
        ergo = Ergometer()
        self.assertEqual(ergo.lese_distance(), 0)
        ArduinoDatenModell(distanze=0)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=0))
        self.assertEqual(ergo.lese_distance(), 0)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=1))
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=1)).lese_distance(), 1)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=255)).lese_distance(), 255)
        self.assertEqual(255, ergo.update_device_werte(ArduinoDatenModell(distanze=255)).device_werte.distanze)
        self.assertEqual(0, ergo.update_device_werte(ArduinoDatenModell(distanze=255)).distanze)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=0))
        self.assertEqual(ergo.lese_distance(), 255)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=1))
        self.assertEqual(ergo.lese_distance(), 256)
        self.assertEqual(1, ergo.distanze)
        ergo = Ergometer()
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=255))
        self.assertEqual(ergo.lese_distance(), 255)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=254))
        self.assertEqual(ergo.lese_distance(), 1*255 + 254)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=253))
        self.assertEqual(ergo.lese_distance(), 2*255 + 253)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=252))
        self.assertEqual(ergo.lese_distance(), 3*255 + 252)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=251))
        self.assertEqual(ergo.lese_distance(), 4*255 + 251)

    def test_lese_distance_waehrend_pause(self):
        ergo = Ergometer()
        self.assertEqual(0, ergo.lese_distance())
        ergo = Ergometer().update_device_werte(ArduinoDatenModell(distanze=0), pause=True)
        self.assertEqual(0,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=0), pause=True).lese_distance())
        self.assertEqual(0,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).lese_distance())
        self.assertEqual(0,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=10), pause=False).lese_distance())
        self.assertEqual(10,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=10), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=False).
                         lese_distance())
        self.assertEqual(10 + 254 - 35,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=10), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=4), pause=False).
                         lese_distance())
        self.assertEqual(10 + 215 + 5,
                         ergo.update_device_werte(ArduinoDatenModell(distanze=10), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=10), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=20), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=35), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=250), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=250), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=False).
                         update_device_werte(ArduinoDatenModell(distanze=4), pause=False).
                         lese_distance())

    def test_lese_cadence(self):
        ergo = Ergometer()
        self.assertEqual(ergo.lese_cadence(), 0)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=1, cad=0))
        self.assertEqual(ergo.lese_cadence(), 0)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=1, cad=1))
        self.assertEqual(ergo.lese_cadence(), 1)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=1, cad=255))
        self.assertEqual(ergo.lese_cadence(), 255)

    def test_calc_cad_durchschnitt(self):
        ergo = Ergometer()
        self.assertEqual(ergo.calc_cad_durchschnitt(0), 0)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=0))
        self.assertEqual(ergo.calc_cad_durchschnitt(0), 0)
        self.assertEqual(ergo.calc_cad_durchschnitt(1000), 0)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=1))
        self.assertEqual(ergo.calc_cad_durchschnitt(1000), 60)
        self.assertEqual(ergo.calc_cad_durchschnitt(500), 120)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=100))
        self.assertEqual(ergo.calc_cad_durchschnitt(60000), 100)
        self.assertEqual(ergo.calc_cad_durchschnitt(61000), 98)
        self.assertEqual(ergo.calc_cad_durchschnitt(59000), 102)
        self.assertEqual(ergo.calc_cad_durchschnitt(180000, 1), 33.3)
        self.assertEqual(ergo.calc_cad_durchschnitt(180000, 2), 33.33)
        self.assertEqual(ergo.calc_cad_durchschnitt(180000, 3), 33.333)
        self.assertEqual(ergo.calc_cad_durchschnitt(90000, 0), 67)
        self.assertEqual(ergo.calc_cad_durchschnitt(90000, 1), 66.7)
        self.assertEqual(ergo.calc_cad_durchschnitt(90000, 2), 66.67)
        self.assertEqual(ergo.calc_cad_durchschnitt(90000, 3), 66.667)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=255))
        self.assertEqual(ergo.calc_cad_durchschnitt(128000), 120)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=0))
        self.assertEqual(ergo.calc_cad_durchschnitt(255000), 60)
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=45))
        self.assertEqual(ergo.calc_cad_durchschnitt(180000), 100)

    def test_calc_distanze_am_ende(self):
        ergo = Ergometer()
        self.assertEqual(0, ergo.calc_distanze_am_ende(0, 10000))
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=1, cad=0))
        self.assertEqual(1, ergo.calc_distanze_am_ende(0, 10000))
        ergo = Ergometer()
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=0, cad=60))
        self.assertEqual(60, ergo.calc_distanze_am_ende(0, 60000))
        self.assertEqual(30, ergo.calc_distanze_am_ende(30000, 60000))
        ergo = ergo.update_device_werte(ArduinoDatenModell(distanze=30, cad=60))
        self.assertEqual(90, ergo.calc_distanze_am_ende(0, 60000))
        self.assertEqual(60, ergo.calc_distanze_am_ende(30000, 60000))

    def test_update_device_werte(self):
        ergo = Ergometer()
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=1)).distanze, 0)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=255)).distanze, 0)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=255)).
                         update_device_werte(ArduinoDatenModell(distanze=1)).distanze, 1)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=255)).
                         update_device_werte(ArduinoDatenModell(distanze=254)).
                         update_device_werte(ArduinoDatenModell(distanze=253)).
                         update_device_werte(ArduinoDatenModell(distanze=252)).
                         update_device_werte(ArduinoDatenModell(distanze=1)).distanze, 4)

    def test_update_device_werte_bei_pause(self):
        ergo = Ergometer()
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=1), pause=True).distanze, 0)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=1), pause=True).im_pausen_modus, True)
        self.assertIsNone(ergo.update_device_werte(ArduinoDatenModell(distanze=1), pause=True).device_werte)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=255), pause=True).distanze, 0)
        self.assertIsNone(ergo.update_device_werte(ArduinoDatenModell(distanze=1), pause=True).device_werte)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=255), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=1), pause=True).distanze, 0)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=255), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=253), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=252), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=1), pause=True).distanze, 0)
        self.assertIsNone(ergo.update_device_werte(ArduinoDatenModell(distanze=1), pause=True).device_werte)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=1)).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).device_werte.distanze,
                         1)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=1)).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).distanze_waehrend_pause,
                         0)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=1)).
                         update_device_werte(ArduinoDatenModell(distanze=254), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=254)).distanze_waehrend_pause,
                         253)
        self.assertEqual(ergo.update_device_werte(ArduinoDatenModell(distanze=254)).
                         update_device_werte(ArduinoDatenModell(distanze=5), pause=True).
                         update_device_werte(ArduinoDatenModell(distanze=5)).distanze_waehrend_pause,
                         6)


    def test_update_cad_zeitenliste(self):
        ergo = Ergometer()
        self.assertEqual([], ergo.update_cad_zeitenliste((0, 0, 0, 0)).cad_zeitenliste)
        self.assertEqual([], ergo.cad_zeitenliste)
        self.assertEqual([1], ergo.update_cad_zeitenliste((1, 0, 0, 0)).cad_zeitenliste)
        self.assertEqual(1, len(ergo.update_cad_zeitenliste((1, 0, 0, 0)).cad_zeitenliste))
        self.assertEqual([1, 2],
                         ergo.update_cad_zeitenliste((1, 0, 0, 0)).
                         update_cad_zeitenliste((1, 2, 0, 0)).cad_zeitenliste)
        self.assertEqual(2,
                         len(ergo.update_cad_zeitenliste((1, 0, 0, 0)).
                             update_cad_zeitenliste((1, 2, 0, 0)).cad_zeitenliste))
        ergo = replace(ergo, cad_zeitenliste=[2, 3, 4, 5])
        self.assertEqual(4, len(ergo.cad_zeitenliste))
        neue_zeiten = [(6, 7, 4, 5), (6, 7, 8, 4)]
        self.assertEqual([2, 3, 4, 5, 6, 7], ergo.update_cad_zeitenliste(neue_zeiten[0]).cad_zeitenliste)
        self.assertEqual(6, len(ergo.update_cad_zeitenliste(neue_zeiten[0]).cad_zeitenliste))
        self.assertEqual([2, 3, 4, 5, 6, 7, 8],
                         ergo.update_cad_zeitenliste(neue_zeiten[0]).
                         update_cad_zeitenliste(neue_zeiten[1]).cad_zeitenliste)

    def test_korrigiere_bremswert(self):
        ergo = Ergometer()
        self.assertEqual({}, ergo.korrekturwerte_bremse)
        self.assertEqual(100, ergo.korrigiere_bremswert(wert=110).bremse)
        self.assertEqual({}, ergo.korrigiere_bremswert(wert=110).korrekturwerte_bremse)
        self.assertEqual(100,
                         ergo.korrigiere_bremswert(wert=110).korrigiere_bremswert(name='Intervall', wert=5).bremse)
        self.assertEqual({'Intervall': 5},
                         ergo.korrigiere_bremswert(wert=110).
                         korrigiere_bremswert(name='Intervall', wert=5).korrekturwerte_bremse)
        self.assertEqual({'Intervall': -10},
                         ergo.korrigiere_bremswert(name='Intervall', wert=5).
                         korrigiere_bremswert(name='Intervall', wert=-15).
                         korrekturwerte_bremse)
        self.assertEqual({'Intervall': -10, 'Warmfahren': 1},
                         ergo.korrigiere_bremswert(name='Intervall', wert=5).
                         korrigiere_bremswert(name='Intervall', wert=-15).
                         korrigiere_bremswert(name='Warmfahren', wert=1).
                         korrekturwerte_bremse)

    def test_berechne_korigierten_bremswert(self):
        ergo = Ergometer()
        ergo = ergo.korrigiere_bremswert(wert=110)
        self.assertEqual(50, ergo.berechne_korigierten_bremswert(ausgangs_wert=50))
        self.assertEqual(100, ergo.berechne_korigierten_bremswert(ausgangs_wert=150))
        self.assertEqual(0, ergo.berechne_korigierten_bremswert(ausgangs_wert=-50))
        ergo = ergo.korrigiere_bremswert(name='Intervall', wert=5)
        self.assertEqual(55, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=50))
        self.assertEqual(100, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=150))
        self.assertEqual(0, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=-150))
        ergo = ergo.korrigiere_bremswert(name='Intervall', wert=-15)
        self.assertEqual(40, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=50))
        self.assertEqual(100, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=150))
        self.assertEqual(91, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=101))
        self.assertEqual(0, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=-150))
        self.assertEqual(0, ergo.berechne_korigierten_bremswert(name='Intervall', ausgangs_wert=9))
        self.assertEqual(50, ergo.berechne_korigierten_bremswert(name='Pause', ausgangs_wert=50))
        self.assertEqual(100, ergo.berechne_korigierten_bremswert(name='Pause', ausgangs_wert=150))
        self.assertEqual(0, ergo.berechne_korigierten_bremswert(name='Pause', ausgangs_wert=-50))
