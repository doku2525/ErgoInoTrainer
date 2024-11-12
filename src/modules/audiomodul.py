from typing import Callable
from collections import namedtuple
import pygame.mixer
from pygame.mixer import music

from src.classes.audioobjekt import AudioObjekt
from src.classes.trainingsprogramm import Trainingsprogramm
from src.classes.trainingsinhalt import Trainingsinhalt


PlaylistAudioObjekt = namedtuple('PlaylistAudioObjekt', ['startzeit', 'endzeit', 'objekt'])

pygame.mixer.init()

AUDIO_VOLUME: float = float(music.get_volume())
AUDIO_VOLUME_FADINGOUT: bool = False
AUDIOOBJEKT_AKTIVE: list[PlaylistAudioObjekt] = list()
MEINE_AUDIO_OBJEKTE: list[AudioObjekt] = [
    AudioObjekt(filename='../../media/sounds/tabata.wav', trainingsplan=['Tabata'],
                trainingsinhalt=['Intervall'], zeit_start=-10000, dauer=30000, prioritaet=(100, 50))
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


def load_und_play_musik(objekt: AudioObjekt, position: int = 0) -> bool:
    music.load(objekt.filename)
    music.play(0, position)
    return music.get_busy()


def fadeout_musik(dauer: int = 1000) -> bool:
    if not AUDIO_VOLUME_FADINGOUT:
        music.fadeout(dauer)
    return music.get_busy()


def stop_musik() -> bool:
    music.stop()
    return music.get_busy()


def stop_und_play_musik(position) -> bool:
    music.stop()
    music.play(0)
    return music.get_busy()


def play_musik(position) -> bool:
    music.play(0)
    return music.get_busy()


def build_playlist(trainingsplan: Trainingsprogramm,
                   audio_objekte: list[AudioObjekt]) -> list[PlaylistAudioObjekt]:
    """
    Liefert Liste mit (startzeit, AudioObjekt) sortiert nach Startzeit
    :param trainingsplan: Traingsplan
    :param audio_objekte: AudioObjekt
    :return: (startzeit: int, AudioObjekt)
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
                        aktuelle_zeit_in_ms: int = 0,
                        busy_status: bool = False) -> (list[PlaylistAudioObjekt],
                                                       list[PlaylistAudioObjekt],
                                                       (Callable, dict)):
    def aktuelles_objekt_beendet() -> tuple[Callable, dict]:
        if playlist[0].objekt == AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms >= playlist[0].startzeit:
            return play_musik, {'position': (aktuelle_zeit_in_ms - playlist[0].startzeit)/1000}
        if playlist[0].objekt == AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms < playlist[0].startzeit:
            return lambda: None, {}
        if playlist[0].objekt != AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms >= playlist[0].startzeit:
            return load_und_play_musik, {'objekt': playlist[0].objekt,
                                         'position': (aktuelle_zeit_in_ms - playlist[0].startzeit) / 1000}
        if playlist[0].objekt != AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms < playlist[0].startzeit:
            return load_musik, {'objekt': playlist[0].objekt}

    if not playlist:              # Leere Playliste mache nicht. Wenn Music laeuft, dann laeuft sie weiter
        return AUDIOOBJEKT_AKTIVE, [], (lambda: None, {})
    if not AUDIOOBJEKT_AKTIVE and busy_status:
        raise RuntimeError("Musicplayer beschaeftig, obwohl kein Objekt geladen wurde.")
    if not AUDIOOBJEKT_AKTIVE and not busy_status and aktuelle_zeit_in_ms < playlist[0].startzeit:
        return playlist[:1], playlist[1:], (load_musik, {'objekt': playlist[0].objekt})
    if not AUDIOOBJEKT_AKTIVE and not busy_status and aktuelle_zeit_in_ms > playlist[0].startzeit:
        return playlist[:1], playlist[1:], (load_und_play_musik,
                                            {'objekt': playlist[0].objekt,
                                             'position': (aktuelle_zeit_in_ms - playlist[0].startzeit) / 1000})
    if AUDIOOBJEKT_AKTIVE and busy_status and aktuelle_zeit_in_ms >= AUDIOOBJEKT_AKTIVE[-1].endzeit:
        return AUDIOOBJEKT_AKTIVE + playlist[:1], playlist[1:], aktuelles_objekt_beendet()
    if AUDIOOBJEKT_AKTIVE and busy_status and aktuelle_zeit_in_ms >= AUDIOOBJEKT_AKTIVE[-1].endzeit - 1000:
        return AUDIOOBJEKT_AKTIVE, playlist, (fadeout_musik,
                                              {'dauer': int(AUDIOOBJEKT_AKTIVE[-1].endzeit - aktuelle_zeit_in_ms)})
    if AUDIOOBJEKT_AKTIVE and busy_status and aktuelle_zeit_in_ms < AUDIOOBJEKT_AKTIVE[-1].endzeit:
        return AUDIOOBJEKT_AKTIVE, playlist, (lambda: None, {})
    if AUDIOOBJEKT_AKTIVE and not busy_status and aktuelle_zeit_in_ms < AUDIOOBJEKT_AKTIVE[-1].startzeit:
        return AUDIOOBJEKT_AKTIVE, playlist, (lambda: None, {})
    if AUDIOOBJEKT_AKTIVE and not busy_status and aktuelle_zeit_in_ms >= AUDIOOBJEKT_AKTIVE[-1].startzeit:
        return (AUDIOOBJEKT_AKTIVE, playlist,
                (play_musik, {'position': (aktuelle_zeit_in_ms - AUDIOOBJEKT_AKTIVE[-1].startzeit) / 1000}))
