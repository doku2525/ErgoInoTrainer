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
    AudioObjekt(filename='media/sounds/tabata.wav', trainingsplan=['Tabata'], trainingsinhalt=['Intervall'],
                zeit_start=-10000, dauer=30000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/01 Hello (Club Edit).mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Warmfahren'],
                zeit_start=361000+700, dauer=333000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/07 - 木綿のハンカチーフ.mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Warmfahren'],
                zeit_start=500, dauer=361000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/08 - Green Tea.mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Ausfahren'],
                zeit_start=-8000, dauer=179000, prioritaet=(100, 50)),
    AudioObjekt(filename='media/sounds/05 - Beautiful Sa.mp3',
                trainingsplan=['Tabata'], trainingsinhalt=['Ausfahren'],
                zeit_start=179000-7000, dauer=276000, prioritaet=(100, 50))

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
    print(f"Load: {objekt.filename}")
    music.load(objekt.filename)
    return music.get_busy()


def load_und_play_musik(objekt: AudioObjekt, position: int = 0, loops: int = 0) -> bool:
    print(f"Loops: {loops} LPM")
    music.load(objekt.filename)
    music.play(loops, position)
    return music.get_busy()


def fadeout_musik(dauer: int = 1000) -> bool:
    if not AUDIO_VOLUME_FADINGOUT:
        music.fadeout(dauer)
    return music.get_busy()


def stop_musik() -> bool:
    music.stop()
    return music.get_busy()


def stop_und_play_musik(position, loops: int = 0) -> bool:
    print(f"Loops: {loops} SPM")
    music.stop()
    music.play(loops, 0)
    return music.get_busy()


def play_musik(position, loops: int = 0) -> bool:
    print(f"Loops: {loops} PM")
    music.play(loops, 0)
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
                        aktuelle_zeit_in_ms: int = 0, busy_status: bool = False) -> (list[PlaylistAudioObjekt],
                                                                                     list[PlaylistAudioObjekt],
                                                                                     (Callable, dict)):
    def aktuelles_objekt_beendet() -> tuple[Callable, dict]:
        if playlist[0].objekt == AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms >= playlist[0].startzeit:
            print("aktuelles_objekt_beendet")
            return play_musik, {'position': (aktuelle_zeit_in_ms - playlist[0].startzeit)/1000,
                                'loops': playlist[0].objekt.loops}
        if playlist[0].objekt == AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms < playlist[0].startzeit:
            return lambda: None, {}
        if playlist[0].objekt != AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms >= playlist[0].startzeit:
            return load_und_play_musik, {'objekt': playlist[0].objekt,
                                         'position': (aktuelle_zeit_in_ms - playlist[0].startzeit) / 1000,
                                         'loops': playlist[0].objekt.loops}
        if playlist[0].objekt != AUDIOOBJEKT_AKTIVE[-1].objekt and aktuelle_zeit_in_ms < playlist[0].startzeit:
            return load_musik, {'objekt': playlist[0].objekt}

    # bool-Funktionen um Zustand zu testen
    def leere_listen() -> bool:
        return not playlist and not AUDIOOBJEKT_AKTIVE

    def nochKeinObjektGeladen_PlayerBesetzt() -> bool:
        return not AUDIOOBJEKT_AKTIVE and busy_status

    def nochKeinObjektGeladen_PlayerFrei() -> bool:
        return not AUDIOOBJEKT_AKTIVE and not busy_status

    def nochKeinObjektGeladen_PlayerFrei_vorStartzeit() -> bool:
        return nochKeinObjektGeladen_PlayerFrei() and aktuelle_zeit_in_ms < playlist[0].startzeit

    def nochKeinObjektGeladen_PlayerFrei_nachStartzeit() -> bool:
        return nochKeinObjektGeladen_PlayerFrei() and aktuelle_zeit_in_ms >= playlist[0].startzeit

    def objektGeladen_PlayerFrei() -> bool:
        return AUDIOOBJEKT_AKTIVE and not busy_status

    def objektGeladen_PlayerFrei_vorStartzeit() -> bool:
        return objektGeladen_PlayerFrei() and aktuelle_zeit_in_ms < AUDIOOBJEKT_AKTIVE[-1].startzeit

    def objektGeladen_PlayerFrei_nachStartzeit() -> bool:
        return objektGeladen_PlayerFrei() and aktuelle_zeit_in_ms >= AUDIOOBJEKT_AKTIVE[-1].startzeit

    def objektGeladen_PlayerBesetzt() -> bool:
        return AUDIOOBJEKT_AKTIVE and busy_status

    def objektGeladen_PlayerBesetzt_vorEndzeit() -> bool:
        return objektGeladen_PlayerBesetzt() and aktuelle_zeit_in_ms < AUDIOOBJEKT_AKTIVE[-1].endzeit

    def objektGeladen_PlayerBesetzt_imFadeoutbereich() -> bool:
        return objektGeladen_PlayerBesetzt() and aktuelle_zeit_in_ms >= AUDIOOBJEKT_AKTIVE[-1].endzeit - 1000

    def objektGeladen_PlayerBesetzt_nachEndzeit() -> bool:
        return objektGeladen_PlayerBesetzt() and aktuelle_zeit_in_ms >= AUDIOOBJEKT_AKTIVE[-1].endzeit

    def objektGeladen_PlayerBesetzt_nachEndzeit_vorNaechster():
        return objektGeladen_PlayerBesetzt_nachEndzeit() and aktuelle_zeit_in_ms < playlist[0].startzeit

    def objektGeladen_PlayerBesetzt_nachEndzeit_nachNaechster():
        return not objektGeladen_PlayerBesetzt_nachEndzeit_vorNaechster()

    # ----- Begin
    # TODO Benutze anderen Variablennamen: (playerUnloaded,playerLoaded), (playerBusy,playerNotbusy)
    # ---- Player leer
    if leere_listen():                                                # Mache NICHTS
        print(f"leere_listen()")
        return AUDIOOBJEKT_AKTIVE, [], (lambda: None, {})
    if nochKeinObjektGeladen_PlayerBesetzt():                           # FEHLER! Player wird von anderem benutzt
        raise RuntimeError("Musicplayer beschaeftig, obwohl kein Objekt geladen wurde.")
    if nochKeinObjektGeladen_PlayerFrei_vorStartzeit():                 # Lade Musik und warte
        return (playlist[:1], playlist[1:],
                (load_musik, {'objekt': playlist[0].objekt}))
    if nochKeinObjektGeladen_PlayerFrei_nachStartzeit():                # Lade Musik und Starte gleich
        return (playlist[:1], playlist[1:],
                (load_und_play_musik, {'objekt': playlist[0].objekt,
                                       'position': (aktuelle_zeit_in_ms - playlist[0].startzeit) / 1000,
                                       'loops': playlist[0].objekt.loops}))

    # ---- Player Beschaeftigt
    # Neues Lied muss beginnen. Hier kann spaeter die prioritaet mit eingebaut werden.
    # TODO zweiten Vergleich in oberen Funktionen einbauen
    if objektGeladen_PlayerBesetzt() and playlist and aktuelle_zeit_in_ms > playlist[0][0]:
        print(f"objektGeladen_PlayerBesetzt() and aktuelle_zeit_in_ms > playlist[0][0]")
        return (AUDIOOBJEKT_AKTIVE + playlist[:1], playlist[1:],
                aktuelles_objekt_beendet())
    # Die Zeit ist abgelaufen, aber das Lied spielt noch. wenn loops nicht in [0,1], die Listen verschieben aber
    # als Funktion nichts machen
    # TODO zweiten Vergleich in oberen Funktionen einbauen
    if (objektGeladen_PlayerBesetzt_nachEndzeit() and playlist and
            not AUDIOOBJEKT_AKTIVE[-1].objekt.loops in [0, 1]):                 # Evtl. in Loop, Listen verschieben
        print(f"objektGeladen_PlayerBesetzt_nachEndzeit nicht in loop")
        return (AUDIOOBJEKT_AKTIVE + playlist[:1], playlist[1:],(lambda:None,{}))
    # Die Zeit ist abgelaufen und objekt ist nicht in loops-modus, also beenden
    # TODO zweiten Vergleich in oberen Funktionen einbauen
    # TODO Ist dieser Test wirklich sinnvoll?
    if (objektGeladen_PlayerBesetzt_nachEndzeit() and playlist and
            AUDIOOBJEKT_AKTIVE[-1].objekt.loops in [0, 1]):                     # Evtl. in Loop, Listen verschieben
        print(f"objektGeladen_PlayerBesetzt_nachEndzeit nicht in loop")
        return (AUDIOOBJEKT_AKTIVE + playlist[:1], playlist[1:],
                aktuelles_objekt_beendet())
    # Wuerde Fadeout starten, wenn nicht loops waere
    # TODO zweiten Vergleich in oberen Funktionen einbauen
    if (objektGeladen_PlayerBesetzt_imFadeoutbereich() and
            not AUDIOOBJEKT_AKTIVE[-1].objekt.loops in [0, 1]):                  # FadeoutBereich, aber da loops NICHTS
        return (AUDIOOBJEKT_AKTIVE, playlist,
                (lambda: None, {}))
    # Beginne Fadeout
    # TODO zweiten Vergleich in oberen Funktionen einbauen
    if (objektGeladen_PlayerBesetzt_imFadeoutbereich() and
            AUDIOOBJEKT_AKTIVE[-1].objekt.loops in [0, 1]):                      # Starte Fadeout
        print(f"objektGeladen_PlayerBesetzt_imFadeoutbereich Nicht loop")
        return (AUDIOOBJEKT_AKTIVE, playlist,
                (fadeout_musik, {'dauer': int(AUDIOOBJEKT_AKTIVE[-1].endzeit - aktuelle_zeit_in_ms)}))
    # !!Standardmodus!! Spiele Musik innerhalb meiner zugewiesenen Zeit. Keine Aktion
    if objektGeladen_PlayerBesetzt_vorEndzeit():                                 # Mache NICHTS
        return AUDIOOBJEKT_AKTIVE, playlist, (lambda: None, {})

    # ---- Player frei
    if objektGeladen_PlayerFrei_vorStartzeit():                         # Mache NICHTS
        return AUDIOOBJEKT_AKTIVE, playlist, (lambda: None, {})
    if objektGeladen_PlayerFrei_nachStartzeit() :                        # Starte Player
        print(f"objektGeladen_PlayerFrei_nachStartzeit")
        return (AUDIOOBJEKT_AKTIVE, playlist,
                (play_musik, {'position': (aktuelle_zeit_in_ms - AUDIOOBJEKT_AKTIVE[-1].startzeit) / 1000,
                              'loops': AUDIOOBJEKT_AKTIVE[-1].objekt.loops}))
