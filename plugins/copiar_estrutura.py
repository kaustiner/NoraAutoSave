from pathlib import Path

from core.speaker import falar

import pyperclip

NOME = "copiar_estrutura"

DESCRICAO = "Copia a estrutura da NORA para a área de transferência"

COMANDOS = {
    "copiar": [
        "copiar estrutura",
        "copiar estrutura da nora",
        "estrutura da nora",
        "mostrar estrutura"
    ]
}


def gerar_arvore(pasta, prefixo=""):

    linhas = []

    itens = sorted(
        Path(pasta).iterdir(),
        key=lambda x: (
            not x.is_dir(),
            x.name.lower()
        )
    )

    for i, item in enumerate(itens):

        ultimo = i == len(itens) - 1

        conector = "└── " if ultimo else "├── "

        linhas.append(
            prefixo + conector + item.name
        )

        if item.is_dir():

            novo_prefixo = (
                prefixo +
                ("    " if ultimo else "│   ")
            )

            linhas.extend(
                gerar_arvore(
                    item,
                    novo_prefixo
                )
            )

    return linhas


def executar(acao, comando):

    raiz = Path.cwd()

    estrutura = "\n".join(
        gerar_arvore(raiz)
    )

    pyperclip.copy(
        estrutura
    )

    falar(
        "Estrutura copiada para a área de transferência."
    )