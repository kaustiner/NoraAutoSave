from core.speaker import falar
from core.llm_client import chamar_llm

NOME = "perguntas_ia"

DESCRICAO = "Responde perguntas usando IA local via Ollama ou LM Studio"

COMANDOS = {
    "perguntar": [
        "pergunte",
        "quem é",
        "o que é",
        "como funciona",
        "explique"
    ]
}


def perguntar_ia(pergunta):

    prompt = f"""
Responda de forma curta e objetiva.

Pergunta:

{pergunta}
"""

    return chamar_llm(prompt)


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
