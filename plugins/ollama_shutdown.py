from core.speaker import falar
import subprocess

NOME = "ollama_shutdown"

DESCRICAO = "Desliga o servidor do Ollama"

COMANDOS = {
    "desligar": [
        "desligar ollama",
        "fechar ollama",
        "encerrar ollama",
        "parar ollama",
        "desliga o ollama",
        "desligar olama",
        "fechar olama",
        "encerrar olama",
        "parar olama",
        "desliga o olama",
        "desligar olhama",
        "fechar olhama",
        "encerrar olhama",
        "parar olhama",
        "desliga o olhama",
        "desligar lama",
        "fechar lama",
        "encerrar lama",
        "parar lama",
        "desliga o lama"
    ]
}


def executar(acao, comando):

    if acao == "desligar":

        try:

            subprocess.run(
                ["taskkill", "/F", "/IM", "ollama.exe"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            falar("Servidor do Ollama desligado.")

        except Exception:

            falar("Não foi possível desligar o Ollama.")