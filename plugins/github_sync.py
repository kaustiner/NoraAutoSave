import os
import json
import subprocess

from core.speaker import falar

NOME = "github_sync"

DESCRICAO = "Envia a NORA para o GitHub"

COMANDOS = {
    "enviar": [
        "enviar github",
        "atualizar github",
        "auto save github",
        "fazer backup github"
    ]
}

CONFIG = "config/github.json"


def carregar_config():

    with open(
        CONFIG,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def executar_git(comando):

    return subprocess.run(
        comando,
        shell=True,
        capture_output=True,
        text=True
    )


def inicializar_git(repo):

    if not os.path.exists(".git"):

        falar(
            "Inicializando Git."
        )

        executar_git(
            "git init"
        )

        executar_git(
            f"git remote add origin {repo}"
        )


def executar(acao, comando):

    if acao != "enviar":
        return

    try:

        cfg = carregar_config()

        repo = cfg["repositorio"]
        branch = cfg.get(
            "branch",
            "main"
        )

        inicializar_git(repo)

        falar(
            "Preparando arquivos."
        )

        executar_git(
            "git add ."
        )

        commit = executar_git(
            'git commit -m "Atualização automática da NORA"'
        )

        falar(
            "Sincronizando com GitHub."
        )

        pull = executar_git(
            f"git pull origin {branch} --allow-unrelated-histories"
        )

        if pull.returncode != 0:
            print(pull.stderr)

        falar(
            "Enviando para o GitHub."
        )

        push = executar_git(
            f"git push origin {branch}"
        )

        if push.returncode == 0:

            falar(
                "Backup concluído."
            )

        else:

            falar(
                "Falha ao enviar."
            )

            print(
                push.stderr
            )

    except Exception as erro:

        falar(
            f"Erro: {erro}"
        )