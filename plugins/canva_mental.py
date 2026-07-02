"""
Plugin: canva_mental
Abre o NORA Canvas (canvas_mental_app.py) como processo totalmente independente.
A NORA continua funcionando normalmente enquanto o Canvas está aberto.
"""

import os
import sys
import subprocess
import time

from core.speaker import falar

NOME = "canvas_mental"

DESCRICAO = "Abre um canvas de mapa mental futurista controlado por gestos de mão"

COMANDOS = {
    "canvas": [
        "canvas",
        "mapa mental",
        "quadro",
        "canvas mental",
        "abrir canvas",
        "desenhar"
    ]
}

_RAIZ_NORA = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

APP_PATH = os.path.join(_RAIZ_NORA, "canvas_mental_app.py")

_processo = None


def _processo_ativo():
    global _processo
    if _processo is None:
        return False
    return _processo.poll() is None


def executar(acao, comando):
    global _processo

    if acao != "canvas":
        return

    if _processo_ativo():
        falar("O Canvas já está aberto.")
        return

    if not os.path.exists(APP_PATH):
        falar("Não encontrei o arquivo canvas_mental_app.py na pasta da NORA.")
        return

    falar("Abrindo NORA Canvas.")

    try:
        # DETACHED_PROCESS + CREATE_NEW_PROCESS_GROUP garante que o processo
        # filho não herda o console da NORA nem trava o CMD dela.
        flags = 0
        if sys.platform == "win32":
            flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

        _processo = subprocess.Popen(
            [sys.executable, APP_PATH],
            cwd=_RAIZ_NORA,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=flags,
            close_fds=True,
        )
        time.sleep(0.3)
    except Exception as erro:
        falar(f"Erro ao abrir o Canvas: {erro}")