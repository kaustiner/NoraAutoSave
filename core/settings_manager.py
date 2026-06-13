import json

CONFIG_PATH = "config/settings.json"


def carregar_config():

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(
            arquivo
        )


def salvar_config(config):

    with open(
        CONFIG_PATH,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            config,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


def obter_voice_key():

    config = carregar_config()

    return config.get(
        "voice_key",
        "alt_l"
    )


def obter_gesture_key():

    config = carregar_config()

    return config.get(
        "gesture_key",
        "f8"
    )


def definir_voice_key(tecla):

    config = carregar_config()

    config["voice_key"] = tecla

    salvar_config(config)


def definir_gesture_key(tecla):

    config = carregar_config()

    config["gesture_key"] = tecla

    salvar_config(config)