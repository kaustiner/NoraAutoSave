from core.speaker import falar

import cv2
import pyautogui
import mediapipe as mp
import math
import time

from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

NOME = "controle_por_mao"

DESCRICAO = "Controle por mão"

COMANDOS = {
    "ativar": [
        "controle por mao",
        "ativar controle por mao",
        "ligar controle por mao"
    ]
}

executando = False
mouse_seguro = False

ultimo_esquerdo = 0
ultimo_direito = 0

detector = None


def distancia(p1, p2):

    return math.sqrt(
        (p1.x - p2.x) ** 2 +
        (p1.y - p2.y) ** 2
    )


def dedo_levantado(
    pontos,
    ponta,
    base
):

    return pontos[ponta].y < pontos[base].y


def iniciar_controle():

    global executando
    global mouse_seguro
    global ultimo_esquerdo
    global ultimo_direito
    global detector

    executando = True

    if detector is None:

        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path="models/hand_landmarker.task"
            ),
            num_hands=1
        )

        detector = vision.HandLandmarker.create_from_options(
            options
        )

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        falar(
            "Não foi possível abrir a câmera."
        )

        return

    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    largura_tela, altura_tela = pyautogui.size()

    ultimo_x = largura_tela // 2
    ultimo_y = altura_tela // 2

    suavizacao = 0.12

    while executando:

        ok, frame = cap.read()

        if not ok:
            continue

        frame = cv2.flip(
            frame,
            1
        )

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

            pontos = resultado.hand_landmarks[0]

            palma = pontos[9]

            polegar = pontos[4]

            indicador = pontos[8]

            medio = pontos[12]

            anelar = pontos[16]

            minimo = pontos[20]

            indicador_up = dedo_levantado(
                pontos,
                8,
                6
            )

            medio_up = dedo_levantado(
                pontos,
                12,
                10
            )

            anelar_up = dedo_levantado(
                pontos,
                16,
                14
            )

            minimo_up = dedo_levantado(
                pontos,
                20,
                18
            )

            agora = time.time()

            # =====================
            # MOVER MOUSE (✊)
            # =====================

            if (
                not indicador_up and
                not medio_up and
                not anelar_up and
                not minimo_up
            ):

                x_min = 0.20
                x_max = 0.80

                y_min = 0.20
                y_max = 0.80

                x = max(
                    x_min,
                    min(
                        palma.x,
                        x_max
                    )
                )

                y = max(
                    y_min,
                    min(
                        palma.y,
                        y_max
                    )
                )

                x = (
                    (x - x_min)
                    /
                    (x_max - x_min)
                )

                y = (
                    (y - y_min)
                    /
                    (y_max - y_min)
                )

                alvo_x = int(
                    x * largura_tela
                )

                alvo_y = int(
                    y * altura_tela
                )

                ultimo_x = int(
                    ultimo_x +
                    (
                        alvo_x - ultimo_x
                    ) * suavizacao
                )

                ultimo_y = int(
                    ultimo_y +
                    (
                        alvo_y - ultimo_y
                    ) * suavizacao
                )

                pyautogui.moveTo(
                    ultimo_x,
                    ultimo_y
                )

            # =====================
            # JOINHA = CLIQUE ESQUERDO
            # =====================

            if (
                not indicador_up and
                not medio_up and
                not anelar_up and
                not minimo_up and
                polegar.x > pontos[3].x
            ):

                if agora - ultimo_esquerdo > 1:

                    pyautogui.click()

                    ultimo_esquerdo = agora

            # =====================
            # ✌️ CLIQUE DIREITO
            # =====================

            if (
                indicador_up and
                medio_up and
                not anelar_up and
                not minimo_up
            ):

                if agora - ultimo_direito > 1:

                    pyautogui.rightClick()

                    ultimo_direito = agora

            # =====================
            # 🤏 SEGURAR CLIQUE
            # =====================

            dist = distancia(
                polegar,
                indicador
            )

            if dist < 0.05:

                if not mouse_seguro:

                    pyautogui.mouseDown()

                    mouse_seguro = True

            else:

                if mouse_seguro:

                    pyautogui.mouseUp()

                    mouse_seguro = False

            h, w, _ = frame.shape

            cv2.circle(
                frame,
                (
                    int(
                        palma.x * w
                    ),
                    int(
                        palma.y * h
                    )
                ),
                12,
                (0, 255, 0),
                -1
            )

        cv2.imshow(
            "NORA - Controle por Mao",
            frame
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

    if mouse_seguro:

        pyautogui.mouseUp()

    cap.release()

    cv2.destroyAllWindows()

    executando = False


def executar(
    acao,
    comando
):

    global executando

    if executando:

        falar(
            "Controle por mão já está ativo."
        )

        return

    falar(
        "Controle por mão ativado."
    )

    iniciar_controle()