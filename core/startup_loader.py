import os
import importlib.util


PASTA_STARTUP = "startup"


def carregar_startup_plugins():

    plugins = []

    if not os.path.exists(PASTA_STARTUP):
        return plugins

    for arquivo in os.listdir(PASTA_STARTUP):

        if not arquivo.endswith(".py"):
            continue

        caminho = os.path.join(
            PASTA_STARTUP,
            arquivo
        )

        nome = arquivo[:-3]

        try:

            spec = importlib.util.spec_from_file_location(
                nome,
                caminho
            )

            modulo = importlib.util.module_from_spec(
                spec
            )

            spec.loader.exec_module(
                modulo
            )

            plugins.append(
                modulo
            )

        except Exception as erro:

            print(
                f"[STARTUP] Erro ao carregar {arquivo}: {erro}"
            )

    return plugins


def executar_startup_plugins(plugins):

    for plugin in plugins:

        try:

            if hasattr(
                plugin,
                "deve_executar"
            ):

                if not plugin.deve_executar():
                    continue

            plugin.executar()

        except Exception as erro:

            print(
                f"[STARTUP] Erro em {plugin.NOME}: {erro}"
            )