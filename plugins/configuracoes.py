from core.speaker import falar
from painel_config import abrir_painel

NOME = "configuracoes"

DESCRICAO = "Abre o painel de configuracoes"

COMANDOS = {
    "abrir": [
        "config",
        "painel",
        "abrir painel",
        "configuracoes",
        "abrir configuracoes"
    ]
}


def executar(acao, comando):

    if acao == "abrir":

        falar(
            "Abrindo painel de configuração."
        )

        abrir_painel()