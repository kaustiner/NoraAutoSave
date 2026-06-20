import json
import requests

CONFIG = "config/ia.json"
OLLAMA_URL = "http://localhost:11434/api/generate"


def carregar_modelo():
    try:
        with open(
            CONFIG,
            "r",
            encoding="utf-8"
        ) as f:
            dados = json.load(f)
        return dados.get(
            "modelo_interpretador",
            "qwen3:0"
        )
    except:
        return "qwen3:0"


MODELO = carregar_modelo()


def interpretar(comando, plugins):

    lista_plugins = []

    for plugin in plugins.values():

        for acao, aliases in plugin.COMANDOS.items():

            lista_plugins.append({
                "plugin": plugin.NOME,
                "acao": acao,
                "comandos": aliases
            })

    prompt = f"""
Você é o interpretador da assistente NORA.

Comando do usuário:
{comando}

Plugins disponíveis:
{json.dumps(lista_plugins, ensure_ascii=False)}

Responda SOMENTE JSON.

Formato:

{{
    "plugin": "nome",
    "acao": "acao",
    "confianca": 0.95
}}

Se não tiver certeza:

{{
    "plugin": null,
    "acao": null,
    "confianca": 0
}}
"""

    try:

        resposta = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO,
                "prompt": prompt,
                "stream": False
            },
            timeout=20
        )

        texto = resposta.json()["response"]

        inicio = texto.find("{")
        fim = texto.rfind("}")

        if inicio == -1:
            return None

        dados = json.loads(
            texto[inicio:fim+1]
        )

        return dados

    except:
        return None