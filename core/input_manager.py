from pynput import keyboard

from core.settings_manager import (
    obter_voice_key,
    obter_gesture_key
)

ALT_PRESSIONADO = False
GESTO_PRESSIONADO = False


def tecla_corresponde(tecla, nome_tecla):

    try:

        if nome_tecla == "alt_l":

            return tecla == keyboard.Key.alt_l

        elif nome_tecla == "shift_l":

            return tecla == keyboard.Key.shift_l

        elif nome_tecla == "shift_r":

            return tecla == keyboard.Key.shift_r

        elif hasattr(tecla, "char"):

            return tecla.char == nome_tecla

    except:

        pass

    return False


def ao_pressionar(tecla):

    global ALT_PRESSIONADO
    global GESTO_PRESSIONADO

    voice_key = obter_voice_key()
    gesture_key = obter_gesture_key()

    if tecla_corresponde(tecla, voice_key):

        ALT_PRESSIONADO = True

    if tecla_corresponde(tecla, gesture_key):

        GESTO_PRESSIONADO = True


def ao_soltar(tecla):

    global ALT_PRESSIONADO
    global GESTO_PRESSIONADO

    voice_key = obter_voice_key()
    gesture_key = obter_gesture_key()

    if tecla_corresponde(tecla, voice_key):

        ALT_PRESSIONADO = False

    if tecla_corresponde(tecla, gesture_key):

        GESTO_PRESSIONADO = False


def iniciar_listener():

    listener = keyboard.Listener(
        on_press=ao_pressionar,
        on_release=ao_soltar
    )

    listener.daemon = True
    listener.start()


def alt_pressionado():

    return ALT_PRESSIONADO


def gesto_pressionado():

    return GESTO_PRESSIONADO