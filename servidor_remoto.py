from flask import Flask
from flask import request
from flask import jsonify

from core.command_parser import processar_comando
from core.command_router import executar_comando
from core.plugin_loader import carregar_plugins

app = Flask(__name__)

plugins = carregar_plugins()


@app.route("/comando", methods=["POST"])
def comando():

    dados = request.json

    comando = dados.get(
        "comando",
        ""
    )

    comando = processar_comando(
        comando
    )

    executar_comando(
        comando,
        plugins
    )

    return jsonify(
        {
            "status": "ok"
        }
    )


def iniciar():

    app.run(
        host="0.0.0.0",
        port=5000
    )