from unittest import TestCase
from unittest.mock import Mock, patch
from collections import namedtuple
import datetime
from datetime import datetime
from typing import Type, cast

from src.classes.viewdatenmodell import ViewDatenmodell
from src.classes.controllerstatus import ControllerStatus


class MockControllerStatus:
    def __init__(self):
        self.modell = Mock()
        self.modell.ergo = Mock()
        self.berechne_pwm_wert = Mock(return_value=40)
        self.gestoppte_zeit = Mock()
        # Mockwerte fuer berechne_ergometer_daten
        self.werte_nach_trainngsplan = [0, 0, 90]
        self.modell.ergo.lese_cadence.return_value = 120
        self.modell.ergo.calc_cad_durchschnitt.return_value = 100
        self.modell.ergo.lese_distance.return_value = 500
        self.modell.ergo.calc_distanze_am_ende.return_value = 6000
        self.modell.ergo.calc_power_index.return_value = 36
        self.modell.zonen.calcPowerGesamt.return_value = 172
        self.modell.zonen.calcPowerDurchschnitt.return_value = 34
        self.modell.ergo.calc_power_watt.return_value = 233

        # Mockwerte fuer test_berechne_intervall_daten
        self.modell.trainingsprogramm.berechne_distanze_aktueller_inhalt.return_value = 20
        self.gestoppte_zeit = Mock()
        self.gestoppte_zeit.als_ms.return_value = 10000
        self.modell.trainingsprogramm.trainingszeit_dauer_aktueller_inhalt.return_value = 30000
        self.modell.trainingsprogramm.countdown_aktueller_inhalt.return_value = 10
        self.modell.trainingsprogramm.berechne_distanze_pro_fertige_inhalte.return_value = [40, 20, 40]
        # Mock für inhalte
        # self.modell.trainingsprogramm.inhalte = Mock()
        MockType = namedtuple('MockedType', ['name', 'dauer'])
        self.modell.trainingsprogramm.inhalte = [
            Mock(dauer=Mock(return_value=20000), name='Intervall'),
            Mock(dauer=Mock(return_value=10000), name='Pause'),
            Mock(dauer=Mock(return_value=20000), name='Intervall')
        ]
        self.modell.trainingsprogramm.fuehre_aus = lambda x: MockType(name='Intervall', dauer=Mock(return_value=20000))

        # Mockwerte fuer berechne_puls_daten
        self.modell.pulsmesser.herzfrequenz = 140
        self.modell.pulsmesser.herzschlaege = 500
        self.modell.pulsmesser.calc_puls_durchschnitt.return_value = 130
        self.modell.puls_device.batterie_level = 90

        # Mockwerte fuer update_daten_modell
        self.gestoppte_zeit.als_s.return_value = 3*60
        self.pause_nach_aktuellem_inhalt = False
        self.modell.trainingsprogramm.unendlich = True
        self.modell.trainingsprogramm.trainingszeit_dauer_gesamt.return_value = 15*60*1000
        self.modell.zonen.mergeWerteAndPower.return_value = {}
        self.modell.board.device_daten.__dict__ = {}
        self.modell.trainingsprogramm.name = "Tabata"


class test_ViewDatenmodell(TestCase):

    def test_view_datenmodell_init(self):
        obj = ViewDatenmodell()
        self.assertEqual("", obj.trainings_name)

    def test_berechne_ergometer_daten(self):
        obj = ViewDatenmodell()
        mock_status = (cast(ControllerStatus, MockControllerStatus()))
        result = obj.berechne_ergometer_daten()
        self.assertEqual(obj, result)
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

    def test_berechne_intervall_daten(self):
        obj = ViewDatenmodell()
        mock_status = (cast(ControllerStatus, MockControllerStatus()))
        result = obj.berechne_intervall_daten()
        self.assertEqual(obj, result)
        result = obj.berechne_intervall_daten(mock_status)
        self.assertEqual(20, result.intervall_distanze)
        self.assertEqual(40, result.intervall_cad)
        self.assertEqual(  # TODO Beim mocken wird der Test auf den Namen 'Intervall' nicht erkannt. Deshalb allesgruen
            [
                [40, 120, 0, 0, (0, 255, 0)],
                [20, 120, 0, 0, (0, 255, 0)],
                [40, 120, 0, 0, (0, 255, 0)]],
            result.intervall_tabelle)
        self.assertEqual(0, result.anzahl_sets)  # TODO Gleiches Problem elem.name wird nicht erkannt
        self.assertEqual(0, result.anzahl_fertige_sets)  # TODO Gleiches Problem elem.name wird nicht erkannt
        self.assertEqual((255, 0, 0), result.intervall_farbe)

    def test_berechne_puls_daten(self):
        obj = ViewDatenmodell()
        mock_status = (cast(ControllerStatus, MockControllerStatus()))
        result = obj.berechne_puls_daten()
        self.assertEqual(obj, result)
        result = obj.berechne_puls_daten(mock_status)
        self.assertEqual(140, result.herz_frequenz)
        self.assertEqual(500, result.herz_gesamt)
        self.assertEqual(130, result.herz_durchschnitt)
        self.assertEqual(90, result.herz_batterielevel)

    def test_update_daten_modell(self):
        obj = ViewDatenmodell()
        mock_status = (cast(ControllerStatus, MockControllerStatus()))
        result = obj.update_daten_modell()
        self.assertEqual(obj, result)
        result = obj.update_daten_modell(mock_status)
        self.assertEqual("0:03:00", result.zeit_gesamt)
        self.assertEqual(10, result.zeit_timer)
        self.assertEqual("0:00:10", result.zeit_timer_string)
        self.assertEqual({}, result.werte_und_power)
        self.assertEqual("{}", result.device_werte)
        self.assertEqual("Tabata", result.trainings_name)
        self.assertEqual("Intervall", result.trainings_inhalt)
        self.assertEqual("0:15:00 ∞", result.trainings_gesamtzeit)
        mock_status.modell.trainingsprogramm.unendlich = False
        result = obj.update_daten_modell(mock_status)
        self.assertEqual("0:15:00 ⊗", result.trainings_gesamtzeit)
        mock_status.pause_nach_aktuellem_inhalt = True
        result = obj.update_daten_modell(mock_status)
        self.assertEqual("0:00:10⊗", result.zeit_timer_string)

    @patch('datetime.datetime')
    def test_erzeuge_log_string(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 11, 27, 12, 13, 14)
        obj = ViewDatenmodell()
        mock_status = (cast(ControllerStatus, MockControllerStatus()))
        result = obj.erzeuge_log_string()
        self.assertEqual(22, len(result.split("\t")))
        obj = ViewDatenmodell()
        obj = obj.update_daten_modell(mock_status)
        result = obj.erzeuge_log_string()
        self.assertEqual(22, len(result.split("\t")))
        self.assertEqual('Tabata', result.split("\t")[0])
        self.assertEqual('2024-11-27', result.split("\t")[1])
        self.assertEqual('12:13:14.000', result.split("\t")[2])
        self.assertEqual('0:03:00', result.split("\t")[3])
        self.assertEqual('Intervall', result.split("\t")[4])
        self.assertEqual('10', result.split("\t")[5])
        self.assertEqual('120', result.split("\t")[6])
        self.assertEqual('90', result.split("\t")[7])
        self.assertEqual('0', result.split("\t")[8])
        self.assertEqual('100', result.split("\t")[9])
        self.assertEqual('500', result.split("\t")[10])
        self.assertEqual('20', result.split("\t")[11])
        self.assertEqual('40', result.split("\t")[12])
        self.assertEqual('herz_schlaege', result.split("\t")[13])
        self.assertEqual('calcPulsDurchschnitt', result.split("\t")[14])
        self.assertEqual('calcHerzschlaegeIntervall', result.split("\t")[15])
        self.assertEqual('calcPulsIntervall', result.split("\t")[16])
        self.assertEqual('0.4', result.split("\t")[17])
        self.assertEqual('herz_freq', result.split("\t")[18])
        self.assertEqual('batterie_level', result.split("\t")[19])
        self.assertEqual('{}', result.split("\t")[20])
        self.assertEqual('herzwert', result.split("\t")[21])
