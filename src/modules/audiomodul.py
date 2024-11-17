from typing import Callable
from collections import namedtuple
import pygame.mixer
from pygame.mixer import music

from src.classes.audioobjekt import AudioObjekt
from src.classes.trainingsprogramm import Trainingsprogramm
from src.classes.trainingsinhalt import Trainingsinhalt


PlaylistAudioObjekt = namedtuple('PlaylistAudioObjekt', ['startzeit', 'endzeit', 'objekt'])

pygame.mixer.init()

FADINGOUT_DAUER = 500
AUDIO_VOLUME: float = float(music.get_volume())
AUDIO_VOLUME_FADINGOUT: bool = False
AUDIOOBJEKT_AKTIVE: list[PlaylistAudioObjekt] = list()
MEINE_AUDIO_OBJEKTE: list[AudioObjekt] = [
    AudioObjekt(filename='media/sounds/tabata.wav', trainingsplan=['Tabata'], trainingsinhalt=['Intervall'],
                zeit_start=-10000, dauer=30000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/01 Hello (Club Edit).mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Warmfahren'],
                zeit_start=361000+700, dauer=333000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/07 - 木綿のハンカチーフ.mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Warmfahren'],
                zeit_start=500, dauer=361000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/松崎ナオ - 川べりの家.mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Ausfahren'],
                zeit_start=-9100, dauer=175000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/05 - Beautiful Sa.mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Ausfahren'],
                zeit_start=175000-9000, dauer=276000, prioritaet=(100, 50))
]


def lautstaerke(neuer_wert: float | None = None) -> float:
    if neuer_wert is not None:
        music.set_volume(neuer_wert if neuer_wert >= 0 else 0)
    volume = music.get_volume()
    return round((volume // 0.05 + (0 if volume % 0.05 <= 0.025 else 1)) * 0.05, 2)


def lauter() -> float:
    music.set_volume(lautstaerke() + 0.05 if 0 <= lautstaerke() + 0.05 else 0)
    return lautstaerke()


def leiser() -> float:
    music.set_volume(lautstaerke() - 0.05 if 0 <= lautstaerke() - 0.05 else 0)
    return lautstaerke()


def mute() -> float:
    volume = lautstaerke()
    if volume == 0:
        music.set_volume(AUDIO_VOLUME)
    else:
        music.set_volume(0)
    return AUDIO_VOLUME


def load_musik(objekt: AudioObjekt) -> bool:
    music.load(objekt.filename)
    return music.get_busy()


def load_und_play_musik(objekt: AudioObjekt, position: float = 0.0, loops: int = 0) -> bool:
    music.load(objekt.filename)
    music.play(loops=loops, start=position)
    return music.get_busy()


def fadeout_musik() -> bool:
    if not AUDIO_VOLUME_FADINGOUT:
        music.fadeout(FADINGOUT_DAUER)
    return music.get_busy()


def stop_musik() -> bool:
    music.stop()
    return music.get_busy()


def stop_und_play_musik(position: float = 0.0, loops: int = 0) -> bool:
    music.stop()
    music.play(loops=loops, start=position)
    return music.get_busy()


def play_musik(position: float = 0.0, loops: int = 0) -> bool:
    music.play(loops=loops, start=position)
    return music.get_busy()


def mache_nichts() -> bool:
    return music.get_busy()


def build_playlist(trainingsplan: Trainingsprogramm,
                   audio_objekte: list[AudioObjekt]) -> list[PlaylistAudioObjekt]:
    """
    Liefert Liste mit (startzeit, AudioObjekt) sortiert nach Startzeit
    :param trainingsplan: Traingsplan
    :param audio_objekte: AudioObjekt
    :return: list[namedTuple[startzeit: int, endzeit: int, AudioObjekt)
    """
    # Definiere Hilfsfunktion, die fuer jedes Audioobjekt die totalen Startzeiten ermittelt
    def calc_startzeit_fuer_objekt(liste: list[Trainingsinhalt],
                                   audio_obj: AudioObjekt) -> list[PlaylistAudioObjekt]:
        liste_mit_gesamtzeiten = [element.dauer() for element in liste]
        return [PlaylistAudioObjekt(startzeit=sum(liste_mit_gesamtzeiten[:index]) + audio_obj.zeit_start,
                                    endzeit=(sum(liste_mit_gesamtzeiten[:index]) + audio_obj.zeit_start +
                                             audio_obj.dauer),
                                    objekt=audio_obj)
                for index, element
                in enumerate(liste) if element.name in audio_obj.trainingsinhalt]

    return sorted([result_tuple
                   for sublist in (calc_startzeit_fuer_objekt(trainingsplan.inhalte, current_audio)
                                   for current_audio        # Erstelle Liste mit der Funktion fuer jedes Audioobjekt
                                   in [a_objekt             # Filter Audios nach Traingsplanname
                                       for a_objekt
                                       in audio_objekte if trainingsplan.name in a_objekt.trainingsplan])
                   for result_tuple in sublist])            # Erzeuge Flache Liste


def play_audio_schedule(playlist: list[PlaylistAudioObjekt] = None,
                        aktuelle_zeit_in_ms: int = 0, busy_status: bool = False) -> (list[PlaylistAudioObjekt],
                                                                                     list[PlaylistAudioObjekt],
                                                                                     (Callable, dict)):

    # bool-Hilfsunktionen, um Zustand zu testen
    def alle_listen_leer() -> bool:
        return not playlist and not AUDIOOBJEKT_AKTIVE

    def player_geladen() -> bool:
        return AUDIOOBJEKT_AKTIVE != []

    def player_spielt() -> bool:
        return busy_status

    def vorAktuellerStartzeit(zeitverschiebung: int = 0) -> bool:
        return aktuelle_zeit_in_ms < AUDIOOBJEKT_AKTIVE[-1].startzeit + zeitverschiebung

    def vorAktuellerEndzeit(zeitverschiebung: int = 0) -> bool:
        return aktuelle_zeit_in_ms < AUDIOOBJEKT_AKTIVE[-1].endzeit + zeitverschiebung

    def vorNaechsterStartzeit(zeitverschiebung: int = 0) -> bool:
        return playlist and aktuelle_zeit_in_ms < playlist[0][0] + zeitverschiebung

    def zeit_fuer_Fadeout() -> bool:
        # Fadeout-Bedingungen geladen und spielt
        return (player_geladen() and player_spielt() and             # 3 mal or Verbindung
                ((not vorAktuellerStartzeit(-FADINGOUT_DAUER) and vorAktuellerStartzeit()) or
                 (not vorAktuellerEndzeit(-FADINGOUT_DAUER) and vorAktuellerEndzeit()) or
                 (not vorNaechsterStartzeit(-FADINGOUT_DAUER) and vorNaechsterStartzeit()))
                )

    def zeit_fuer_load_and_play() -> bool:
        # load_play-Bedingungen playlist_voll and nach der naechsten Startzeit
        return ((player_geladen() or not player_geladen()) and          # Egal, ob geladen oder nicht
                (player_spielt() or not player_spielt()) and
                playlist and                                            # Ohne playlist kann nicht geladen werden
                ((not player_spielt() and not vorNaechsterStartzeit()) or
                 (player_spielt() and not vorNaechsterStartzeit())))

    def zeit_fuer_play() -> bool:
        # play-Bedingungen geladen + spielt nicht + nach aktueller Startzeit + nicht vor Endzeit
        return (player_geladen() and not player_spielt() and
                not vorAktuellerStartzeit() and vorAktuellerEndzeit())

    def zeit_fuer_load() -> bool:
        # laden-Bedingungen: playliste + spielt() nicht + nach aktueller Endzeit + vor naechster Startzeit
        return (playlist and not player_spielt() and
                ((not player_geladen() and vorNaechsterStartzeit()) or
                 (player_geladen() and not vorAktuellerEndzeit() and vorNaechsterStartzeit()))
                )

    # ---------------------
    # ----- Begin Hauptteil
    # TODO Wenn aktuelle Zeit nicht laeuft, wird nach dem Liedende immer wieder play fuer aktuelle Lied aufgerufen.
    #       Playlist wird nicht veraendert.
    # TODO Wenn das Liedende vor endzeit beendet, also not busy, startet das Lied wieder. Bis endzeit erreicht ist.
    #       Verhalten kann evt. durch ermitteln der Liedlaenge verbessert werden.
    # TODO Sie TODOs in AudioObjekt
    if alle_listen_leer():                                 # Mache NICHTS
        return AUDIOOBJEKT_AKTIVE, [], (mache_nichts, {})
    if not player_geladen() and player_spielt():           # FEHLER! Player wird vor Start von anderem Prozess benutzt?
        raise RuntimeError("Musikplayer beschaeftig, obwohl kein Objekt geladen wurde.")
    if zeit_fuer_load():
        return (playlist[:1], playlist[1:],
                (load_musik, {'objekt': playlist[0].objekt}))
    if zeit_fuer_load_and_play():
        return (playlist[:1], playlist[1:],
                (load_und_play_musik, {'objekt': playlist[0].objekt,
                                       'position': (aktuelle_zeit_in_ms - playlist[0].startzeit) / 1000,
                                       'loops': playlist[0].objekt.loops}))
    if zeit_fuer_play():
        return (AUDIOOBJEKT_AKTIVE, playlist,
                (play_musik, {'position': (aktuelle_zeit_in_ms - AUDIOOBJEKT_AKTIVE[-1].startzeit) / 1000,
                              'loops': AUDIOOBJEKT_AKTIVE[-1].objekt.loops}))
    if zeit_fuer_Fadeout():
        return (AUDIOOBJEKT_AKTIVE, playlist,
                (fadeout_musik, {}))
    # Mache nichts
    return AUDIOOBJEKT_AKTIVE, playlist, (mache_nichts, {})
