import io

import pyautogui

from PIL import Image
from PIL import ImageWin

import win32clipboard

from core.speaker import falar


NOME = "captura_tela"

DESCRICAO = "Captura a tela e copia para a área de transferência"

COMANDOS = {
    "capturar": [
        "capturar tela",
        "tirar print",
        "print tela",
        "screenshot"
    ]
}


def copiar_imagem_para_clipboard(imagem):

    output = io.BytesIO()

    imagem.convert("RGB").save(
        output,
        "BMP"
    )

    dados = output.getvalue()[14:]

    output.close()

    win32clipboard.OpenClipboard()

    try:

        win32clipboard.EmptyClipboard()

        win32clipboard.SetClipboardData(
            win32clipboard.CF_DIB,
            dados
        )

    finally:

        win32clipboard.CloseClipboard()


def executar(acao, argumentos):

    if acao != "capturar":
        return

    try:

        falar(
            "Capturando tela."
        )

        imagem = pyautogui.screenshot()

        copiar_imagem_para_clipboard(
            imagem
        )

        falar(
            "Tela capturada e copiada para a área de transferência."
        )

    except Exception as erro:

        falar(
            f"Erro ao capturar tela. {erro}"
        )