import os
import importlib.util
from core.config_manager import plugin_ativo

PASTA_PLUGINS = "plugins"


def carregar_plugins():

    plugins = {}

    for arquivo in os.listdir(PASTA_PLUGINS):

        if not arquivo.endswith(".py"):
            continue

        if arquivo == "__init__.py":
            continue

        nome = arquivo[:-3]

        if not plugin_ativo(nome):
            continue

        caminho = os.path.join(PASTA_PLUGINS, arquivo)

        spec = importlib.util.spec_from_file_location(
            nome,
            caminho
        )

        modulo = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(modulo)

        plugins[nome] = modulo

    return plugins