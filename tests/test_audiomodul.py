from unittest import TestCase
from dataclasses import replace
from pygame.mixer import music
import time
import audiomodul
from trainingsprogramm import erzeuge_trainingsprogramm_Tabata, erzeuge_trainingsprogramm_G2Intervall


class test_Audiomodul(TestCase):
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
        audio = audiomodul.MEINE_AUDIO_OBJEKTE
        self.assertEqual(0, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))

        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = audiomodul.MEINE_AUDIO_OBJEKTE
        self.assertEqual(8, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))
        for index in range(8):
            self.assertEqual(600000 - 10000 + index * 30000,
                             audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[index][0])

        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = (audiomodul.MEINE_AUDIO_OBJEKTE +
                 [replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Ausfahren'])])
        self.assertEqual(9, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))

        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = (audiomodul.MEINE_AUDIO_OBJEKTE +
                 [replace(replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Ausfahren']), zeit_start=0),
                  replace(replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Warmfahren']), zeit_start=0),
                  replace(replace(audiomodul.MEINE_AUDIO_OBJEKTE[0], trainingsinhalt=['Irgendwas']), zeit_start=10000)])
        self.assertEqual(10, len(audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)))
        self.assertEqual(0,
                         audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[0][0])
        self.assertEqual(600000+8*30000,
                         audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)[-1][0])

    def test_play_audio_schedule(self):
        plan = erzeuge_trainingsprogramm_Tabata(pwm=(1, 3), cad=(100, 100))
        audio = audiomodul.MEINE_AUDIO_OBJEKTE
        playlist = audiomodul.build_playlist(trainingsplan=plan, audio_objekte=audio)
        self.assertEqual([], audiomodul.AUDIOOBJEKT_AKTIVE)
        self.assertNotEqual([], playlist)

        # Tests mit leereraudiomodul.AUDIOOBJEKT_AKTIVE
        self.assertEqual([], audiomodul.play_audio_schedule()[0])
        self.assertEqual([], audiomodul.play_audio_schedule()[1])
        self.assertEqual({}, audiomodul.play_audio_schedule()[2][1])
        self.assertEqual([playlist[0]], audiomodul.play_audio_schedule(playlist=playlist)[0])
        self.assertEqual(playlist[1:], audiomodul.play_audio_schedule(playlist=playlist)[1])
        self.assertEqual(audiomodul.load_musik, audiomodul.play_audio_schedule(playlist=playlist)[2][0])
        self.assertEqual({'objekt': playlist[0].objekt}, audiomodul.play_audio_schedule(playlist=playlist)[2][1])
        audiomodul.AUDIOOBJEKT_AKTIVE = audiomodul.play_audio_schedule(playlist=playlist)[0]
        self.assertEqual([playlist[0]],
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].startzeit + 5)[0])
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].startzeit + 5)[1])
        self.assertEqual(audiomodul.play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].startzeit + 5)[2][0])
        self.assertEqual({'position': 5/1000},
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].startzeit + 5)[2][1])

        # Der Player laeuft jetzt, deshalb wuerde music.get_busy() => True liefern
        self.assertEqual([playlist[0]],
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 1000,
                                                        busy_status=True)[0],)
        self.assertEqual(playlist[1:],
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 1000,
                                                        busy_status=True)[1])
        self.assertEqual(audiomodul.fadeout_musik,
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 1000,
                                                        busy_status=True)[2][0])
        self.assertEqual({'dauer': 1000},
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 1000,
                                                        busy_status=True)[2][1])

        # Der Player laeuft jetzt, deshalb wuerde music.get_busy() => True liefern
        self.assertEqual(playlist[0].endzeit, playlist[1].startzeit)
        self.assertEqual(playlist[:2],
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 0,
                                                        busy_status=True)[0],)
        self.assertEqual(playlist[2:],
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 0,
                                                        busy_status=True)[1])
        self.assertNotEqual(audiomodul.stop_musik,
                            audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                           aktuelle_zeit_in_ms=playlist[0].endzeit - 0,
                                                           busy_status=True)[2][0])
        self.assertEqual(audiomodul.play_musik,
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 0,
                                                        busy_status=True)[2][0])
        self.assertEqual({'position': 0},
                         audiomodul.play_audio_schedule(playlist=playlist[1:],
                                                        aktuelle_zeit_in_ms=playlist[0].endzeit - 0,
                                                        busy_status=True)[2][1])
