import os

from core.gesture_config_manager import (
    carregar_gestos,
    definir_plugin,
    remover_gesto
)

PASTA_GESTOS = "data/gestures"
PASTA_PLUGINS = "plugins"


def listar_gestos():

    if not os.path.exists(PASTA_GESTOS):
        return []

    return sorted([
        nome
        for nome in os.listdir(PASTA_GESTOS)
        if os.path.isdir(
            os.path.join(
                PASTA_GESTOS,
                nome
            )
        )
    ])


def listar_plugins():

    if not os.path.exists(PASTA_PLUGINS):
        return []

    return sorted([
        arquivo[:-3]
        for arquivo in os.listdir(PASTA_PLUGINS)
        if arquivo.endswith(".py")
        and arquivo != "__init__.py"
    ])


def abrir_painel():

    while True:

        print("\n==========")
        print("GESTOS")
        print("==========")

        configurados = carregar_gestos()

        if configurados:

            print("\nVínculos atuais:\n")

            for gesto, plugin in configurados.items():

                print(
                    f"{gesto} -> {plugin}"
                )

        else:

            print(
                "\nNenhum vínculo configurado."
            )

        print("\n1 - Vincular gesto")
        print("2 - Remover vínculo")
        print("0 - Sair")

        op = input("\n> ")

        if op == "0":

            print(
                "\n[NORA] Fechando painel.\n"
            )

            break

        elif op == "1":

            gestos = listar_gestos()

            if not gestos:

                print(
                    "\n[NORA] Nenhum gesto cadastrado."
                )

                continue

            print("\nGestos disponíveis:\n")

            for i, gesto in enumerate(
                gestos,
                start=1
            ):

                print(
                    f"{i} - {gesto}"
                )

            try:

                indice_gesto = int(
                    input(
                        "\nEscolha o gesto: "
                    )
                ) - 1

                gesto = gestos[
                    indice_gesto
                ]

            except:

                print(
                    "\n[NORA] Opção inválida."
                )

                continue

            plugins = listar_plugins()

            print(
                "\nPlugins disponíveis:\n"
            )

            for i, plugin in enumerate(
                plugins,
                start=1
            ):

                print(
                    f"{i} - {plugin}"
                )

            try:

                indice_plugin = int(
                    input(
                        "\nEscolha o plugin: "
                    )
                ) - 1

                plugin = plugins[
                    indice_plugin
                ]

            except:

                print(
                    "\n[NORA] Opção inválida."
                )

                continue

            definir_plugin(
                gesto,
                plugin
            )

            print(
                "\n[NORA] Vínculo salvo."
            )

        elif op == "2":

            configurados = carregar_gestos()

            if not configurados:

                print(
                    "\n[NORA] Nenhum vínculo encontrado."
                )

                continue

            itens = list(
                configurados.keys()
            )

            print("\nVínculos:\n")

            for i, gesto in enumerate(
                itens,
                start=1
            ):

                print(
                    f"{i} - {gesto}"
                )

            try:

                indice = int(
                    input(
                        "\nEscolha: "
                    )
                ) - 1

                gesto = itens[
                    indice
                ]

            except:

                print(
                    "\n[NORA] Opção inválida."
                )

                continue

            remover_gesto(
                gesto
            )

            print(
                "\n[NORA] Vínculo removido."
            )

        else:

            print(
                "\n[NORA] Opção inválida."
            )


if __name__ == "__main__":

    abrir_painel()