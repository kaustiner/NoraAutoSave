from core.speaker import falar

from core.dialog_manager import (
    iniciar,
    ativo,
    obter_etapa,
    definir_etapa,
    encerrar
)

NOME = "teste_dialogo"

DESCRICAO = "Teste de diálogo"

COMANDOS = {
    "teste": [
        "teste dialogo"
    ]
}


def executar(acao, comando):

    if not ativo():

        iniciar(
            NOME,
            acao,
            "nome"
        )

        falar(
            "Qual é o seu nome?"
        )

        return

    etapa = obter_etapa()

    if etapa == "nome":

        definir_etapa(
            "idade"
        )

        falar(
            f"Prazer, {comando}. Qual sua idade?"
        )

        return

    if etapa == "idade":

        falar(
            f"Você informou idade {comando}."
        )

        encerrar()