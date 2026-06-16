dialogo = None


def iniciar(plugin, acao, etapa="inicio"):

    global dialogo

    dialogo = {
        "plugin": plugin,
        "acao": acao,
        "etapa": etapa,
        "dados": {}
    }


def ativo():

    return dialogo is not None


def obter():

    return dialogo


def obter_plugin():

    if not dialogo:
        return None

    return dialogo["plugin"]


def obter_acao():

    if not dialogo:
        return None

    return dialogo["acao"]


def obter_etapa():

    if not dialogo:
        return None

    return dialogo["etapa"]


def definir_etapa(etapa):

    if dialogo:

        dialogo["etapa"] = etapa


def atualizar(chave, valor):

    if dialogo:

        dialogo["dados"][chave] = valor


def obter_dado(chave, padrao=None):

    if not dialogo:
        return padrao

    return dialogo["dados"].get(
        chave,
        padrao
    )


def obter_dados():

    if not dialogo:
        return {}

    return dialogo["dados"]


def resposta_sim(texto):

    texto = texto.lower().strip()

    return texto in [
        "s",
        "sim",
        "claro",
        "ok",
        "confirmo"
    ]


def resposta_nao(texto):

    texto = texto.lower().strip()

    return texto in [
        "n",
        "nao",
        "não",
        "negativo"
    ]


def cancelar(texto):

    texto = texto.lower().strip()

    return texto in [
        "cancelar",
        "cancela",
        "pare",
        "parar",
        "esquecer",
        "deixa pra la",
        "deixa pra lá"
    ]


def encerrar():

    global dialogo

    dialogo = None