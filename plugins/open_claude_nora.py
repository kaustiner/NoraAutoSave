from core.speaker import falar

import os
import subprocess

NOME = "open_claude_nora"

DESCRICAO = "Abre o OpenClaude na pasta da NORA com o modelo qwen3:8b"

COMANDOS = {
    "abrir": [
        "abrir open claude nora",
        "abrir open claude da nora",
        "abrir claude nora",
        "abrir claude nora",
        "abrir cloude nora",
        "abrir clode nora",
        "abrir code nora",
        "open claude nora",
        "claude nora",
        "cloude nora",
        "clode nora",
        "code nora"
    ]
}

PASTA_NORA = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

def executar(acao, comando):
    try:
        falar(
            "Abrindo OpenClaude na pasta da Nora com o modelo qwen3:8b."
        )
        
        # Comando para abrir um novo cmd na pasta da Nora e executar o OpenClaude
        subprocess.Popen(
            [
                "cmd", 
                "/k",  # Mantém o cmd aberto após a execução
                "openclaude",  # Comando para iniciar o OpenClaude
                "--model",     # Parâmetro para especificar o modelo
                "qwen3:8b"     # Modelo a ser usado
            ],
            cwd=PASTA_NORA  # Define o diretório de trabalho para a pasta da Nora
        )
    
    except Exception as erro:
        falar(
            f"Erro ao abrir OpenClaude: {erro}"
        )
