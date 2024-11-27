from unittest import TestCase
from unittest.mock import Mock, patch
from src.classes.viewdatenmodell import ViewDatenmodell


class MockControllerStatus:
    def __init__(self, pwm_wert: int = 40, distanze_am_ziel: int = 6000):
        self.modell = Mock()
        self.modell.ergo = Mock()
        self.berechne_pwm_wert = Mock(return_value=pwm_wert)
        self.gestoppte_zeit = Mock()
        self.modell.ergo.lese_cadence.return_value = 120
        self.modell.ergo.calc_cad_durchschnitt.return_value = 100
        self.modell.ergo.lese_distance.return_value = 500
        self.modell.ergo.calc_power_index.return_value = 36
        self.modell.zonen.calcPowerGesamt.return_value = 172
        self.modell.zonen.calcPowerDurchschnitt.return_value = 34
        self.modell.ergo.calc_power_watt.return_value = 233
        self.werte_nach_trainngsplan = [0, 0, 90]
        self.gestoppte_zeit.als_ms.return_value = 5 * 60 * 1000     # 5min
        self.modell.ergo.calc_distanze_am_ende.return_value = distanze_am_ziel

class test_ViewDatenmodell(TestCase):

    def test_view_datenmodell_init(self):
        assert True

    def test_berechne_ergometer_daten(self):
        obj = ViewDatenmodell()
        mock_status = MockControllerStatus()
        result = obj.berechne_ergometer_daten()
        result = obj.berechne_ergometer_daten(mock_status)
        self.assertEqual(120, result.cad_frequenz)
        self.assertEqual(100, result.cad_durchschnitt)
        self.assertEqual(90, result.cad_aktuell)
        self.assertEqual(30, result.cad_differenz)
        self.assertEqual(0.4, result.pwm_wert)
        self.assertEqual(500, result.distanze)
        self.assertEqual(6000, result.distanze_am_ziel)
        self.assertEqual(36, result.power_aktuell)
        self.assertEqual(172, result.power_gesamt)
        self.assertEqual(34, result.power_durchschnitt)
        self.assertEqual(233, result.power_watt)
