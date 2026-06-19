from core.speaker import falar

NOME = "apresentacao"

DESCRICAO = "Apresentação da NORA"

COMANDOS = {
    "apresentar": [
        "oi",
        "ola",
        "quem e voce",
        "quem é voce",
        "quem e a nora",
        "quem é a nora",
        "o que voce faz",
        "o que você faz",
        "o que e a nora",
        "o que é a nora"
    ]
}


def executar(acao, comando):

    if acao == "apresentar":

        falar(
            "Olá. Eu sou a NORA. "
            "Uma assistente pessoal modular desenvolvida em Python por KAIO WILLIAN. "
            "Posso executar comandos, abrir programas, controlar plugins, "
            "automatizar tarefas e crescer através de novos módulos."
            "Está versão criada dia 19/06/2026 é a primeira disponibilizada ao público."
        )