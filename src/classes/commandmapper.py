from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from dataclasses import dataclass, field, replace
import src.modules.audiomodul as audio
import pygame

if TYPE_CHECKING:
    from src.classes.controllerstatus import ControllerStatus
    from src.classes.ergometer import Ergometer


# ----------------------
# Kommandos
def beende_programm(status: ControllerStatus) -> None:
    status.modell.board.sendeUndLeseWerte(0)


def bremsePlusPlus(status: ControllerStatus) -> Ergometer:
    return status.modell.ergo.bremsePlusPlus(name=status.werte_nach_trainngsplan[0])


def bremsePlus(status: ControllerStatus) -> Ergometer:
    return status.modell.ergo.bremsePlus(name=status.werte_nach_trainngsplan[0])


def bremseMinusMinus(status: ControllerStatus) -> Ergometer:
    return status.modell.ergo.bremseMinusMinus(name=status.werte_nach_trainngsplan[0])


def bremseMinus(status: ControllerStatus) -> Ergometer:
    return status.modell.ergo.bremseMinus(name=status.werte_nach_trainngsplan[0])


def resetBremswertkorrektur(status: ControllerStatus) -> Ergometer:
    return status.modell.ergo.loesche_bremswertkorrektur(name=status.werte_nach_trainngsplan[0])


def resetAlleBremswertkorrekturen(status: ControllerStatus) -> Ergometer:
    return status.modell.ergo.loesche_bremswertkorrektur(name=None)


def pause_mit_zeit(status: ControllerStatus) -> None:
    if status.modell.uhr.macht_pause():
        status.modell.uhr = status.modell.uhr.start(status.modell.millis_jetzt())
    else:
        status.modell.uhr = status.modell.uhr.pause(status.modell.millis_jetzt())


def pause_nach_inhalt(status: ControllerStatus) -> None:
    status.pause_nach_aktuellem_inhalt = not status.pause_nach_aktuellem_inhalt


def change_unendlich_status_in_trainingsprogramm(status: ControllerStatus) -> None:
    status.modell.trainingsprogramm = replace(status.modell.trainingsprogramm,
                                              unendlich=not status.modell.trainingsprogramm.unendlich)


@dataclass(frozen=True)
class CommandMapper:
    command_string: str = field(default_factory=str)
    key_bindings: list[int] | list[(int, int)] = field(default_factory=list)
    flask_route: str | None = field(default_factory=str)
    funktion: Callable = field(default=lambda: None)
    kwargs: dict = field(default_factory=dict)


# K_KP... = Keypadtasten
# NumLock => KMOD_NUM = 4096    als Modifier
# WICHTIG !!! ctrl+alt+key wird nicht erkannt.
# Aber ctrl+shift, alt+shift, NumLock+Alt+Shift+key etc wird erkannt.
"""kwargs={'status': True}: Die Funktion benutzt das status-Argument in command_mapper() siehe unten."""
COMMANDS = [
    CommandMapper(command_string="QUIT", key_bindings=[pygame.K_q],
                  flask_route=None, funktion=beende_programm, kwargs={'status': True}),
    CommandMapper(command_string="PWM++", key_bindings=[pygame.K_UP, pygame.K_KP8],
                  flask_route='pwm_plusplus', funktion=bremsePlusPlus, kwargs={'status': True}),
    CommandMapper(command_string="PWM+", key_bindings=[pygame.K_RIGHT, pygame.K_KP6],
                  flask_route='pwm_plus', funktion=bremsePlus, kwargs={'status': True}),
    CommandMapper(command_string="PWM--", key_bindings=[pygame.K_DOWN, pygame.K_KP2],
                  flask_route='pwm_minusminus', funktion=bremseMinusMinus, kwargs={'status': True}),
    CommandMapper(command_string="PWM-", key_bindings=[pygame.K_LEFT, pygame.K_KP4],
                  flask_route='pwm_minus', funktion=bremseMinus, kwargs={'status': True}),
    CommandMapper(command_string="RESET_BREMSKORREKTUR", key_bindings=[pygame.K_KP5, pygame.K_BACKSPACE],
                  flask_route=None, funktion=resetBremswertkorrektur, kwargs={'status': True}),
    CommandMapper(command_string="RESET_BREMSKORREKTUR_ALL", key_bindings=[(pygame.KMOD_RSHIFT, pygame.K_BACKSPACE),
                                                                           (pygame.KMOD_RSHIFT, pygame.K_KP5)],
                  flask_route=None, funktion=resetAlleBremswertkorrekturen, kwargs={'status': True}),
    CommandMapper(command_string="PAUSE", key_bindings=[pygame.K_p, pygame.K_SPACE, pygame.K_KP_ENTER],
                  flask_route='pause', funktion=pause_mit_zeit, kwargs={'status': True}),
    CommandMapper(command_string="MUSIK_MUTE", key_bindings=[pygame.K_m, pygame.K_KP_PERIOD],
                  flask_route='musik_mute', funktion=audio.mute, kwargs={}),
    CommandMapper(command_string="MUSIK_LAUTER", key_bindings=[pygame.K_KP_MULTIPLY],
                  flask_route=None, funktion=audio.lauter, kwargs={}),
    CommandMapper(command_string="MUSIK_LEISER", key_bindings=[pygame.K_KP_DIVIDE],
                  flask_route=None, funktion=audio.leiser, kwargs={}),
    CommandMapper(command_string="PAUSE_NACH_INHALT", key_bindings=[pygame.K_e],
                  flask_route='pause_nach_inhalt', funktion=pause_nach_inhalt, kwargs={'status': True}),
    CommandMapper(command_string="CHANGE_TRANINGSPROGRAMM_UNENDLICH",
                  key_bindings=[(pygame.KMOD_SHIFT, pygame.K_e),
                                (pygame.KMOD_LSHIFT, pygame.K_e),
                                (pygame.KMOD_RSHIFT, pygame.K_e)],
                  flask_route='change_trainigsprogramm_unendlich',
                  funktion=change_unendlich_status_in_trainingsprogramm, kwargs={'status': True}),
]

ALLE_SHIFT_MODIFIER = [pygame.KMOD_SHIFT, pygame.KMOD_LSHIFT, pygame.KMOD_RSHIFT]


def key_mapper(key: int, modifier: int = 0) -> str:
    # Ohne Modifier werden zu (0, key) umgewandelt
    key_bindings = {(modifier, taste): commando.command_string
                    for commando in COMMANDS
                    for key in commando.key_bindings
                    for modifier, taste in ([key] if isinstance(key, tuple) else [(0, key)])}
    return key_bindings.get((modifier, key), "")


def command_mapper(status: ControllerStatus) -> Callable:
    # Das Komando besteht aus einem tupel[Callable, dict[args]]
    command_map = {commando.command_string: (commando.funktion,
                                             commando.kwargs | ({'status': status} if
                                                                commando.kwargs.get('status', False)
                                                                else {}))
                   for commando
                   in COMMANDS}
    return command_map.get(status.gedrueckte_taste, lambda: None)
