import json

ARQUIVO = "config/plugins.json"


def carregar():

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(
                arquivo
            )

    except:

        return {}


def salvar(dados):

    with open(
        ARQUIVO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            indent=4
        )


def ativar(nome):

    dados = carregar()

    dados[nome] = True

    salvar(dados)


def desativar(nome):

    dados = carregar()

    dados[nome] = False

    salvar(dados)