import json

from core.llm_client import chamar_llm


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

        texto = chamar_llm(prompt)

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
