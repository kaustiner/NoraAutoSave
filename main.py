import time
import threading

import sounddevice as sd

from core.plugin_loader import carregar_plugins
from core.command_parser import processar_comando
from core.command_router import executar_comando

from core.startup_loader import (
    carregar_startup_plugins,
    executar_startup_plugins
)

from core.input_manager import (
    iniciar_listener,
    alt_pressionado,
    gesto_pressionado
)

from core.voice_manager import (
    ouvir_push_to_talk,
    salvar_audio,
    transcrever_arquivo
)

from core.gesture_manager import (
    detectar_gesto
)

from core.dialog_manager import (
    ativo,
    cancelar,
    encerrar,
    obter_plugin,
    obter_acao
)

from core.speaker import falar

from ui.ui_manager import (
    set_status,
    set_mensagem
)

from ui.popup_ui import (
    iniciar_interface
)

from core.interface_mode import (
    obter_modo
)

print("\n[NORA] Inicializando...\n")

plugins = carregar_plugins()

startup_plugins = carregar_startup_plugins()

executar_startup_plugins(
    startup_plugins
)

print(
    f"[NORA] {len(plugins)} plugin(s) carregado(s)"
)

print(
    f"[NORA] {len(startup_plugins)} startup plugin(s)"
)

print(
    "[NORA] Pronta.\n"
)

modo = obter_modo()

if modo in [
    "interface",
    "ambos"
]:

    threading.Thread(
        target=iniciar_interface,
        daemon=True
    ).start()


def executar_texto(comando):

    set_mensagem(comando)

    comando = processar_comando(
        comando
    )

    if ativo():

        if cancelar(comando):

            encerrar()

            falar(
                "Operação cancelada."
            )

            set_status(
                "Pronta."
            )

            return

        nome_plugin = obter_plugin()

        if nome_plugin in plugins:

            plugins[nome_plugin].executar(
                obter_acao(),
                comando
            )

        set_status(
            "Pronta."
        )

        return

    executar_comando(
        comando,
        plugins
    )

    set_status(
        "Pronta."
    )


def loop_terminal():

    while True:

        comando = input("> ")

        if comando.lower() in [
            "sair",
            "exit"
        ]:

            print(
                "\n[NORA] Encerrando..."
            )

            exit()

        executar_texto(
            comando
        )


if modo in [
    "terminal",
    "ambos"
]:

    threading.Thread(
        target=loop_terminal,
        daemon=True
    ).start()


iniciar_listener()

gravando = False
gravacao = []
stream = None

gesto_em_execucao = False

while True:

    if (
        gesto_pressionado()
        and
        not gesto_em_execucao
    ):

        gesto_em_execucao = True

        set_status(
            "Gestos ativos..."
        )

        set_mensagem(
            "Detectando gesto..."
        )

        gesto = detectar_gesto()

        if gesto:

            set_mensagem(
                f"Gesto: {gesto}"
            )

            executar_texto(
                gesto
            )

    elif not gesto_pressionado():

        gesto_em_execucao = False

    if alt_pressionado() and not gravando:

        gravando = True

        set_status(
            "Ouvindo..."
        )

        set_mensagem(
            "Aguardando voz..."
        )

        gravacao, callback = ouvir_push_to_talk()

        stream = sd.InputStream(
            samplerate=44100,
            channels=1,
            dtype="int16",
            callback=callback
        )

        stream.start()

    elif (
        not alt_pressionado()
        and gravando
    ):

        gravando = False

        set_status(
            "Processando..."
        )

        stream.stop()
        stream.close()

        caminho = salvar_audio(
            gravacao
        )

        if caminho:

            texto = transcrever_arquivo(
                caminho
            )

            if texto:

                set_mensagem(
                    texto
                )

                executar_texto(
                    texto
                )

        set_status(
            "Pronta."
        )

    time.sleep(0.05)