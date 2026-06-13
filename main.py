import time
import threading
import sounddevice as sd

from core.plugin_loader import carregar_plugins
from core.command_parser import processar_comando
from core.command_router import executar_comando

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

print("\n[NORA] Inicializando...\n")

plugins = carregar_plugins()

print(
    f"[NORA] {len(plugins)} plugin(s) carregado(s)"
)

print(
    "[NORA] Pronta.\n"
)


def executar_texto(comando):

    comando = processar_comando(
        comando
    )

    executar_comando(
        comando,
        plugins
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

    # ======================
    # GESTOS
    # ======================

    if gesto_pressionado() and not gesto_em_execucao:

        gesto_em_execucao = True

        print(
            "\n[NORA] Detectando gesto..."
        )

        gesto = detectar_gesto()

        if gesto:

            print(
                f"\n[NORA] Gesto detectado: {gesto}\n"
            )

            executar_texto(
                gesto
            )

    elif not gesto_pressionado():

        gesto_em_execucao = False

    # ======================
    # VOZ
    # ======================

    if alt_pressionado() and not gravando:

        gravando = True

        gravacao, callback = ouvir_push_to_talk()

        stream = sd.InputStream(
            samplerate=44100,
            channels=1,
            dtype="int16",
            callback=callback
        )

        stream.start()

    elif not alt_pressionado() and gravando:

        gravando = False

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

                print(
                    f"\n[VOCÊ] {texto}\n"
                )

                executar_texto(
                    texto
                )

    time.sleep(0.05)