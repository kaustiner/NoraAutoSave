import json
import os

ARQUIVO = "data/agenda/lembretes.json"


def carregar():

    if not os.path.exists(ARQUIVO):
        return []

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

        return []


def salvar(lembretes):

    os.makedirs(
        "data/agenda",
        exist_ok=True
    )

    with open(
        ARQUIVO,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            lembretes,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def adicionar(lembrete):

    lembretes = carregar()

    lembretes.append(
        lembrete
    )

    salvar(
        lembretes
    )


def limpar():

    salvar([])