from unittest import TestCase
from unittest.mock import patch, Mock, MagicMock
from dataclasses import replace
import time

import src.classes.ergometer
from src.classes.applikationmodel import ApplikationModell
from src.classes.controllerstatus import ControllerStatus, ZEIT_DELTA
from src.classes.boardconnector import BoardConnector
from src.classes.stoppuhr import FlexibleZeit
from src.classes import trainingsprogramm as tp


class test_ControllerStatus(TestCase):

    def setUp(self):
        with patch('src.modules.audiomodul.build_playlist') as mock_build_playlist:
            mock_build_playlist.return_value = []
            programm = tp.erzeuge_trainingsprogramm_Tabata((1, 10), (90, 100),
                                                      warmfahrzeit=0.25,
                                                      ausfahrzeit=0.25)
            modell = ApplikationModell(board=BoardConnector(device=None))
            modell.trainingsprogramm = programm
            self.status = ControllerStatus(modell)
            self.status.werte_nach_trainngsplan = tuple()

    def test_programm_beenden(self):
        self.assertFalse(self.status.programm_beenden())
        self.status.gedrueckte_taste = 'QUIT'
        self.assertTrue(self.status.programm_beenden())

    def test_stoppe_zeit(self):
        # TODO Der Aufruf mit self.status.stoppe_zeit() liefert 0
        zeit = int(time.time() * 1000)
        self.status = self.status.stoppe_zeit()
        self.assertAlmostEqual(zeit, self.status.modell.millis_jetzt(), delta=20)

    def test_es_ist_zeit_fuer_update(self):
        self.status.gestoppte_zeit = FlexibleZeit.create_from_sekunden(0)
        self.status.zeit_fuer_naechstes_update = FlexibleZeit.create_from_sekunden(1)
        for x in range(11):
            self.status.gestoppte_zeit = FlexibleZeit.create_from_sekunden(x/10)
            if x <= 10:
                self.assertFalse(self.status.es_ist_zeit_fuer_update())
            else:
                self.assertTrue(self.status.es_ist_zeit_fuer_update())

    def test_berechne_neue_updatezeit(self):
        self.status.gestoppte_zeit = FlexibleZeit.create_from_millis(0)
        self.assertEqual(FlexibleZeit.create_from_millis(1000),
                         self.status.zeit_fuer_naechstes_update)
        for x in range(2,11):
            self.status.berechne_neue_updatezeit()
            self.assertEqual(FlexibleZeit.create_from_millis(x * 1000),
                             self.status.zeit_fuer_naechstes_update)

    @patch('src.classes.stoppuhr.FlexibleZeit.als_ms')
    def test_update_werte_nach_trainingsplan(self, mock_als_ms):
        mock_als_ms.return_value = 10000
        result = self.status.update_werte_nach_trainingsplan()
        self.assertEqual(('Warmfahren', 1, 90), result.werte_nach_trainngsplan)
        mock_als_ms.return_value = 8 * 30_000 + 15_000 - 1000
        result = self.status.update_werte_nach_trainingsplan()
        self.assertEqual(('Pause', 1, 90), result.werte_nach_trainngsplan)
        mock_als_ms.return_value = 8 * 30_000 + 15_000 - 21_000
        result = self.status.update_werte_nach_trainingsplan()
        self.assertEqual(('Intervall', 10, 100), result.werte_nach_trainngsplan)
        mock_als_ms.return_value = 8 * 30_000 + 2 * 15_000 - 1_000
        result = self.status.update_werte_nach_trainingsplan()
        self.assertEqual(('Ausfahren', 1, 90), result.werte_nach_trainngsplan)
        mock_als_ms.return_value = 8 * 30_000 + 2 * 15_000 + 1_000
        result = self.status.update_werte_nach_trainingsplan()
        self.assertEqual(('Ausfahren', 1, 90), result.werte_nach_trainngsplan)


    def test_berechne_pwm_wert(self):
        self.status.werte_nach_trainngsplan = ('Warmfahren', 1, 90)
        self.assertEqual(1, self.status.berechne_pwm_wert())
        self.status.modell.ergo = replace(self.status.modell.ergo, korrekturwerte_bremse={'Warmfahren': 10})
        self.assertEqual(11, self.status.berechne_pwm_wert())

    @patch('src.classes.stoppuhr.FlexibleZeit.als_ms')
    @patch('src.classes.controllerstatus.ControllerStatus.es_ist_zeit_fuer_update')
    def test_trainingsende_pause_machen(self, mock_update_zeit, mock_als_ms):

        # Es sollte nur bei einer Konstellation true ergeben
        mock_update_zeit.return_value = True
        mock_als_ms.return_value = self.status.modell.trainingsprogramm.trainingszeit_dauer_gesamt() + 1
        self.status.modell.trainingsprogramm.unendlich = False
        self.assertTrue(self.status.trainingsende_pause_machen())

        # Fuer sich aendernde ControllerStatus.gestoppte_zeit
        mock_update_zeit.return_value = True
        mock_als_ms.return_value = self.status.modell.trainingsprogramm.trainingszeit_dauer_gesamt()
        self.status.modell.trainingsprogramm.unendlich = False
        self.assertFalse(self.status.trainingsende_pause_machen())

        # Fuer sich aendernde ControllerStatus.es_ist_zeit_fuer_update()
        mock_update_zeit.return_value = False
        mock_als_ms.return_value = self.status.modell.trainingsprogramm.trainingszeit_dauer_gesamt() + 1
        self.status.modell.trainingsprogramm.unendlich = False
        self.assertFalse(self.status.modell.trainingsprogramm.unendlich)

        # Fuer sich aendernde ControllerStatus.modell.trainingsprogramm.unendlich
        mock_update_zeit.return_value = True
        mock_als_ms.return_value = self.status.modell.trainingsprogramm.trainingszeit_dauer_gesamt() + 1
        self.status.modell.trainingsprogramm.unendlich = True
        self.assertFalse(self.status.trainingsende_pause_machen())

    @patch('src.classes.stoppuhr.FlexibleZeit.als_ms')
    @patch('src.classes.controllerstatus.ControllerStatus.es_ist_zeit_fuer_update')
    @patch('src.classes.controllerstatus.ControllerStatus.neuer_wert_pause_nach_aktuellem_inhalt')
    def test_pause_am_ende_des_aktuellen_inhalts(self, mock_neuer_wert, mock_update_zeit, mock_als_ms):
        # True-Bedingungen
        mock_update_zeit.return_value = True
        mock_als_ms.return_value = 0
        mock_neuer_wert.return_value = True
        self.assertTrue(self.status.pause_am_ende_des_aktuellen_inhalts())
        mock_als_ms.return_value = ZEIT_DELTA - 1
        self.assertTrue(self.status.pause_am_ende_des_aktuellen_inhalts())

        # False-Bedingungen
        mock_update_zeit.return_value = True
        mock_als_ms.return_value = 0
        mock_neuer_wert.return_value = False
        self.assertFalse(self.status.pause_am_ende_des_aktuellen_inhalts())
        mock_als_ms.return_value = ZEIT_DELTA
        mock_neuer_wert.return_value = True
        self.assertFalse(self.status.pause_am_ende_des_aktuellen_inhalts())
        mock_update_zeit.return_value = False
        mock_als_ms.return_value = 0
        mock_neuer_wert.return_value = True
        self.assertFalse(self.status.pause_am_ende_des_aktuellen_inhalts())


    @patch('src.classes.stoppuhr.FlexibleZeit.als_ms')
    def test_neuer_wert_pause_nach_aktuellem_inhalt(self, mock_als_ms):
        # Wenn pause_nach_aktuellem_inhalt = False und trainingsplan.unendlich = False
        mock_als_ms.return_value = 1000
        self.assertFalse(self.status.neuer_wert_pause_nach_aktuellem_inhalt())
        mock_als_ms.return_value = 8 * 30_000 + 15_000
        self.assertFalse(self.status.neuer_wert_pause_nach_aktuellem_inhalt())
        mock_als_ms.return_value = 8 * 30_000 + 15_000 + ZEIT_DELTA - 1
        self.assertFalse(self.status.neuer_wert_pause_nach_aktuellem_inhalt())
        mock_als_ms.return_value = 8 * 30_000 + 15_000 + ZEIT_DELTA + 1
        self.assertTrue(self.status.neuer_wert_pause_nach_aktuellem_inhalt())

        # Wenn pause_nach_aktuellem_inhalt = True immer True
        self.status.pause_nach_aktuellem_inhalt = True
        mock_als_ms.return_value = ZEIT_DELTA - 1
        self.assertTrue(self.status.neuer_wert_pause_nach_aktuellem_inhalt())
        mock_als_ms.return_value = 1000
        self.assertTrue(self.status.neuer_wert_pause_nach_aktuellem_inhalt())
        mock_als_ms.return_value = 15_000 + 1000
        self.assertTrue(self.status.neuer_wert_pause_nach_aktuellem_inhalt())

    def test_update_ergometer(self):
        pass

    def test_update_musik(self):
        pass

    def test_update_pulswerte(self):
        pass

    def test_update_daten(self):
        pass

    def test_update_status(self):
        pass