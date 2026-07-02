import os
import threading
import time

import cv2
import mediapipe as mp
import pyautogui
import sounddevice as sd
from mediapipe.tasks.python import BaseOptions, vision

from core.speaker import falar

try:
    from core.voice_manager import salvar_audio, transcrever_arquivo
except Exception:
    salvar_audio = lambda *_args, **_kwargs: ""
    transcrever_arquivo = lambda *_args, **_kwargs: ""

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

_BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_BASE, "models", "hand_landmarker.task")


class Suavizador:
    def __init__(self, n=6):
        self.hx = []
        self.hy = []
        self.n = n

    def add(self, x, y):
        self.hx.append(x)
        self.hy.append(y)
        if len(self.hx) > self.n:
            self.hx.pop(0)
            self.hy.pop(0)

    def pos(self):
        n = len(self.hx)
        if n == 0:
            return 0, 0
        w = list(range(1, n + 1))
        s = sum(w)
        return int(sum(self.hx[i] * w[i] for i in range(n)) / s), int(sum(self.hy[i] * w[i] for i in range(n)) / s)

    def clear(self):
        self.hx.clear()
        self.hy.clear()


def tamanho_mao(pts):
    dx = pts[0].x - pts[12].x
    dy = pts[0].y - pts[12].y
    return (dx * dx + dy * dy) ** 0.5


def dedo_levantado(pts, ponta, pip):
    escala = tamanho_mao(pts)
    margem = escala * 0.15
    return pts[ponta].y < pts[pip].y - margem


def polegar_levantado(pts):
    escala = tamanho_mao(pts)
    margem = escala * 0.15
    return pts[4].x > pts[3].x + margem


def distancia(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return (dx * dx + dy * dy) ** 0.5


def detectar_gestos(pts):
    ind = dedo_levantado(pts, 8, 6)
    med = dedo_levantado(pts, 12, 10)
    anel = dedo_levantado(pts, 16, 14)
    min_ = dedo_levantado(pts, 20, 18)
    pol = polegar_levantado(pts)
    n_dedos = sum([ind, med, anel, min_])
    pinca = ind and not med and not anel and not min_ and distancia(pts[4], pts[8]) < tamanho_mao(pts) * 0.35
    return {
        "ind": ind,
        "med": med,
        "anel": anel,
        "min": min_,
        "pol": pol,
        "n_dedos": n_dedos,
        "um_dedo": ind and not med and not anel and not min_ and not pinca,
        "dois_dedos": ind and med and not anel and not min_,
        "tres_dedos": ind and med and anel and not min_,
        "quatro_dedos": ind and med and anel and min_,
        "pinca": pinca,
        "mao_aberta": n_dedos == 4,
        "punho": n_dedos == 0 and not pol,
    }


class ControlePorMaoApp:
    def __init__(self):
        self.running = True
        self.detector = None
        self.cap = None
        self.voice_stream = None
        self.voice_frames = []
        self.gravando = False
        self.node_editando = None
        self.last_gesto = "none"
        self.suav = Suavizador(7)
        self.ux, self.uy = 0, 0
        self.larg, self.alt = pyautogui.size()
        self.ux, self.uy = self.larg // 2, self.alt // 2

    def _carregar_detector(self):
        if self.detector is not None:
            return self.detector
        opts = vision.HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=os.path.abspath(MODEL_PATH)),
            num_hands=2,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.5,
        )
        self.detector = vision.HandLandmarker.create_from_options(opts)
        return self.detector

    def _iniciar_gravacao(self):
        if self.gravando or sd is None:
            return
        self.gravando = True
        self.voice_frames = []

        def callback(indata, frames, time_info, status):
            self.voice_frames.append(indata.copy())

        self.voice_stream = sd.InputStream(samplerate=44100, channels=1, dtype="int16", callback=callback)
        self.voice_stream.start()
        falar("Ouvindo o nome do bloco...")

    def _parar_gravacao(self):
        if not self.gravando:
            return
        self.gravando = False
        if self.voice_stream is not None:
            self.voice_stream.stop()
            self.voice_stream.close()
            self.voice_stream = None

        def processar():
            caminho = salvar_audio(self.voice_frames)
            if not caminho:
                return
            texto = transcrever_arquivo(caminho)
            if texto and self.node_editando is not None:
                self.node_editando.txt = texto.strip()
                self.node_editando.resize()
                falar("Nome do bloco atualizado.")

        threading.Thread(target=processar, daemon=True).start()

    def run(self):
        falar("Controle por mão ativado.")
        detector = self._carregar_detector()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            falar("Não foi possível abrir a câmera.")
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            res = detector.detect(img)

            dir_pts = None
            esq_pts = None
            if res.hand_landmarks and res.handedness:
                for i, lm in enumerate(res.hand_landmarks):
                    lado = res.handedness[i][0].display_name
                    if lado == "Right":
                        dir_pts = lm
                    else:
                        esq_pts = lm

            main_pts = esq_pts if esq_pts else dir_pts
            gesto = "none"
            if main_pts is not None:
                g = detectar_gestos(main_pts)
                if g["pinca"]:
                    gesto = "pinca"
                elif g["um_dedo"]:
                    gesto = "um"
                elif g["dois_dedos"]:
                    gesto = "dois"
                elif g["tres_dedos"]:
                    gesto = "tres"
                elif g["quatro_dedos"]:
                    gesto = "quatro"
                elif g["mao_aberta"]:
                    gesto = "aberta"
                elif g["punho"]:
                    gesto = "punho"

                if gesto == "um" and main_pts is not None:
                    x = max(0.25, min(main_pts[8].x, 0.75))
                    y = max(0.15, min(main_pts[8].y, 0.85))
                    x = (x - 0.25) / 0.5
                    y = (y - 0.15) / 0.7
                    ax = int(x * self.larg)
                    ay = int(y * self.alt)
                    self.suav.add(ax, ay)
                    sx, sy = self.suav.pos()
                    if abs(sx - self.ux) > 3 or abs(sy - self.uy) > 3:
                        pyautogui.moveTo(sx, sy)
                        self.ux, self.uy = sx, sy
                else:
                    self.suav.clear()

                if gesto == "dois" and self.last_gesto != "dois":
                    pyautogui.click(button="right")
                elif gesto == "quatro" and self.last_gesto != "quatro":
                    pyautogui.hotkey("ctrl", "c")
                elif gesto == "tres" and self.last_gesto != "tres":
                    self._iniciar_gravacao()
                elif gesto != "tres" and self.last_gesto == "tres":
                    self._parar_gravacao()

            else:
                self.suav.clear()
                if self.last_gesto == "tres":
                    self._parar_gravacao()

            if gesto != "tres" and self.gravando:
                self._parar_gravacao()

            self.last_gesto = gesto

            cv2.putText(frame, f"Gesto: {gesto}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2)
            cv2.putText(frame, "Pinça=clique, 1 dedo=mouse, 2 dedos=dir, 3 dedos=ouvir, 4 dedos=ctrl+c", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.imshow("NORA - Controle por Mão", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        if self.gravando:
            self._parar_gravacao()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        falar("Controle por mão encerrado.")


if __name__ == "__main__":
    ControlePorMaoApp().run()
