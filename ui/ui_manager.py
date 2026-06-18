STATUS = "Pronta."
MENSAGEM = "Aguardando comando..."


def set_status(texto):
    global STATUS
    STATUS = texto


def get_status():
    return STATUS


def set_mensagem(texto):
    global MENSAGEM
    MENSAGEM = texto


def get_mensagem():
    return MENSAGEM