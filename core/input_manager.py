from pynput import keyboard

from core.settings_manager import (
    obter_voice_key,
    obter_gesture_key
)

VOICE_PRESSIONADO = False
GESTO_PRESSIONADO = False


MAPA_TECLAS = {
    "alt_l": keyboard.Key.alt_l,
    "alt_r": keyboard.Key.alt_r,

    "ctrl_l": keyboard.Key.ctrl_l,
    "ctrl_r": keyboard.Key.ctrl_r,

    "shift_l": keyboard.Key.shift_l,
    "shift_r": keyboard.Key.shift_r,

    "f7": keyboard.Key.f7,
    "f8": keyboard.Key.f8,
    "f9": keyboard.Key.f9,
    "f10": keyboard.Key.f10,
    "f11": keyboard.Key.f11,
    "f12": keyboard.Key.f12
}


def ativar_voz():

    global VOICE_PRESSIONADO

    VOICE_PRESSIONADO = True


def desativar_voz():

    global VOICE_PRESSIONADO

    VOICE_PRESSIONADO = False


def ativar_gesto():

    global GESTO_PRESSIONADO

    GESTO_PRESSIONADO = True


def desativar_gesto():

    global GESTO_PRESSIONADO

    GESTO_PRESSIONADO = False


def tecla_corresponde(tecla, nome_tecla):

    try:

        nome_tecla = nome_tecla.lower()

        if nome_tecla in MAPA_TECLAS:

            return tecla == MAPA_TECLAS[nome_tecla]

        if hasattr(tecla, "char"):

            return (
                tecla.char
                and
                tecla.char.lower() == nome_tecla
            )

    except:
        pass

    return False


def ao_pressionar(tecla):

    global VOICE_PRESSIONADO
    global GESTO_PRESSIONADO

    voice_key = obter_voice_key()
    gesture_key = obter_gesture_key()

    if tecla_corresponde(
        tecla,
        voice_key
    ):

        VOICE_PRESSIONADO = True

    if tecla_corresponde(
        tecla,
        gesture_key
    ):

        GESTO_PRESSIONADO = True


def ao_soltar(tecla):

    global VOICE_PRESSIONADO
    global GESTO_PRESSIONADO

    voice_key = obter_voice_key()
    gesture_key = obter_gesture_key()

    if tecla_corresponde(
        tecla,
        voice_key
    ):

        VOICE_PRESSIONADO = False

    if tecla_corresponde(
        tecla,
        gesture_key
    ):

        GESTO_PRESSIONADO = False


def iniciar_listener():

    listener = keyboard.Listener(
        on_press=ao_pressionar,
        on_release=ao_soltar
    )

    listener.daemon = True

    listener.start()


def alt_pressionado():

    return VOICE_PRESSIONADO


def gesto_pressionado():

    return GESTO_PRESSIONADO