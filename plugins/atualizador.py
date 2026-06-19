import os
import shutil
import zipfile
import tempfile
import requests

from core.speaker import falar

NOME = "atualizador"

DESCRICAO = "Atualiza a NORA pelo GitHub"

COMANDOS = {
    "atualizar": [
        "atualizar nora",
        "verificar atualizacao",
        "verificar atualização",
        "update nora"
    ]
}

REPO_ZIP = (
    "https://github.com/kaustiner/"
    "NoraAutoSave/archive/refs/heads/master.zip"
)


def executar(acao, comando):

    if acao != "atualizar":
        return

    falar("Verificando atualizações.")

    try:

        temp_dir = tempfile.mkdtemp()

        zip_path = os.path.join(
            temp_dir,
            "update.zip"
        )

        resposta = requests.get(
            REPO_ZIP,
            timeout=30
        )

        with open(zip_path, "wb") as f:
            f.write(resposta.content)

        falar("Download concluído.")

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(temp_dir)

        pasta_extraida = None

        for item in os.listdir(temp_dir):

            caminho = os.path.join(
                temp_dir,
                item
            )

            if os.path.isdir(caminho):
                pasta_extraida = caminho
                break

        if not pasta_extraida:

            falar(
                "Falha ao localizar arquivos."
            )

            return

        destino = os.getcwd()

        for item in os.listdir(
            pasta_extraida
        ):

            origem = os.path.join(
                pasta_extraida,
                item
            )

            destino_item = os.path.join(
                destino,
                item
            )

            if os.path.isdir(origem):

                shutil.copytree(
                    origem,
                    destino_item,
                    dirs_exist_ok=True
                )

            else:

                shutil.copy2(
                    origem,
                    destino_item
                )

        falar(
            "Atualização concluída. Reinicie a NORA."
        )

    except Exception as e:

        falar(
            f"Erro na atualização: {e}"
        )