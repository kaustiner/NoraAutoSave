import requests
import json
import os
import importlib.util

from core.llm_client import chamar_llm

PASTA_PLUGINS = os.path.join(os.path.dirname(__file__), "plugins")


def _listar_plugins():
    """Retorna lista de (nome, descricao, comandos) de todos os plugins."""
    plugins = []

    if not os.path.exists(PASTA_PLUGINS):
        return plugins

    for arquivo in os.listdir(PASTA_PLUGINS):
        if not arquivo.endswith(".py"):
            continue

        caminho = os.path.join(PASTA_PLUGINS, arquivo)

        try:
            spec = importlib.util.spec_from_file_location("_tmp", caminho)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)

            nome = getattr(modulo, "NOME", arquivo.replace(".py", ""))
            descricao = getattr(modulo, "DESCRICAO", "")
            comandos = getattr(modulo, "COMANDOS", {})

            exemplos = []
            for acao, lista in comandos.items():
                exemplos += lista[:2]

            plugins.append({
                "nome": nome,
                "descricao": descricao,
                "acao": list(comandos.keys())[0] if comandos else "",
                "exemplos": exemplos
            })

        except Exception:
            continue

    return plugins


def _prompt_rotear(comando, plugins):
    lista_plugins = ""

    for p in plugins:
        exemplos_str = ", ".join(f'"{e}"' for e in p["exemplos"])
        lista_plugins += (
            f"- nome: {p['nome']}\n"
            f"  descricao: {p['descricao']}\n"
            f"  acao: {p['acao']}\n"
            f"  exemplos: {exemplos_str}\n\n"
        )

    return f"""Você é um roteador de intenções de um assistente de voz chamado NORA.

O usuário disse: "{comando}"

Plugins disponíveis:
{lista_plugins}

Responda APENAS com um JSON no formato abaixo, sem texto adicional, sem markdown, sem explicações:

Se o comando se relaciona com algum plugin:
{{"acao": "rotear", "plugin": "nome_do_plugin", "acao_plugin": "acao_do_plugin"}}

Se não existe nenhum plugin relacionado:
{{"acao": "criar", "descricao": "descrição objetiva do que o plugin deve fazer para atender o comando do usuário"}}
"""


def _extrair_json(texto):
    """Extrai JSON da resposta do LLM mesmo com lixo ao redor."""
    inicio = texto.find("{")
    fim = texto.rfind("}") + 1

    if inicio == -1 or fim == 0:
        return None

    try:
        return json.loads(texto[inicio:fim])
    except Exception:
        return None


def rotear(comando):
    """
    Tenta rotear o comando para um plugin existente.
    Retorna dict com:
      - {"acao": "rotear", "plugin": nome, "acao_plugin": acao}
      - {"acao": "criar", "descricao": descricao}
      - {"acao": "erro", "motivo": texto}
    """
    plugins = _listar_plugins()
    prompt = _prompt_rotear(comando, plugins)

    try:
        resposta_llm = chamar_llm(prompt, temperature=0.1)
        resultado = _extrair_json(resposta_llm)

        if not resultado:
            return {
                "acao": "erro",
                "motivo": "LLM não retornou JSON válido"
            }

        return resultado

    except requests.exceptions.ConnectionError:
        return {
            "acao": "erro",
            "motivo": "LLM não está acessível (Ollama ou LM Studio)"
        }
    except Exception as e:
        return {
            "acao": "erro",
            "motivo": str(e)
        }


def executar_plugin(nome_plugin, acao, comando):
    """Carrega e executa um plugin pelo nome."""
    caminho = os.path.join(PASTA_PLUGINS, f"{nome_plugin}.py")

    if not os.path.exists(caminho):
        return False

    try:
        spec = importlib.util.spec_from_file_location(nome_plugin, caminho)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        modulo.executar(acao, comando)
        return True
    except Exception:
        return False
