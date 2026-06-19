from core.speaker import falar

import cv2
import pyautogui
import mediapipe as mp
import time

from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
import core.voice_manager as vm

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

NOME = "controle_por_mao"
DESCRICAO = "Controle por mão"

COMANDOS = {
    "ativar": [
        "controle por mao",
        "controle por mão",
        "controle por gesto",
        "controle por ge",
        "ativar controle por mao",
        "ligar controle por mao",
    ]
}

executando = False
mouse_seguro = False

ultimo_esquerdo = 0
ultimo_direito = 0
ultimo_scroll = 0

detector = None
gravando = False


def dedo_levantado(pontos, ponta, base):
    margem = 0.03

    return pontos[ponta].y < (pontos[base].y - margem)


def iniciar_controle():
    global executando
    global mouse_seguro
    global ultimo_esquerdo
    global ultimo_direito
    global ultimo_scroll
    global detector
    global gravando

    executando = True

    if detector is None:
        options = vision.HandLandmarkerOptions(
            base_options=BaseOptions(
                model_asset_path="models/hand_landmarker.task"
            ),
            num_hands=1,
        )

        detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        falar("Não foi possível abrir a câmera.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    largura_tela, altura_tela = pyautogui.size()

    ultimo_x = largura_tela // 2
    ultimo_y = altura_tela // 2

    suavizacao = 0.35

    while executando:
        ok, frame = cap.read()

        if not ok:
            continue

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        imagem = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        resultado = detector.detect(imagem)

        if resultado.hand_landmarks:
            pontos = resultado.hand_landmarks[0]

            indicador_up = dedo_levantado(pontos, 8, 6)
            medio_up = dedo_levantado(pontos, 12, 10)
            anelar_up = dedo_levantado(pontos, 16, 14)
            minimo_up = dedo_levantado(pontos, 20, 18)

            dedos = sum([
                indicador_up,
                medio_up,
                anelar_up,
                minimo_up
            ])

            indicador = pontos[8]

            agora = time.time()

            polegar_aberto = abs(
                pontos[4].x -
                pontos[3].x
            ) > 0.05

            telefone = (
                polegar_aberto
                and not indicador_up
                and not medio_up
                and not anelar_up
                and minimo_up
            )

            if telefone:
                falar("Estou ouvindo.")

                if not gravando:

                    def _gravar_e_transcrever():
                        global gravando

                        gravando = True

                        try:
                            gravacao, callback = vm.ouvir_push_to_talk()

                            with vm.sd.InputStream(
                                samplerate=vm.TAXA,
                                channels=1,
                                callback=callback
                            ):
                                vm.sd.sleep(4000)

                            caminho = vm.salvar_audio(gravacao)

                            if caminho:
                                texto = vm.transcrever_arquivo(caminho)

                                if texto:
                                    falar(texto)

                        except Exception as e:
                            falar(f"Erro ao ouvir: {e}")

                        finally:
                            gravando = False

                    import threading

                    threading.Thread(
                        target=_gravar_e_transcrever,
                        daemon=True
                    ).start()

                else:
                    falar("Já estou gravando.")

                continue

            # =====================
            # 1 DEDO = MOVER MOUSE
            # =====================
            if dedos == 1 and indicador_up:
                x_min = 0.35
                x_max = 0.65

                y_min = 0.25
                y_max = 0.75

                x = max(x_min, min(indicador.x, x_max))
                y = max(y_min, min(indicador.y, y_max))

                x = (x - x_min) / (x_max - x_min)
                y = (y - y_min) / (y_max - y_min)

                alvo_x = int(x * largura_tela)
                alvo_y = int(y * altura_tela)

                ultimo_x = int(
                    ultimo_x + (alvo_x - ultimo_x) * suavizacao
                )

                ultimo_y = int(
                    ultimo_y + (alvo_y - ultimo_y) * suavizacao
                )

                pyautogui.moveTo(ultimo_x, ultimo_y)

            # =====================
            # 2 DEDOS = CLIQUE ESQUERDO
            # =====================
            if (
                indicador_up
                and medio_up
                and not anelar_up
                and not minimo_up
            ):
                if agora - ultimo_esquerdo > 0.8:
                    pyautogui.click()
                    ultimo_esquerdo = agora

            # =====================
            # 3 DEDOS = CLIQUE DIREITO
            # =====================
            if (
                indicador_up
                and medio_up
                and anelar_up
                and not minimo_up
            ):
                if agora - ultimo_direito > 0.8:
                    pyautogui.rightClick()
                    ultimo_direito = agora

            # =====================
            # 4 DEDOS = SEGURAR
            # =====================
            if (
                indicador_up
                and medio_up
                and anelar_up
                and minimo_up
            ):
                if not mouse_seguro:
                    pyautogui.mouseDown()
                    mouse_seguro = True
            else:
                if mouse_seguro:
                    pyautogui.mouseUp()
                    mouse_seguro = False

            # =====================
            # 5 DEDOS = WIN + TAB
            # =====================
            polegar_aberto = abs(
                pontos[4].x - pontos[3].x
            ) > 0.04

            if (
                polegar_aberto
                and indicador_up
                and medio_up
                and anelar_up
                and minimo_up
            ):
                if agora - ultimo_scroll > 3:
                    pyautogui.hotkey(
                        "win",
                        "tab"
                    )
                    ultimo_scroll = agora

            h, w, _ = frame.shape

            for indice in [4, 8, 12, 16, 20]:
                ponto = pontos[indice]

                cv2.circle(
                    frame,
                    (
                        int(ponto.x * w),
                        int(ponto.y * h)
                    ),
                    10,
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


def executar(acao, comando):
    global executando

    if executando:
        falar("Controle por mão já está ativo.")
        return

    falar("Controle por mão ativado.")
    import threading

    threading.Thread(
        target=iniciar_controle,
        daemon=True
    ).start()