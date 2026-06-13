import socket
import threading

from core.speaker import falar
from core.remote_server import (
    iniciar_servidor
)

NOME = "controle_remoto"

DESCRICAO = "Controle remoto pela rede"

COMANDOS = {
    "ativar": [
        "ativar controle remoto",
        "iniciar controle remoto"
    ],
    "ip": [
        "ip nora",
        "mostrar ip"
    ]
}

servidor_ativo = False


def obter_ip():

    try:

        s = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        s.connect(
            ("8.8.8.8", 80)
        )

        ip = s.getsockname()[0]

        s.close()

        return ip

    except:

        return "127.0.0.1"


def executar(
    acao,
    comando
):

    global servidor_ativo

    if acao == "ip":

        falar(
            f"IP: {obter_ip()}:5000"
        )

        return

    if acao == "ativar":

        if servidor_ativo:

            falar(
                "Controle remoto já ativo."
            )

            return

        threading.Thread(
            target=iniciar_servidor,
            daemon=True
        ).start()

        servidor_ativo = True

        falar(
            f"Controle remoto iniciado em http://{obter_ip()}:5000"
        )