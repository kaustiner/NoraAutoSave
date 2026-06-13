def executar_comando(comando, plugins):

    encontrados = []
    vistos = set()

    for plugin in plugins.values():

        for acao, aliases in plugin.COMANDOS.items():

            for alias in aliases:

                if comando.startswith(alias):

                    chave = (
                        plugin.NOME,
                        acao
                    )

                    if chave not in vistos:

                        vistos.add(chave)

                        encontrados.append(
                            (
                                plugin,
                                acao
                            )
                        )

    if len(encontrados) == 0:

        print(
            "\n[NORA] Não entendi o comando.\n"
        )

        return

    if len(encontrados) > 1:

        print(
            "\n[NORA] Mais de um plugin encontrado:\n"
        )

        for i, (plugin, acao) in enumerate(encontrados):

            print(
                f"{i+1} - {plugin.NOME} ({acao})"
            )

        escolha = int(
            input("\nEscolha: ")
        ) - 1

        plugin, acao = encontrados[escolha]

    else:

        plugin, acao = encontrados[0]

    try:

        plugin.executar(
            acao,
            comando
        )

    except Exception as erro:

        print(
            "\nERRO COMPLETO:\n"
        )

        print(erro)

        input(
            "\nPressione ENTER..."
        )