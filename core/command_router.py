def normalizar(texto):
    import re
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto


def comandos_similares(comando, alias):
    comando = normalizar(comando)
    alias = normalizar(alias)

    if comando.startswith(alias):
        return True

    palavras_alias = set(alias.split())
    palavras_comando = set(comando.split())

    if not palavras_alias:
        return False

    matches = palavras_alias & palavras_comando
    score = len(matches) / len(palavras_alias)

    return score >= 0.8


def executar_comando(comando, plugins):
    encontrados = []
    vistos = set()

    for plugin in plugins.values():
        for acao, aliases in plugin.COMANDOS.items():
            for alias in aliases:
                if comandos_similares(comando, alias):
                    chave = (plugin.NOME, acao)

                    if chave not in vistos:
                        vistos.add(chave)
                        encontrados.append((plugin, acao))

    if len(encontrados) == 0:
        print("\n[NORA] Não entendi o comando.\n")
        return

    if len(encontrados) > 1:
        print("\n[NORA] Mais de um plugin encontrado:\n")

        for i, (plugin, acao) in enumerate(encontrados):
            print(f"{i+1} - {plugin.NOME} ({acao})")

        escolha = int(input("\nEscolha: ")) - 1
        plugin, acao = encontrados[escolha]

    else:
        plugin, acao = encontrados[0]

    try:
        plugin.executar(acao, comando)

    except Exception as erro:
        print("\nERRO COMPLETO:\n")
        print(erro)
        input("\nPressione ENTER...")