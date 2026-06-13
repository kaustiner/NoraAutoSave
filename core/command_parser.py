import re

PALAVRAS_IGNORADAS = [
    "nora",
    "por favor",
    "pra mim",
    "rapidinho",
    "agora",
    "aí"
]


def normalizar(texto: str) -> str:

    texto = texto.lower()

    # remove pontuação
    texto = re.sub(r"[^\w\s]", "", texto)

    # remove múltiplos espaços
    texto = re.sub(r"\s+", " ", texto)

    texto = texto.strip()

    return texto


def processar_comando(comando: str) -> str:

    comando = normalizar(comando)

    for palavra in PALAVRAS_IGNORADAS:
        comando = comando.replace(palavra, "")

    comando = re.sub(r"\s+", " ", comando).strip()

    return comando