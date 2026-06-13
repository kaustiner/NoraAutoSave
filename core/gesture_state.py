GESTO_ATIVO = False


def gesto_ativo():

    return GESTO_ATIVO


def ativar_gesto():

    global GESTO_ATIVO

    GESTO_ATIVO = True


def resetar_gesto():

    global GESTO_ATIVO

    GESTO_ATIVO = False