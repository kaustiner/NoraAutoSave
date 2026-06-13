import json

ARQUIVO = "config/gestures.json"


def carregar_gestos():

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {}


def salvar_gestos(dados):

    with open(
        ARQUIVO,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dados,
            f,
            indent=4,
            ensure_ascii=False
        )


def adicionar_gesto(nome):

    dados = carregar_gestos()

    if nome not in dados:

        dados[nome] = ""

    salvar_gestos(dados)


def definir_plugin(
    gesto,
    plugin
):

    dados = carregar_gestos()

    dados[gesto] = plugin

    salvar_gestos(dados)


def remover_gesto(gesto):

    dados = carregar_gestos()

    if gesto in dados:

        del dados[gesto]

    salvar_gestos(dados)


def obter_plugin(gesto):

    dados = carregar_gestos()

    return dados.get(
        gesto
    )