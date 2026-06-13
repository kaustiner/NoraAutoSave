import pyttsx3


def falar(texto):

    print(
        f"\n[NORA] {texto}\n"
    )

    try:

        engine = pyttsx3.init()

        engine.say(texto)

        engine.runAndWait()

        engine.stop()

    except Exception as erro:

        print(
            f"[NORA] Erro de voz: {erro}"
        )