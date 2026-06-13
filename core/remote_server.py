import json
import os

from flask import Flask
from flask import request


ARQUIVO_COMANDOS = "data/remote_commands.json"

app = Flask(__name__)


def garantir_arquivo():

    pasta = "data"

    if not os.path.exists(pasta):

        os.makedirs(pasta)

    if not os.path.exists(
        ARQUIVO_COMANDOS
    ):

        with open(
            ARQUIVO_COMANDOS,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                [],
                f,
                ensure_ascii=False,
                indent=4
            )


def carregar_comandos():

    garantir_arquivo()

    with open(
        ARQUIVO_COMANDOS,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def salvar_comandos(comandos):

    with open(
        ARQUIVO_COMANDOS,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            comandos,
            f,
            ensure_ascii=False,
            indent=4
        )


@app.route("/", methods=["GET", "POST"])
def inicio():

    mensagem = ""

    if request.method == "POST":

        comando = request.form.get(
            "comando",
            ""
        ).strip()

        if comando:

            comandos = carregar_comandos()

            comandos.append(
                comando
            )

            salvar_comandos(
                comandos
            )

            mensagem = (
                f"Comando enviado: {comando}"
            )

    return f"""
<!DOCTYPE html>
<html>
<head>

<meta charset="utf-8">

<title>NORA</title>

<style>

body {{

    font-family: Arial;
    text-align: center;

    margin-top: 50px;
}}

input {{

    width: 300px;
    padding: 10px;

    font-size: 16px;
}}

button {{

    padding: 10px 20px;

    font-size: 16px;

    margin-left: 5px;
}}

</style>

</head>

<body>

<h1>NORA</h1>

<form method="POST">

<input
    name="comando"
    placeholder="Digite um comando"
    autofocus
>

<button type="submit">
Enviar
</button>

</form>

<p>{mensagem}</p>

</body>
</html>
"""


def iniciar_servidor():

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )