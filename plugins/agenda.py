from core.speaker import falar

from core.dialog_manager import (
    iniciar,
    ativo,
    obter_dado,
    atualizar,
    definir_etapa,
    resposta_sim,
    resposta_nao,
    encerrar,
    obter
)

from core.date_parser import interpretar

from core.reminder_parser import extrair

from core.agenda_manager import (
    criar_lembrete,
    listar_lembretes,
    apagar_todos,
    apagar_indice
)

NOME = "agenda"

DESCRICAO = "Sistema de lembretes"


COMANDOS = {

    "criar": [
        "criar lembrete",
        "novo lembrete",
        "adicionar lembrete"
    ],

    "listar": [
        "listar lembretes",
        "mostrar lembretes",
        "ver lembretes"
    ],

    "apagar": [
        "apagar lembretes",
        "apagar todos os lembretes",
        "apague lembretes",
        "apague os lembretes",
        "remover lembretes",
        "remover todos os lembretes",
        "excluir lembretes",
        "excluir todos os lembretes"
    ],

    "apagar_um": [
        "apagar lembrete",
        "remover lembrete",
        "excluir lembrete"
    ],

    "natural": [
        "me lembre",
        "me lembra",
        "lembra de",
        "preciso lembrar",
        "não me deixa esquecer",
        "nao me deixa esquecer"
    ]
}


def executar(acao, comando):

    if acao == "criar":

        executar_criacao(
            comando
        )

        return

    if acao == "listar":

        executar_listagem()

        return

    if acao == "apagar":

        executar_apagar_todos(
            comando
        )

        return

    if acao == "apagar_um":

        executar_apagar_um(
            comando
        )

        return

    if acao == "natural":

        executar_natural(
            comando
        )

        return


def executar_criacao(comando):

    if not ativo():

        iniciar(
            NOME,
            "criar",
            "nome"
        )

        falar(
            "Qual o nome do lembrete?"
        )

        return

    dialogo = obter()

    if dialogo["etapa"] == "nome":

        atualizar(
            "titulo",
            comando
        )

        definir_etapa(
            "data"
        )

        falar(
            "Qual a data?"
        )

        return

    if dialogo["etapa"] == "data":

        titulo = obter_dado(
            "titulo"
        )

        data = interpretar(
            comando
        )

        criar_lembrete(
            titulo=titulo,
            data=data,
            startup=(data is None)
        )

        falar(
            "Lembrete salvo."
        )

        encerrar()


def executar_listagem():

    lembretes = listar_lembretes()

    if not lembretes:

        falar(
            "Nenhum lembrete encontrado."
        )

        return

    for indice, lembrete in enumerate(
        lembretes,
        start=1
    ):

        titulo = lembrete.get(
            "titulo",
            "Sem nome"
        )

        if lembrete.get(
            "startup"
        ):

            falar(
                f"{indice}. {titulo} (startup)"
            )

            continue

        if "data" in lembrete:

            falar(
                f"{indice}. {titulo} - {lembrete['data']}"
            )

            continue

        falar(
            f"{indice}. {titulo}"
        )


def executar_apagar_um(comando):

    partes = comando.split()

    numero = None

    for parte in partes:

        if parte.isdigit():

            numero = int(
                parte
            )

            break

    if numero is None:

        falar(
            "Informe o número do lembrete."
        )

        return

    removido = apagar_indice(
        numero - 1
    )

    if not removido:

        falar(
            "Lembrete não encontrado."
        )

        return

    falar(
        f"Lembrete removido: {removido['titulo']}"
    )


def executar_apagar_todos(comando):

    if not ativo():

        lembretes = listar_lembretes()

        if not lembretes:

            falar(
                "Não existem lembretes."
            )

            return

        for indice, lembrete in enumerate(
            lembretes,
            start=1
        ):

            falar(
                f"{indice}. {lembrete['titulo']}"
            )

        iniciar(
            NOME,
            "apagar",
            "confirmar"
        )

        falar(
            "Deseja apagar todos os lembretes?"
        )

        return

    dialogo = obter()

    if dialogo["etapa"] != "confirmar":

        return

    if resposta_sim(comando):

        apagar_todos()

        falar(
            "Todos os lembretes foram removidos."
        )

        encerrar()

        return

    if resposta_nao(comando):

        falar(
            "Operação cancelada."
        )

        encerrar()

        return

    falar(
        "Responda sim ou não."
    )


def executar_natural(comando):

    resultado = extrair(
        comando
    )

    if not resultado:

        falar(
            "Não consegui entender o lembrete."
        )

        return

    criar_lembrete(
        titulo=resultado["titulo"],
        data=resultado["data"],
        startup=(
            resultado["data"] is None
        )
    )

    falar(
        "Lembrete salvo."
    )