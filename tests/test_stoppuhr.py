from unittest import TestCase

from src.classes.stoppuhr import Stoppuhr, FlexibleZeit, ZE


class test_Stoppuhr(TestCase):
    def setUp(self):
        self.uhr = Stoppuhr(0)

    def test_pause(self):
        self.uhr = Stoppuhr.factory(0).pause(1)
        self.assertTrue(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 0)

        self.uhr = Stoppuhr.factory(0).pause(1).pause(2)
        self.assertTrue(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 0)

    def test_start(self):
        # Starte die Zeit
        self.uhr = Stoppuhr.factory(0).start(0)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 0)

        # Jeder weitere Aufruf sollte nichts veraendern
        self.uhr = Stoppuhr.factory(0).start(0).start(1)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 0)

        # Pausenlaenge, also 1-0, wird zu der urspruengliche startzeit hinzuaddiert. __pause bleibt unveraendert.
        self.uhr = Stoppuhr.factory(0).start(1)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 1)

        self.uhr = Stoppuhr.factory(0).start(1).start(2)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 1)

    def test_start_pause_combinationen(self):
        # Start bei 1 sek und pause bei 2 sek
        # Die startzeit der letzten Pause wird in __pause gespeichert.
        self.uhr = Stoppuhr.factory(0).start(1).pause(2)
        self.assertTrue(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 2)
        self.assertEquals(self.uhr.__dict__['startzeit'], 1)
        self.uhr = Stoppuhr.factory(0).start(1).pause(3)
        self.assertTrue(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 3)
        self.assertEquals(self.uhr.__dict__['startzeit'], 1)

        # Start bei 1 sek und pause bei 2 sek und bei 5 sek wieder start
        # startzeit ist 1 und wird mit der beendeten Pausenlaenge (5-2=3) aufaddiert.
        self.uhr = Stoppuhr.factory(0).start(1).pause(2).start(5)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 2)
        self.assertEquals(self.uhr.__dict__['startzeit'], 4)

        self.uhr = Stoppuhr.factory(0).start(1).pause(2).start(5).pause(10)
        self.assertTrue(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 10)
        self.assertEquals(self.uhr.__dict__['startzeit'], 4)

    def test_zeit(self):
        # Noch im Pausenmodus, nach Erzeugung
        self.uhr = Stoppuhr.factory(0)
        self.assertEquals(0, self.uhr.zeit(0))
        self.assertEquals(0, self.uhr.zeit(1))

        # Uhr nach 2 sek gestartet. Ohne Pausen seit Erzeugung
        self.uhr = Stoppuhr.factory(0).start(2)
        self.assertEquals(-1, self.uhr.zeit(1))
        self.assertEquals(0, self.uhr.zeit(2))
        self.assertEquals(1, self.uhr.zeit(3))

        # Uhr nach 2 sek gestartet und nach 4 sek wieder gestoppt.
        self.uhr = Stoppuhr.factory(0).start(2).pause(4)
        self.assertEquals(2, self.uhr.zeit(0))
        self.assertEquals(2, self.uhr.zeit(3))
        self.assertEquals(2, self.uhr.zeit(4))
        self.assertEquals(2, self.uhr.zeit(5))

        # Uhr nach 2 sek gestartet und nach 4 sek wieder gestoppt und nach 10 sek wieder gestartet.
        self.uhr = Stoppuhr.factory(0).start(2).pause(4).start(10)
        self.assertEquals(2, self.uhr.zeit(10))
        self.assertEquals(3, self.uhr.zeit(11))
        self.assertEquals(1, self.uhr.zeit(9))
        self.assertEquals(-8, self.uhr.zeit(0))

    def test_mache_pause(self):
        self.assertTrue(self.uhr.macht_pause())
        self.uhr = self.uhr.start(0)
        self.assertFalse(self.uhr.macht_pause())

    def test_reset(self):
        self.uhr = Stoppuhr.factory(0).reset(0)
        self.assertTrue(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 0)

        self.uhr = Stoppuhr.factory(0).reset(1)
        self.assertTrue(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 1)
        self.assertEquals(self.uhr.__dict__['startzeit'], 1)
        self.assertEquals(0, self.uhr.zeit(2))

        self.uhr = Stoppuhr.factory(0).start(0).reset(1)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 1)
        self.assertEquals(1, self.uhr.zeit(2))

        self.uhr = Stoppuhr.factory(0).start(0).reset(-1)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], -1)
        self.assertEquals(3, self.uhr.zeit(2))

        # Countdown mit negativen Zahlen
        self.uhr = Stoppuhr.factory(0).start(0).reset(10)
        self.assertFalse(self.uhr.macht_pause())
        self.assertEquals(self.uhr.__dict__['pausenzeit'], 0)
        self.assertEquals(self.uhr.__dict__['startzeit'], 10)
        self.assertEquals(-10, self.uhr.zeit(0))
        self.assertEquals(-1, self.uhr.zeit(9))
        self.assertEquals(0, self.uhr.zeit(10))

    def test_flexiblezeit_objekt(self):
        self.assertEqual(1000, FlexibleZeit.create_from_millis(1000).als(ZE.MS))
        self.assertEqual(1000, FlexibleZeit.create_from_millis(1000.45).als(ZE.MS))
        self.assertEqual(1, FlexibleZeit.create_from_millis(1000).als(ZE.SEK))
        self.assertEqual(1.5, FlexibleZeit.create_from_millis(1500).als(ZE.SEK))
        self.assertEqual(1, FlexibleZeit.create_from_millis(1000 * 60).als(ZE.MIN))
        self.assertEqual(1, FlexibleZeit.create_from_millis(1000 * 60 * 60).als(ZE.H))
        self.assertEqual(1000, FlexibleZeit.create_from_millis(1000).als_ms())
        self.assertEqual(1, FlexibleZeit.create_from_millis(1000).als_s())
        self.assertEqual(1000 * 60 * 1000, FlexibleZeit.create_from_minuten(1000).als_ms())
        self.assertEqual(1000 * 60, FlexibleZeit.create_from_minuten(1000).als_s())
        self.assertEqual(1000, FlexibleZeit.create_from_minuten(1000).als_min())
        self.assertEqual(1000 / 60, FlexibleZeit.create_from_minuten(1000).als_h())
        self.assertEqual(1.5, FlexibleZeit.create_from_minuten(90).als_h())
        self.assertEqual(60, FlexibleZeit.create_from_stunden(1).als_min())
        self.assertEqual(1, FlexibleZeit.create_from_sekunden(60).als_min())
        # Rechenfehler bei vielen Nachkommastellen
        self.assertEqual(1001, FlexibleZeit.create_from_sekunden(1.001).als_ms())
        self.assertEqual(1001, FlexibleZeit.create_from_sekunden(1.0009).als_ms())
        self.assertEqual(1001, FlexibleZeit.create_from_minuten(1001 / ZE.MIN.value).als_ms())
        self.assertEqual(1001, FlexibleZeit.create_from_stunden(1001 / ZE.H.value).als_ms())

    def test_flexiblezeit_boolean(self):
        self.assertTrue(FlexibleZeit.create_from_millis(900) < FlexibleZeit.create_from_millis(1000))
        self.assertLess(FlexibleZeit.create_from_millis(900), FlexibleZeit.create_from_millis(1000))
        self.assertTrue(FlexibleZeit.create_from_millis(1900) > FlexibleZeit.create_from_millis(1000))
        self.assertTrue(FlexibleZeit.create_from_millis(1000) == FlexibleZeit.create_from_millis(1000))
        self.assertTrue(FlexibleZeit.create_from_millis(1000) <= FlexibleZeit.create_from_millis(1000))
        self.assertTrue(FlexibleZeit.create_from_millis(2000) != FlexibleZeit.create_from_millis(1000))
        self.assertFalse(FlexibleZeit.create_from_millis(1900) < FlexibleZeit.create_from_millis(1000))
        self.assertFalse(FlexibleZeit.create_from_millis(1900) == FlexibleZeit.create_from_millis(1000))
        self.assertFalse(FlexibleZeit.create_from_millis(2000) <= FlexibleZeit.create_from_millis(1000))
        self.assertFalse(FlexibleZeit.create_from_millis(1000) != FlexibleZeit.create_from_millis(1000))

    def test_flexiblezeit_rechnen(self):
        zeit = FlexibleZeit.create_from_millis(900) + FlexibleZeit.create_from_millis(1000)
        self.assertEquals(1900, zeit.als_ms())
        zeit = zeit.__add__(FlexibleZeit.create_from_millis(1000))
        self.assertEquals(2900, zeit.als_ms())
        zeit2 = zeit + FlexibleZeit.create_from_millis(1000)
        self.assertEquals(2900, zeit.als_ms())
        self.assertEquals(3900, zeit2.als_ms())
