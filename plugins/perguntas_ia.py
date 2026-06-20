from core.speaker import falar

import requests

NOME = "perguntas_ia"

DESCRICAO = "Responde perguntas usando Qwen local"

COMANDOS = {
    "perguntar": [
        "pergunte",
        "quem é",
        "o que é",
        "como funciona",
        "explique"
    ]
}

OLLAMA_URL = "http://localhost:11434/api/generate"

MODELO = "qwen3:0.6b"


def perguntar_ia(pergunta):

    prompt = f"""
Responda de forma curta e objetiva.

Pergunta:

{pergunta}
"""

    resposta = requests.post(
        OLLAMA_URL,
        json={
            "model": MODELO,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    resposta.raise_for_status()

    return resposta.json()["response"]


def executar(acao, comando):

    try:

        pergunta = comando.strip()

        resposta = perguntar_ia(
            pergunta
        )

        falar(
            resposta
        )

    except Exception as erro:

        falar(
            f"Erro: {erro}"
        )