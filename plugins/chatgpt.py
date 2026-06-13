import webbrowser

from core.speaker import falar

NOME = "chatgpt"

DESCRICAO = "Abre o ChatGPT no navegador padrão."

COMANDOS = {
    "abrir_chatgpt": [
        "abrir chat",
        "abrir chatgpt",
        "abrir chat gpt",
        "chatgpt",
        "chat gpt",
        "abra chat",
        "abra chat gpt",
        "abra o chat",
        "abra o chat gpt"
    ]
}


def executar(acao, comando):

    if acao == "abrir_chatgpt":

        falar(
            "Abrindo ChatGPT."
        )

        webbrowser.open(
            "https://chatgpt.com"
        )

        return