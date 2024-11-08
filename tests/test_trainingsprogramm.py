from unittest import TestCase

import trainingsinhalt
from trainingsprogramm import (Trainingsprogramm, erzeuge_trainingsprogramm_G1,
                               erzeuge_trainingsprogramm_G2Intervall, erzeuge_trainingsprogramm_Tabata,
                               erzeuge_trainingsprogramm_G1_mit_sprints)
from trainingsinhalt import Dauermethode
import copy


class test_Trainingsprogramm(TestCase):
    def setUp(self):
        liste = [
            Dauermethode("G1", 10000, 100, 30, trainingsinhalt.BelastungTypen.Erholung)
        ]
        self.plan = Trainingsprogramm("G1", liste)

    def test_fuehre_aus(self):
        self.plan.inhalte = self.plan.inhalte * 5
        for index, element in enumerate(self.plan.inhalte):
            self.plan.inhalte[index] = copy.copy(element)
            self.plan.inhalte[index].name = f"G{index}"
        self.assertEqual(self.plan.fuehre_aus(0).name, "G0")
        self.assertEqual(self.plan.fuehre_aus(1).name, "G0")
        self.assertEqual(self.plan.fuehre_aus(10000).name, "G0")
        self.assertEqual(self.plan.fuehre_aus(10001).name, "G1")
        self.assertEqual(self.plan.fuehre_aus(20001).name, "G2")
        self.assertEqual(self.plan.fuehre_aus(30001).name, "G3")
        self.assertEqual(self.plan.fuehre_aus(40001).name, "G4")
        self.assertEqual(self.plan.fuehre_aus(50001).name, "G4")

    def test_verarbeite_messwerte(self):
        self.plan.inhalte = self.plan.inhalte * 5
        self.assertEqual(self.plan.verarbeite_messwerte(0, 5), [5])
        self.assertEqual(self.plan.verarbeite_messwerte(5000, 5), [5])
        self.assertEqual(self.plan.verarbeite_messwerte(10000, 10), [10])
        self.assertEqual(self.plan.verarbeite_messwerte(15000, 15), [10,15])
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 20), [10,15,20])

    def test_verarbeite_messwerte_falsche(self):
        # Macht in der Praxis keinen Sinn und sollte von der Programmlogik der Aufrufenden Funktion abgefangen werden
        self.plan.inhalte = self.plan.inhalte * 5
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 5), [5])
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 5), [5, 5])
        self.assertEqual(self.plan.verarbeite_messwerte(20001, 5), [5, 5, 5])
        self.assertEqual(self.plan.verarbeite_messwerte(10001, 10), [5, 5, 10])

    def test_berechne_distanze_pro_fertige_inhalte(self):
        self.plan.inhalte = self.plan.inhalte * 5
        self.plan.verarbeite_messwerte(0, 5)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), [])
        self.plan.verarbeite_messwerte(5000, 5)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), [])
        self.plan.verarbeite_messwerte(10000, 10)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), [])
        self.plan.verarbeite_messwerte(15000, 15)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), [10])
        self.plan.verarbeite_messwerte(20001, 21)
        self.assertEqual(self.plan.berechne_distanze_pro_fertige_inhalte(), [10,5])

    def test_berechne_distanze_aktueller_inhalt(self):
        self.plan.inhalte = self.plan.inhalte * 5
        self.plan.verarbeite_messwerte(0, 5)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 5)
        self.plan.verarbeite_messwerte(5000, 5)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 5)
        self.plan.verarbeite_messwerte(10000, 10)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 10)
        self.plan.verarbeite_messwerte(15000, 15)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 5)
        self.plan.verarbeite_messwerte(20000, 19)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 9)
        self.plan.verarbeite_messwerte(20001, 20)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 1)
        self.plan.verarbeite_messwerte(21000, 21)
        self.assertEqual(self.plan.berechne_distanze_aktueller_inhalt(), 2)

    def test_fuehre_naechstes_aus(self):
        self.plan.inhalte = self.plan.inhalte * 5
        for index, element in enumerate(self.plan.inhalte):
            self.plan.inhalte[index] = copy.copy(element)
            self.plan.inhalte[index].name = f"G{index}"
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
        self.plan.inhalte = self.plan.inhalte * 5
        self.assertEqual(self.plan.trainingszeit_dauer_gesamt(), 50000)

    def test_trainingszeit_rest_gesamt(self):
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0), 10000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(5000), 5000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10000), 0)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10001), -1)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(-1000), 11000)
        self.plan.inhalte = self.plan.inhalte * 5
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(0), 50000)
        self.assertEqual(self.plan.trainingszeit_rest_gesamt(10000), 40000)

    def test_trainingszeit_dauer_aktueller_inhalt(self):
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(0), 0)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(5000), 5000)
        self.plan.inhalte = self.plan.inhalte * 5
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(0), 0)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(10000), 10000)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(10001), 1)
        self.assertEqual(self.plan.trainingszeit_dauer_aktueller_inhalt(45000), 5000)

    def test_trainingszeit_beendeter_inhalte(self):
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(0), 0)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(10000), 0)
        self.assertEqual(self.plan.trainingszeit_beendeter_inhalte(10001), 0)
        self.plan.inhalte = self.plan.inhalte * 5
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
        self.plan.inhalte = self.plan.inhalte * 5
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(10000), 0)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(10001), 1)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(15001), 1)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(20000), 1)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(20001), 2)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(45000), 4)
        self.assertEqual(self.plan.finde_index_des_aktuellen_inhalts(50001), 4)

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
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 + zeit * zeit_set * to_millis)).dauer(),
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
                             training.fuehre_aus(int(warmfahrzeit * to_millis + 1 + zeit * zeit_set * to_millis)).dauer(),
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

