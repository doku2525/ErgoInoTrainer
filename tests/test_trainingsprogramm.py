from unittest import TestCase
from dataclasses import replace

from src.classes import trainingsinhalt
from src.classes.trainingsprogramm import (Trainingsprogramm, erzeuge_trainingsprogramm_G1,
                                           erzeuge_trainingsprogramm_G2Intervall, erzeuge_trainingsprogramm_Tabata,
                                           erzeuge_trainingsprogramm_G1_mit_sprints, erzeuge_trainingsprogramm_K3)
from src.classes.trainingsinhalt import Dauermethode, CountdownBisStart
import copy


class test_Trainingsprogramm(TestCase):
    def setUp(self):
        liste = [
            Dauermethode("G1", 10000, 100, 30, trainingsinhalt.BelastungTypen.Erholung)
        ]
        liste_mit_countdown = [CountdownBisStart()] + (liste * 5)
        self.plan = Trainingsprogramm("G1", liste)
        self.plan_mit_fuenf = Trainingsprogramm("G1", liste * 5)
        self.plan_mit_countdown = Trainingsprogramm("G1", liste_mit_countdown)
        self.mein_filter = lambda ti: ti.typ != trainingsinhalt.BelastungTypen.COUNTDOWN

    def test_fuehre_aus(self):
        self.plan = replace(self.plan, inhalte=self.plan.inhalte * 5)
        for index, element in enumerate(self.plan.inhalte):
            self.plan.inhalte[index] = copy.copy(element)
            self.plan.inhalte[index] = replace(self.plan.inhalte[index], name=f"G{index}")
        self.assertEqual(self.plan.fuehre_aus(0).name, "G0")
        self.assertEqual(self.plan.fuehre_aus(1).name, "G0")
        self.assertEqual(self.plan.fuehre_aus(10000).name, "G0")
        self.assertEqual(self.plan.fuehre_aus(10001).name, "G1")
        self.assertEqual(self.plan.fuehre_aus(20001).name, "G2")
        self.assertEqual(self.plan.fuehre_aus(30001).name, "G3")
        self.assertEqual(self.plan.fuehre_aus(40001).name, "G4")
        self.assertEqual(self.plan.fuehre_aus(50001).name, "G4")

    def test_verarbeite_messwerte(self):
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.verarbeite_messwerte(0, 5).ergebnisse, (5, ))
        self.assertEqual(self.plan.verarbeite_messwerte(5000, 5).ergebnisse, (5, ))
        self.assertEqual(self.plan.verarbeite_messwerte(10000, 10).ergebnisse, (10, ))
        self.plan = self.plan.verarbeite_messwerte(10000, 10)
        self.assertEqual(self.plan.verarbeite_messwerte(15000, 15).ergebnisse, (10, 15))
        self.plan = self.plan.verarbeite_messwerte(15000, 15)
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 20).ergebnisse, (10, 15, 20))

    def test_verarbeite_messwerte_falsche(self):
        # Macht in der Praxis keinen Sinn und sollte von der Programmlogik der Aufrufenden Funktion abgefangen werden
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 5).ergebnisse, (5, ))
        self.plan = self.plan.verarbeite_messwerte(20001, 5)
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 5).ergebnisse, (5, 5))
        self.plan = self.plan.verarbeite_messwerte(20001, 5)
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 5).ergebnisse, (5, 5, 5))
        self.plan = self.plan.verarbeite_messwerte(20001, 5)
        self.assertEqual(self.plan.verarbeite_messwerte(10001, 10).ergebnisse, (5, 5, 10))

    def test_berechne_distanze_pro_fertige_inhalte(self):
        self.plan = self.plan_mit_fuenf
        self.plan = self.plan.verarbeite_messwerte(0, 5)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), ())
        self.plan = self.plan.verarbeite_messwerte(5000, 5)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), ())
        self.plan = self.plan.verarbeite_messwerte(10000, 10)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), ())
        self.plan = self.plan.verarbeite_messwerte(15000, 15)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), (10, ))
        self.plan = self.plan.verarbeite_messwerte(20001, 21)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), (10, 5))

    def test_berechne_distanze_aktueller_inhalt(self):
        self.plan = self.plan_mit_fuenf
        self.plan = self.plan.verarbeite_messwerte(0, 5)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 5)
        self.plan = self.plan.verarbeite_messwerte(5000, 5)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 5)
        self.plan = self.plan.verarbeite_messwerte(10000, 10)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 10)
        self.plan = self.plan.verarbeite_messwerte(15000, 15)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 5)
        self.plan = self.plan.verarbeite_messwerte(20000, 19)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 9)
        self.plan = self.plan.verarbeite_messwerte(20001, 20)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 1)
        self.plan = self.plan.verarbeite_messwerte(21000, 21)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 2)

    def test_fuehre_naechstes_aus(self):
        self.plan = self.plan_mit_fuenf
        for index, element in enumerate(self.plan.inhalte):
            self.plan.inhalte[index] = copy.copy(element)
            self.plan.inhalte[index] = replace(self.plan.inhalte[index], name=f"G{index}")
        self.assertEqual(self.plan.fuehre_naechstes_aus(0).name, "G1")
        self.assertEqual(self.plan.fuehre_naechstes_aus(1).name, "G1")
        self.assertEqual(self.plan.fuehre_aus(10000).name, "G0")
        self.assertEqual(self.plan.fuehre_naechstes_aus(10000).name, "G1")
        self.assertEqual(self.plan.fuehre_naechstes_aus(10001).name, "G2")
        self.assertEqual(self.plan.fuehre_naechstes_aus(20000).name, "G2")
        self.assertEqual(self.plan.fuehre_naechstes_aus(20001).name, "G3")
        self.assertEqual(self.plan.fuehre_naechstes_aus(30001).name, "G4")
        self.assertEqual(self.plan.fuehre_naechstes_aus(40001).name, "G4")
        self.assertEqual(self.plan.fuehre_naechstes_aus(50000).name, "G4")
        self.assertEqual(self.plan.fuehre_naechstes_aus(50001).name, "G4")

    def test_trainingszeit_dauer_gesamt(self):
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(), 10000)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(), 50000)

    def test_trainingszeit_dauer_gesamt_mit_filter(self):
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(filter_funktion=self.mein_filter), 10000)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(filter_funktion=self.mein_filter), 50000)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(filter_funktion=self.mein_filter), 50000)

    def test_trainingszeit_dauer_gesamt_mit_filter_und_countdown(self):
        self.plan = self.plan_mit_countdown
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(), 65_000)
        self.plan = self.plan_mit_countdown
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(filter_funktion=self.mein_filter), 50_000)

    def test_trainingszeit_rest_gesamt(self):
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0), 10000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(5000), 5000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10000), 0)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10001), -1)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(-1000), 11000)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0), 50000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10000), 40000)

    def test_trainingszeit_rest_gesamt_mit_filter(self):
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0, self.mein_filter), 10000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(5000, self.mein_filter), 5000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10000, self.mein_filter), 0)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10001, self.mein_filter), -1)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(-1000, self.mein_filter), 11000)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0, self.mein_filter), 50000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10000, self.mein_filter), 40000)

    def test_trainingszeit_rest_gesamt_mit_filter_und_countdown(self):
        self.plan = self.plan_mit_countdown
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0), 65_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0, self.mein_filter), 50_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(5000), 60_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(5000, self.mein_filter), 45_000)
        self.plan = replace(self.plan, inhalte= list(reversed(self.plan_mit_countdown.inhalte)))
        # Jetzt steht Countdown am Ende. Beginnt also nach 50_000
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0), 65_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0, self.mein_filter), 50_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(50_000), 15_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(50_000, self.mein_filter), 0)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(55_000), 10_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(55_000, self.mein_filter), -5_000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(65_000), 0)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(65_000, self.mein_filter), -15_000)

    def test_trainingszeit_dauer_aktueller_inhalt(self):
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(0), 0)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(5000), 5000)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(0), 0)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(10000), 10000)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(10001), 1)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(45000), 5000)

    def test_countdown_aktueller_inhalt(self):
        self.assertEqual(self.plan.countdown_aktueller_inhalt(0), 10)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(1), 10)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(5000), 6)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(5001), 5)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.countdown_aktueller_inhalt(0), 10)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(10000), 1)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(10001), 10)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(45000), 6)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(45001), 5)
        self.plan = self.plan_mit_countdown
        self.assertEqual(self.plan_mit_countdown.fuehre_aus(0).typ, trainingsinhalt.BelastungTypen.COUNTDOWN)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(0), -15)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(5001), -10)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(15000), -1)
        self.assertEqual(self.plan.countdown_aktueller_inhalt(15001), 10)

    def test_trainingszeit_beendeter_inhalte(self):
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(0), 0)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(10000), 0)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(10001), 0)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(0), 0)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(10000), 0)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(10001), 10000)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(15000), 10000)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(25000), 20000)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(45000), 40000)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(50000), 40000)

    def test_berechne_distanze_gesamt(self):
        liste = [
            Dauermethode("G1", 10 * 60000, 100, 30, trainingsinhalt.BelastungTypen.Erholung),
            Dauermethode("G1", 10 * 60000, 100, 30, trainingsinhalt.BelastungTypen.Erholung)
        ]
        plan = Trainingsprogramm("G1", liste)
        self.assertEqual(20*100, plan.berechne_distanze_gesamt())

        liste = [
            Dauermethode("G1", 10 * 60000, 100, 30, trainingsinhalt.BelastungTypen.Erholung),
            Dauermethode("G1", 10 * 60000, 50, 30, trainingsinhalt.BelastungTypen.Erholung)
        ]
        plan = Trainingsprogramm("G1", liste)
        self.assertEqual(15*100, plan.berechne_distanze_gesamt())

    def test_finde_index_des_aktuellen_inhalts(self):
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(0), 0)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(10000), 0)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(10001), 0)
        self.plan = self.plan_mit_fuenf
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(10000), 0)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(10001), 1)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(15001), 1)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(20000), 1)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(20001), 2)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(45000), 4)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(50001), 4)

    def test_ist_letzter_inhalt(self):
        self.plan = self.plan_mit_fuenf
        self.assertFalse(self.plan.ist_letzter_inhalt(10000))
        self.assertFalse(self.plan.ist_letzter_inhalt(10001))
        self.assertFalse(self.plan.ist_letzter_inhalt(15001))
        self.assertFalse(self.plan.ist_letzter_inhalt(20000))
        self.assertFalse(self.plan.ist_letzter_inhalt(20001))
        self.assertFalse(self.plan.ist_letzter_inhalt(40000))
        self.assertTrue(self.plan.ist_letzter_inhalt(40001))
        self.assertTrue(self.plan.ist_letzter_inhalt(45000))
        self.assertTrue(self.plan.ist_letzter_inhalt(50001))

    def test_erzeuge_trainingsplan_G1(self):
        training = erzeuge_trainingsprogramm_G1(90, 35, 100)
        self.assertEqual(18, len(training.inhalte))
        self.assertEqual(90*60*1000, training.trainingszeit_dauer_gesamt())
        self.assertEqual(1, training.trainingszeit_dauer_aktueller_inhalt(5*60*1000+1))
        self.assertEqual(3*60*1000, training.fuehre_aus(2*60*1000).dauer() -
                         training.trainingszeit_dauer_aktueller_inhalt(2*60*1000))
        for index, element in enumerate(training.inhalte):
            self.assertEqual(5*60*1000, element.dauer(), f"Element {index}")

    def test_erzeuge_trainingsprogramm_G2Intervall(self):
        training = erzeuge_trainingsprogramm_G2Intervall((35, 45), (100, 100))
        zeit_intervall = 1
        zeit_pause = 4
        zeit_set = zeit_intervall + zeit_pause
        warmfahrzeit = 10
        ausfahrzeit = 5
        reps = 6
        to_millis = 60 * 1000

        self.assertEqual(reps * 2 + 2, len(training.inhalte))
        self.assertEqual((warmfahrzeit + (zeit_set * reps) + ausfahrzeit) * to_millis,
                         training.trainingszeit_dauer_gesamt())
        self.assertEqual("Warmfahren",
                         training.fuehre_aus(warmfahrzeit * to_millis).name)
        self.assertEqual("Ausfahren",
                         training.fuehre_aus((warmfahrzeit + zeit_set * reps) * to_millis + 1).name)
        for zeit in range(0, reps):
            self.assertEqual("Intervall",
                             training.fuehre_aus(warmfahrzeit * to_millis + 1 + zeit * zeit_set * to_millis).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Intervall",
                             training.fuehre_aus((warmfahrzeit + zeit_intervall) * to_millis + zeit *
                                                 zeit_set * to_millis).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_intervall * to_millis,
                             training.fuehre_aus(warmfahrzeit * to_millis + 1 + zeit * zeit_set * to_millis).dauer(),
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus((warmfahrzeit + zeit_set) * to_millis - 1 + zeit * zeit_set
                                                 * to_millis).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_pause * to_millis,
                             training.fuehre_aus((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis).dauer(), f"Zeit = {zeit}")

    def test_erzeuge_trainingsprogramm_Tabata(self):
        training = erzeuge_trainingsprogramm_Tabata((35, 55), (100, 100))
        zeit_intervall = 20 / 60
        zeit_pause = 10 / 60
        zeit_set = zeit_intervall + zeit_pause
        warmfahrzeit = 10
        ausfahrzeit = 6
        reps = 8
        to_millis = 60 * 1000

        self.assertEqual(reps * 2 + 2, len(training.inhalte))
        self.assertEqual((warmfahrzeit + (zeit_set * reps) + ausfahrzeit) * to_millis,
                         training.trainingszeit_dauer_gesamt())
        self.assertEqual("Warmfahren",
                         training.fuehre_aus(warmfahrzeit * to_millis).name)
        self.assertEqual("Ausfahren",
                         training.fuehre_aus(int((warmfahrzeit + zeit_set * reps) * to_millis) + 1).name)
        for zeit in range(0, reps):
            self.assertEqual("Intervall",
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 + zeit * zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Intervall",
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + zeit *
                                                 zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_intervall * to_millis,
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 +
                                                     zeit * zeit_set * to_millis)).dauer(),
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus(int((warmfahrzeit + zeit_set) * to_millis - 1 + zeit * zeit_set
                                                 * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_pause * to_millis,
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis)).dauer(), f"Zeit = {zeit}")

    def test_erzeuge_trainingsprogramm_G1_mit_sprints(self):
        training = erzeuge_trainingsprogramm_G1_mit_sprints((34, 64), (100, 100))
        zeit_intervall = 0.25
        zeit_pause = 4.75
        zeit_set = zeit_intervall + zeit_pause
        warmfahrzeit = 10
        reps = 4
        to_millis = 60 * 1000

        self.assertEqual(reps * 2 + 2 + 60 / 5, len(training.inhalte))
        self.assertEqual(90 * to_millis,
                         training.trainingszeit_dauer_gesamt())
        self.assertEqual("G1",
                         training.fuehre_aus(warmfahrzeit * to_millis).name)
        self.assertEqual("G1",
                         training.fuehre_aus(int((warmfahrzeit + zeit_set * reps) * to_millis + 1)).name)
        for zeit in range(0, reps):
            self.assertEqual("Intervall",
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 + zeit * zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Intervall",
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + zeit *
                                                 zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_intervall * to_millis,
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 +
                                                     zeit * zeit_set * to_millis)).dauer(),
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus(int((warmfahrzeit + zeit_set) * to_millis - 1 + zeit * zeit_set
                                                 * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_pause * to_millis,
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis)).dauer(), f"Zeit = {zeit}")

    def test_erzeuge_trainingsprogramm_K3(self):
        training = erzeuge_trainingsprogramm_K3((35, 80), (100, 50), intervall_dauer=5, ausfahrzeit=5)
        zeit_intervall = 5
        zeit_pause = 5
        zeit_set = zeit_intervall + zeit_pause
        warmfahrzeit = 10
        ausfahrzeit = 10 - zeit_pause
        reps = 3
        to_millis = 60 * 1000

        self.assertEqual(3 * 2 + 2, len(training.inhalte))
        self.assertTrue(not training.unendlich)
        self.assertEqual((warmfahrzeit + (zeit_set * reps) + ausfahrzeit) * to_millis,
                         training.trainingszeit_dauer_gesamt())
        self.assertEqual("Warmfahren",
                         training.fuehre_aus(warmfahrzeit * to_millis).name)
        self.assertEqual("Ausfahren",
                         training.fuehre_aus(int((warmfahrzeit + zeit_set * reps) * to_millis) + 1).name)
        for zeit in range(0, reps):
            self.assertEqual("Intervall",
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 + zeit * zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Intervall",
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + zeit *
                                                 zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_intervall * to_millis,
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 +
                                                     zeit * zeit_set * to_millis)).dauer(),
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual("Pause",
                             training.fuehre_aus(int((warmfahrzeit + zeit_set) * to_millis - 1 + zeit * zeit_set
                                                 * to_millis)).name,
                             f"Zeit = {zeit}")
            self.assertEqual(zeit_pause * to_millis,
                             training.fuehre_aus(int((warmfahrzeit + zeit_intervall) * to_millis + 1 + zeit *
                                                 zeit_set * to_millis)).dauer(), f"Zeit = {zeit}")
