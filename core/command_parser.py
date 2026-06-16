import re


PALAVRAS_IGNORADAS = [
    "nora",
    "por favor",
    "pra mim",
    "rapidinho",
    "agora",
    "aí"
]


def normalizar(texto):

    texto = texto.lower()

    texto = re.sub(
        r"[^\w\s]",
        "",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def processar_comando(comando):

    comando = normalizar(
        comando
    )

    for palavra in PALAVRAS_IGNORADAS:

        if comando.startswith(
            palavra + " "
        ):

            comando = comando[
                len(palavra):
            ].strip()

    return comando