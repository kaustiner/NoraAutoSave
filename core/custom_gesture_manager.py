import json
import os
import math

PASTA_GESTOS = "data/gestures"


def garantir_pasta():

    if not os.path.exists(PASTA_GESTOS):

        os.makedirs(PASTA_GESTOS)


def salvar_amostra(
    nome_gesto,
    indice,
    pontos
):

    garantir_pasta()

    pasta = os.path.join(
        PASTA_GESTOS,
        nome_gesto
    )

    os.makedirs(
        pasta,
        exist_ok=True
    )

    caminho = os.path.join(
        pasta,
        f"{indice}.json"
    )

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            pontos,
            arquivo,
            indent=4
        )


def carregar_gestos():

    garantir_pasta()

    gestos = {}

    for nome_gesto in os.listdir(
        PASTA_GESTOS
    ):

        pasta = os.path.join(
            PASTA_GESTOS,
            nome_gesto
        )

        if not os.path.isdir(
            pasta
        ):

            continue

        gestos[nome_gesto] = []

        for arquivo in os.listdir(
            pasta
        ):

            if arquivo.endswith(
                ".json"
            ):

                caminho = os.path.join(
                    pasta,
                    arquivo
                )

                with open(
                    caminho,
                    "r",
                    encoding="utf-8"
                ) as f:

                    gestos[nome_gesto].append(
                        json.load(f)
                    )

    return gestos


def calcular_similaridade(
    gesto1,
    gesto2
):

    if len(gesto1) != len(gesto2):

        return 0

    distancia_total = 0

    for p1, p2 in zip(
        gesto1,
        gesto2
    ):

        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]

        distancia_total += math.sqrt(
            dx * dx +
            dy * dy
        )

    media = (
        distancia_total /
        len(gesto1)
    )

    score = max(
        0,
        100 - media * 300
    )

    return round(
        score,
        2
    )


def procurar_semelhante(
    pontos
):

    gestos = carregar_gestos()

    melhor_nome = None
    melhor_score = 0

    for nome, amostras in gestos.items():

        scores = []

        for amostra in amostras:

            score = calcular_similaridade(
                pontos,
                amostra
            )

            scores.append(
                score
            )

        if scores:

            media = sum(
                scores
            ) / len(
                scores
            )

            if media > melhor_score:

                melhor_score = media
                melhor_nome = nome

    return (
        melhor_nome,
        round(
            melhor_score,
            2
        )
    )