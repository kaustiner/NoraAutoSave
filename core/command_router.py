import re


def normalizar(texto):
    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto


def comandos_similares(comando, alias):
    comando = normalizar(comando)
    alias = normalizar(alias)

    # Match exato ou por prefixo (mais confiável)
    if comando == alias:
        return True

    if comando.startswith(alias + " ") or comando.startswith(alias):
        return True

    # Similaridade só para aliases com 3+ palavras
    palavras_alias = alias.split()
    palavras_comando = set(comando.split())

    if len(palavras_alias) < 3:
        return False

    matches = sum(1 for p in palavras_alias if p in palavras_comando)
    score = matches / len(palavras_alias)

    return score >= 0.85


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
                    break  # achou match nessa ação, passa pra próxima

    if len(encontrados) == 0:
        print("\n[NORA] Não entendi o comando.\n")
        return

    if len(encontrados) > 1:
        print("\n[NORA] Mais de um plugin encontrado:\n")

        for i, (plugin, acao) in enumerate(encontrados):
            print(f"{i+1} - {plugin.NOME} ({acao})")

        try:
            escolha = int(input("\nEscolha: ")) - 1
            plugin, acao = encontrados[escolha]
        except:
            print("\n[NORA] Escolha inválida.\n")
            return

    else:
        plugin, acao = encontrados[0]

    try:
        plugin.executar(acao, comando)

    except Exception as erro:
        print("\nERRO COMPLETO:\n")
        print(erro)
        input("\nPressione ENTER...")