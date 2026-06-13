from core.gesture_manager import (
    capturar_pontos
)

from core.custom_gesture_manager import (
    salvar_amostra,
    procurar_semelhante
)

TOTAL_AMOSTRAS = 5

amostras = []

print(
    "\n[NORA] Cadastro de gesto\n"
)

for i in range(
    TOTAL_AMOSTRAS
):

    print(
        f"[NORA] Mostre o gesto {i+1}/{TOTAL_AMOSTRAS}"
    )

    pontos = capturar_pontos()

    if pontos:

        amostras.append(
            pontos
        )

    else:

        print(
            "[NORA] Falha na captura."
        )

        continue

nome_existente = None
melhor_score = 0

for amostra in amostras:

    nome, score = procurar_semelhante(
        amostra
    )

    if score > melhor_score:

        melhor_score = score
        nome_existente = nome

if melhor_score > 90:

    print(
        "\n[NORA] Gesto muito parecido com:"
    )

    print(
        nome_existente
    )

    print(
        f"Similaridade: {melhor_score}%"
    )

else:

    nome = input(
        "\nNome do gesto: "
    )

    for indice, amostra in enumerate(
        amostras,
        start=1
    ):

        salvar_amostra(
            nome,
            indice,
            amostra
        )

    print(
        "\n[NORA] Gesto salvo."
    )