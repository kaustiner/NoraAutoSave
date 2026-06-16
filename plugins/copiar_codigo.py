import os
import pyperclip

from core.speaker import falar

NOME = "copiar_codigo"

DESCRICAO = "Copia código de arquivos do projeto"

COMANDOS = {
    "copiar_codigo": [
        "copiar",
        "copia"
    ]
}


def limpar_comando(texto):

    remover = [
        "copiar",
        "copia",
        "plugin",
        "arquivo",
        "codigo",
        "código"
    ]

    texto = texto.lower()

    incluir_caminho = True

    palavras_sem_caminho = [
        "sem caminho",
        "mas sem caminho",
        "só o código",
        "so o codigo",
        "só código",
        "so codigo",
        "apenas codigo",
        "apenas código"
    ]

    for palavra in palavras_sem_caminho:

        if palavra in texto:

            incluir_caminho = False

            texto = texto.replace(
                palavra,
                ""
            )

    for palavra in remover:

        texto = texto.replace(
            palavra,
            ""
        )

    texto = " ".join(
        texto.split()
    )

    return texto, incluir_caminho


def encontrar_arquivo(termo):

    pasta_raiz = os.getcwd()

    palavras = termo.lower().split()

    encontrados = []

    ignorar_pastas = {
        "__pycache__",
        ".git",
        ".venv",
        "venv"
    }

    ignorar_extensoes = {
        ".pyc",
        ".pyo"
    }

    for raiz, dirs, arquivos in os.walk(pasta_raiz):

        dirs[:] = [
            d
            for d in dirs
            if d not in ignorar_pastas
        ]

        for arquivo in arquivos:

            nome, ext = os.path.splitext(
                arquivo.lower()
            )

            if ext in ignorar_extensoes:
                continue

            nome_limpo = (
                nome
                .replace("_", " ")
                .replace("-", " ")
            )

            score = 0

            for palavra in palavras:

                if palavra in nome_limpo:
                    score += 1

            if score > 0:

                encontrados.append(
                    (
                        score,
                        os.path.join(
                            raiz,
                            arquivo
                        )
                    )
                )

    encontrados.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return [
        caminho
        for _, caminho in encontrados
    ]


def copiar_arquivo(
    caminho,
    incluir_caminho=True
):

    with open(
        caminho,
        "r",
        encoding="utf-8"
    ) as f:

        codigo = f.read()

    if incluir_caminho:

        texto = (
            f"ARQUIVO:\n\n"
            f"{caminho}\n\n"
            f"{'-' * 40}\n\n"
            f"{codigo}"
        )

    else:

        texto = codigo

    pyperclip.copy(
        texto
    )


def executar(
    acao,
    comando
):

    if acao != "copiar_codigo":
        return

    termo, incluir_caminho = limpar_comando(
        comando
    )

    if not termo:

        falar(
            "Qual arquivo deseja copiar?"
        )
        return

    resultados = encontrar_arquivo(
        termo
    )

    if not resultados:

        falar(
            "Nenhum arquivo encontrado."
        )
        return

    if len(resultados) == 1:

        try:

            copiar_arquivo(
                resultados[0],
                incluir_caminho
            )

            falar(
                "Código copiado para a área de transferência."
            )

        except Exception as e:

            falar(
                f"Erro: {e}"
            )

        return

    falar(
        "Encontrei mais de um arquivo."
    )

    for i, arquivo in enumerate(
        resultados,
        start=1
    ):

        print(
            f"{i} - {arquivo}"
        )

    try:

        escolha = int(
            input(
                "\nEscolha: "
            )
        ) - 1

        if escolha < 0:
            raise ValueError

        caminho = resultados[
            escolha
        ]

        copiar_arquivo(
            caminho,
            incluir_caminho
        )

        falar(
            "Código copiado para a área de transferência."
        )

    except:

        falar(
            "Escolha inválida."
        )