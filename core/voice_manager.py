import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import tempfile
import os


TAXA = 44100


def falar(texto):

    print(f"\n[NORA] {texto}\n")


def transcrever_arquivo(caminho):

    reconhecedor = sr.Recognizer()

    try:

        with sr.AudioFile(caminho) as source:

            audio = reconhecedor.record(source)

        texto = reconhecedor.recognize_google(
            audio,
            language="pt-BR"
        )

        return texto

    except:

        return ""


def ouvir_push_to_talk():

    print("\n[NORA] Ouvindo...")

    gravacao = []

    def callback(indata, frames, time, status):

        gravacao.append(
            indata.copy()
        )

    return gravacao, callback


def salvar_audio(gravacao):

    import numpy as np

    if not gravacao:
        return ""

    audio = np.concatenate(
        gravacao,
        axis=0
    )

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp:

        caminho = temp.name

    write(
        caminho,
        TAXA,
        audio
    )

    return caminho