from unittest import TestCase
from dataclasses import replace
import os

import src.modules.audiomodul
from src.modules import audiomodul
from src.classes.trainingsprogramm import erzeuge_trainingsprogramm_Tabata, erzeuge_trainingsprogramm_G2Intervall
from src.classes.audioobjekt import AudioObjekt


class test_Audiomodul(TestCase):

    def setUp(self):
        self.audio = [
            AudioObjekt(filename='media/sounds/tabata.wav',
                        trainingsplan=['Tabata'], trainingsinhalt=['Intervall'], zeit_start=-10000, dauer=30000,
                        prioritaet=(100, 50)),
            AudioObjekt(filename='media/sounds/tabata.wav', trainingsplan=['Tabata'], trainingsinhalt=['Warmfahren'],
                        zeit_start=1000, dauer=30000, prioritaet=(10, 0), loops=-1),
            AudioObjekt(filename='media/sounds/tabata.wav', trainingsplan=['Tabata'], trainingsinhalt=['Ausfahren'],
                        zeit_start=1000, dauer=30000, prioritaet=(10, 0), loops=5)]
        audiomodul.AUDIOOBJEKT_AKTIVE = list()
        audiomodul.AUDIO_VOLUME_FADINGOUT = False

    def test_lautstaerke(self):
        self.assertAlmostEqual(audiomodul.AUDIO_VOLUME, audiomodul.lautstaerke(), delta=0.025)
        self.assertGreaterEqual(1.0, audiomodul.lautstaerke())
        self.assertLessEqual(0.0, audiomodul.lautstaerke())
        self.assertEqual(0.5, audiomodul.lautstaerke(0.5))
        self.assertEqual(0.0, audiomodul.lautstaerke(-1.5))
        self.assertEqual(1.0, audiomodul.lautstaerke(1.5))

    def test_lauter(self):
        audiomodul.lautstaerke(0)
        self.assertEqual(0.05, audiomodul.lauter())
        self.assertEqual(0.1, audiomodul.lauter())
        self.assertEqual(0.15, audiomodul.lauter())
        audiomodul.lautstaerke(0.5)
        self.assertEqual(0.55, audiomodul.lauter())
        audiomodul.lautstaerke(1)
        self.assertEqual(1.00, audiomodul.lauter())

    def test_leiser(self):
        audiomodul.lautstaerke(0)
        self.assertEqual(0.0, audiomodul.leiser())
        audiomodul.lautstaerke(1)
        self.assertEqual(0.95, audiomodul.leiser())
        self.assertEqual(0.90, audiomodul.leiser())
        audiomodul.lautstaerke(0.5)
        self.assertEqual(0.45, audiomodul.leiser())
        audiomodul.lautstaerke(0.10)
        self.assertEqual(0.05, audiomodul.leiser())
        self.assertEqual(0.0, audiomodul.leiser())
        self.assertEqual(0.0, audiomodul.leiser())

    def test_mute(self):
        audiomodul.AUDIO_VOLUME = audiomodul.lautstaerke(0.5)
        self.assertEqual(0.5, audiomodul.lautstaerke())
        audiomodul.AUDIO_VOLUME = audiomodul.mute()
        self.assertEqual(0.0, audiomodul.lautstaerke())
        audiomodul.AUDIO_VOLUME = audiomodul.mute()
        self.assertEqual(0.5, audiomodul.lautstaerke())
        audiomodul.AUDIO_VOLUME = audiomodul.mute()
        audiomodul.AUDIO_VOLUME = audiomodul.mute()

    def test_build_playlist(self):
        plan = erzeuge_trainingsprogramm_G2Intervall(pwm=(1, 3), cad=(100, 100))
        audio = self.audio
        self.assertEqual(0, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))

        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        # TODO Workaround, da Test fuer Tabata ohne Countdown geschrieben wurde
        plan = replace(plan, inhalte=plan.inhalte[1:])
        audio = self.audio[:1]
        self.assertEqual(8, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))
        for index in range(8):
            self.assertEqual(600000 - 10000 + index * 30000,
                             audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[index][0])

        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        # TODO Workaround, da Test fuer Tabata ohne Countdown geschrieben wurde
        plan = replace(plan, inhalte=plan.inhalte[1:])
        print(f"\nAudiomodule: {audiomodul.MEINE_AUDIO_OBJEKTE}")
        audio = (self.audio[:1] +
                 [replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Ausfahren'])])
        self.assertEqual(9, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))

        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        # TODO Workaround, da Test fuer Tabata ohne Countdown geschrieben wurde
        plan = replace(plan, inhalte=plan.inhalte[1:])
        audio = (audiomodul.MEINE_AUDIO_OBJEKTE[:1] +
                 [replace(replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Ausfahren']), zeit_start=0),
                  replace(replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Warmfahren']), zeit_start=0),
                  replace(replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Irgendwas']), zeit_start=10000)])
        self.assertEqual(10, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))
        self.assertEqual(0,
                         audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[0][0])
        self.assertEqual(600000 + 8 * 30000,
                         audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[-1][0])

    def test_play_audio_schedule_player_ungeladen(self):
        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        # TODO Workaround, da Test fuer Tabata ohne Countdown geschrieben wurde
        plan = replace(plan, inhalte=plan.inhalte[1:])
        audio = self.audio
        playlist = audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[1:-1]
        self.assertEqual(8, len(playlist))
        self.assertEqual([], audiomodul.AUDIOOBJEKT_AKTIVE)
        # Mit leerer Playlist => leere Listen und Funktion
        self.assertEqual([], audiomodul.play_audio_schedule()[0])
        self.assertEqual([], audiomodul.play_audio_schedule()[1])
        self.assertEqual(audiomodul.mache_nichts, audiomodul.play_audio_schedule()[2][0])
        # Zeit ist 0 => lade
        self.assertEqual([playlist[0]], audiomodul.play_audio_schedule(playlist=playlist)[0])
        self.assertEqual(playlist[1:], audiomodul.play_audio_schedule(playlist=playlist)[1])
        self.assertEqual(audiomodul.load_musik, audiomodul.play_audio_schedule(playlist=playlist)[2][0])
        aktuelle_zeit = playlist[0].startzeit
        # Zeit kurz for erster Startzeit =>
        self.assertEqual([playlist[0]],
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit - 100)[0])
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist,aktuelle_zeit_in_ms=aktuelle_zeit - 100)[1])
        self.assertEqual(audiomodul.load_musik,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit - 100)[2][0])
        # Zeit == erster Startzeit => play
        self.assertEqual([playlist[0]],
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[0])
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[1])
        self.assertEqual(audiomodul.load_und_play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[2][0])

    def test_play_audio_schedule_player_geladen_playlist_voll_startzeit_nicht_busy(self):
        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = self.audio
        playlist = audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[1:-1]
        self.assertEqual(8, len(playlist))
        self.assertEqual([], audiomodul.AUDIOOBJEKT_AKTIVE)
        audiomodul.AUDIOOBJEKT_AKTIVE = playlist[:1]
        playlist = playlist[1:]
        self.assertEqual(7, len(playlist))
        self.assertEqual(1, len(audiomodul.AUDIOOBJEKT_AKTIVE))

        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].startzeit
        # Zeit kurz vor Startzeit => Listen ungeaendert, leere Funktion
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit - 100)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit - 100)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit - 100)[2][0])
        # Zeit == erster Startzeit => Listen ungeaendert, play
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[1])
        self.assertEqual(audiomodul.play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[2][0])
        # Zeit > erster Startzeit => Listen ungeaendert, play
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit+1000)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit+1000)[1])
        self.assertEqual(audiomodul.play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit+1000)[2][0])
        # Zeit in Fadoutzeit => Listen ungeaendert, play
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit - audiomodul.FADINGOUT_DAUER//2
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[1])
        self.assertEqual(audiomodul.play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[2][0])
        # Zeit > endzeit == naechste startzeit => Listen aendern, load_play
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit
        self.assertEqual(playlist[:1],
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[0])
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[1])
        self.assertEqual(audiomodul.load_und_play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[2][0])
        # endzeit == ZEIT < naechste startzeit => Listen aendern, load
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit
        playlist = playlist[1:]
        self.assertEqual(playlist[:1],
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[0])
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[1])
        self.assertEqual(audiomodul.load_musik,
                         audiomodul.play_audio_schedule(playlist=playlist, aktuelle_zeit_in_ms=aktuelle_zeit)[2][0])

    def test_play_audio_schedule_player_geladen_playlist_voll_startzeit_busy(self):
        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = self.audio
        playlist = audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[1:-1]
        self.assertEqual(8, len(playlist))
        self.assertEqual([], audiomodul.AUDIOOBJEKT_AKTIVE)

        audiomodul.AUDIOOBJEKT_AKTIVE = playlist[:1]
        playlist = playlist[1:]
        self.assertEqual(7, len(playlist))
        self.assertEqual(1, len(audiomodul.AUDIOOBJEKT_AKTIVE))

        # Zeit < aktuelle startzeit - fading => Listen ungeaendert, mache_nichts
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].startzeit - 2000
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])

        # FADINGZEIT < ZEIT < aktuelle startzeit => Listen ungeaendert, fadeout
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].startzeit - audiomodul.FADINGOUT_DAUER // 2
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.fadeout_musik,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])
        # Zeit == Startzeit => Listen ungeaendert, mache_nichts
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].startzeit
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])
        # Zeit > Startzeit => Listen ungeaendert, mache_nichts
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].startzeit + 1000
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])

    def test_play_audio_schedule_player_geladen_playlist_voll_endzeit_busy(self):
        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = self.audio
        playlist = audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[1:-1]
        self.assertEqual(8, len(playlist))
        self.assertEqual([], audiomodul.AUDIOOBJEKT_AKTIVE)

        audiomodul.AUDIOOBJEKT_AKTIVE = playlist[:1]
        playlist = playlist[1:]
        self.assertEqual(7, len(playlist))
        self.assertEqual(1, len(audiomodul.AUDIOOBJEKT_AKTIVE))

        # FADOUTZEIT < Zeit Endzeit => Listen ungeaendert, fadeout
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit - audiomodul.FADINGOUT_DAUER // 2
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.fadeout_musik,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])

        # Zeit == Endzeit == naechste Startzeit => listen aendern, load_and_play Funktion
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit
        self.assertEqual(playlist[:1],
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.load_und_play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])
        # Endzeit == naechste Startzeit < ZEIT => Listen aendern, load_and_play Funktion
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit + 1000
        self.assertEqual(playlist[:1],
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.load_und_play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])
        # Endzeit < ZEIT < naechste Startzeit => Listen ungeaendert, leere Funktion
        playlist = playlist[1:]
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit + 1000
        self.assertLess(audiomodul.AUDIOOBJEKT_AKTIVE[-1].startzeit + 2000, playlist[0].startzeit, "Wirklich kleiner")
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])

    def test_play_audio_schedule_player_geladen_playlist_leer_endzeit(self):
        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = self.audio
        playlist = audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[1:-1]
        self.assertEqual(8, len(playlist))
        self.assertEqual([], audiomodul.AUDIOOBJEKT_AKTIVE)

        audiomodul.AUDIOOBJEKT_AKTIVE = playlist[:]
        playlist = []
        self.assertEqual(0, len(playlist))
        self.assertEqual(8, len(audiomodul.AUDIOOBJEKT_AKTIVE))

        # FADOUTZEIT < Zeit Endzeit => Listen ungeaendert, fadeout
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit - audiomodul.FADINGOUT_DAUER // 2
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.fadeout_musik,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])
        # FADOUTZEIT < Zeit Endzeit, nicht busy => Listen ungeaendert, play
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit - audiomodul.FADINGOUT_DAUER // 2
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=False)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=False)[1])
        self.assertEqual(audiomodul.play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=False)[2][0])
        # Zeit == Endzeit, busy => listen ungeaendert, mache_nichts
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])
        # Zeit == Endzeit, nicht busy => listen ungeaendert, mache_nichts
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=False)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=False)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=False)[2][0])
        # Endzeit < ZEIT => Listen ungeaendert, mache_nichts
        aktuelle_zeit = audiomodul.AUDIOOBJEKT_AKTIVE[-1].endzeit + 5000
        self.assertEqual(audiomodul.AUDIOOBJEKT_AKTIVE,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[0])
        self.assertEqual(playlist,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.mache_nichts,
                         audiomodul.play_audio_schedule(playlist=playlist,
                                                        aktuelle_zeit_in_ms=aktuelle_zeit,
                                                        busy_status=True)[2][0])
