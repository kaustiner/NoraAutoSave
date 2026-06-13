import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from core.custom_gesture_manager import (
    procurar_semelhante
)

MODELO = "models/hand_landmarker.task"

base_options = python.BaseOptions(
    model_asset_path=MODELO
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(
    options
)


def capturar_pontos():

    camera = cv2.VideoCapture(0)

    try:

        while True:

            ok, frame = camera.read()

            if not ok:

                continue

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            imagem = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            resultado = detector.detect(
                imagem
            )

            if resultado.hand_landmarks:

                pontos = []

                for landmark in resultado.hand_landmarks[0]:

                    pontos.append([
                        landmark.x,
                        landmark.y
                    ])

                return pontos

    finally:

        camera.release()


def detectar_gesto():

    pontos = capturar_pontos()

    nome, score = procurar_semelhante(
        pontos
    )

    if score >= 90:

        return nome

    return None