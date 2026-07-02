import os
import subprocess
import sys
import time

from core.speaker import falar

NOME = "controle_por_mao"
DESCRICAO = "Abre o controle por mão em um processo separado"
COMANDOS = {
    "ativar": [
        "controle por mao",
        "controle por mão",
        "controle por gesto",
        "ativar controle por mao",
        "ligar controle por mao",
    ]
}

_RAIZ_NORA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PATH = os.path.join(_RAIZ_NORA, "controle_por_mao_app.py")
_processo = None


def _processo_ativo():
    global _processo
    if _processo is None:
        return False
    return _processo.poll() is None


def executar(acao, comando):
    global _processo
    if acao != "ativar":
        return

    if _processo_ativo():
        falar("O controle por mão já está ativo.")
        return

    if not os.path.exists(APP_PATH):
        falar("Não encontrei o app de controle por mão.")
        return

    falar("Abrindo controle por mão.")
    try:
        _processo = subprocess.Popen(
            [sys.executable, APP_PATH],
            cwd=_RAIZ_NORA,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        time.sleep(0.2)
    except Exception as erro:
        falar(f"Erro ao abrir o controle por mão: {erro}")
