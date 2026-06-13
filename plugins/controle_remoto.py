import threading
import socket

from flask import Flask
from flask import request
from flask import jsonify

from core.speaker import falar
from core.command_parser import processar_comando
from core.command_router import executar_comando
from core.plugin_loader import carregar_plugins


NOME = "controle_remoto"

DESCRICAO = "Controle da NORA pelo celular"

COMANDOS = {
    "ativar": [
        "ativar controle remoto",
        "iniciar controle remoto",
        "ligar controle remoto"
    ],
    "ip": [
        "ip nora",
        "mostrar ip",
        "qual ip"
    ]
}


app = Flask(__name__)

servidor_ativo = False
plugins_cache = None


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


@app.route("/comando", methods=["POST"])
def receber_comando():

    global plugins_cache

    dados = request.json or {}

    token = dados.get(
        "token",
        ""
    )

    if token != "nora123":

        return jsonify(
            {
                "erro": "token invalido"
            }
        ), 401

    comando = dados.get(
        "comando",
        ""
    )

    comando = processar_comando(
        comando
    )

    executar_comando(
        comando,
        plugins_cache
    )

    return jsonify(
        {
            "status": "ok"
        }
    )


def iniciar_servidor():

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )


def executar(acao, comando):

    global servidor_ativo
    global plugins_cache

    if acao == "ip":

        ip = obter_ip()

        falar(
            f"IP atual: {ip}:5000"
        )

        return

    if acao == "ativar":

        if servidor_ativo:

            falar(
                "Controle remoto já está ativo."
            )

            return

        plugins_cache = carregar_plugins()

        threading.Thread(
            target=iniciar_servidor,
            daemon=True
        ).start()

        servidor_ativo = True

        ip = obter_ip()

        falar(
            f"Controle remoto iniciado em http://{ip}:5000"
        )