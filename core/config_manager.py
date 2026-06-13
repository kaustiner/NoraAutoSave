import json

ARQUIVO = "config/plugins.json"


def carregar():

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {}


def plugin_ativo(nome):

    dados = carregar()

    return dados.get(
        nome,
        True
    )