import os


def garantir_pasta(caminho):

    os.makedirs(
        caminho,
        exist_ok=True
    )


def ler_arquivo(caminho):

    try:

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return arquivo.read()

    except:

        return ""


def escrever_arquivo(
    caminho,
    conteudo
):

    with open(
        caminho,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(conteudo)