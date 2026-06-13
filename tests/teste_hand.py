import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

modelo = "models/hand_landmarker.task"

base_options = python.BaseOptions(
    model_asset_path=modelo
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(
    options
)

camera = cv2.VideoCapture(0)

print("[NORA] Procurando mão...")

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

        print(
            "[NORA] Mão detectada"
        )

        break

camera.release()