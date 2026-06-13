from core.file_manager import (
    ler_arquivo,
    escrever_arquivo
)

ARQUIVO_NOTAS = "data/notes/notas.txt"


def adicionar_nota(texto):

    atual = ler_arquivo(
        ARQUIVO_NOTAS
    )

    atual += texto + "\n"

    escrever_arquivo(
        ARQUIVO_NOTAS,
        atual
    )


def listar_notas():

    return ler_arquivo(
        ARQUIVO_NOTAS
    )