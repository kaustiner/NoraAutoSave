from core.speaker import falar
import threading
import webbrowser

NOME = "jarvis_music"

DESCRICAO = "Easter egg do Jarvis"

COMANDOS = {
    "jarvis": [
        "jarvis",
        "i am iron man",
        "tony stark"
    ]
}

URL = "https://www.youtube.com/watch?v=XgWUDbYfNe4&list=RDXgWUDbYfNe4&start_radio=1"


def abrir_musica():

    webbrowser.open(URL)


def executar(acao, comando):

    if acao != "jarvis":
        return

    falar(
        "Bem-vindo de volta, senhor."
    )

    threading.Thread(
        target=abrir_musica,
        daemon=True
    ).start()