from core.speaker import falar

import cv2
import pyautogui
import mediapipe as mp
import time
import threading
import numpy as np

from mediapipe.tasks.python import vision
from mediapipe.tasks.python import BaseOptions
import core.voice_manager as vm
import sounddevice as sd

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

NOME = "controle_por_mao"
DESCRICAO = "Controle por mão"

COMANDOS = {
    "ativar": [
        "controle por mao",
        "controle por mão",
        "controle por gesto",
        "ativar controle por mao",
        "ligar controle por mao",
    ]
}

executando = False
detector = None

mouse_pausado = False
mouse_seguro = False
gravando_voz = False
joinha_inicio = None

ultimo_esquerdo = 0
ultimo_direito = 0
ultimo_win = 0
ultimo_selecionar = 0
ultimo_copiar = 0

# Histórico para suavização
historico_x = []
historico_y = []
HISTORICO_MAX = 8

# Conexões da mão (MediaPipe hand skeleton)
CONEXOES = [
    (0,1),(1,2),(2,3),(3,4),       # polegar
    (0,5),(5,6),(6,7),(7,8),       # indicador
    (0,9),(9,10),(10,11),(11,12),  # médio
    (0,13),(13,14),(14,15),(15,16),# anelar
    (0,17),(17,18),(18,19),(19,20),# mínimo
    (5,9),(9,13),(13,17)           # palma
]


def dedo_levantado(pontos, ponta, base, margem=0.04):
    return pontos[ponta].y < (pontos[base].y - margem)


def distancia(p1, p2):
    return ((p1.x - p2.x)**2 + (p1.y - p2.y)**2) ** 0.5


def suavizar_posicao(x, y):
    global historico_x, historico_y
    historico_x.append(x)
    historico_y.append(y)
    if len(historico_x) > HISTORICO_MAX:
        historico_x.pop(0)
        historico_y.pop(0)
    # Média ponderada — frames mais recentes têm mais peso
    pesos = list(range(1, len(historico_x) + 1))
    soma = sum(pesos)
    sx = sum(historico_x[i] * pesos[i] for i in range(len(historico_x))) / soma
    sy = sum(historico_y[i] * pesos[i] for i in range(len(historico_y))) / soma
    return int(sx), int(sy)


def detectar_gestos(pontos):
    indicador = dedo_levantado(pontos, 8, 6)
    medio     = dedo_levantado(pontos, 12, 10)
    anelar    = dedo_levantado(pontos, 16, 14)
    minimo    = dedo_levantado(pontos, 20, 18)

    # Polegar: compara horizontal pois varia conforme orientação
    polegar = abs(pontos[4].x - pontos[3].x) > 0.05

    # Joinha: polegar aponta pra cima, demais dobrados
    joinha = (
        pontos[4].y < pontos[2].y - 0.06
        and not indicador
        and not medio
        and not anelar
        and not minimo
    )

    # Mão aberta: todos levantados
    mao_aberta = indicador and medio and anelar and minimo

    # Telefone: polegar + mínimo, resto dobrado
    telefone = (
        polegar
        and not indicador
        and not medio
        and not anelar
        and minimo
    )

    # Punho ✊: tudo dobrado, polegar ao lado
    punho = (
        not indicador and not medio
        and not anelar and not minimo
        and not joinha
        and abs(pontos[4].x - pontos[3].x) < 0.06
    )

    # Punho 👊: polegar dobrado pra dentro
    punho_copia = (
        not indicador and not medio
        and not anelar and not minimo
        and not joinha
        and pontos[4].x < pontos[3].x - 0.02
    )

    # 4 dedos sem polegar = Win
    quatro_dedos = indicador and medio and anelar and minimo and not polegar

    # 1 dedo = mover mouse
    um_dedo = indicador and not medio and not anelar and not minimo

    # 2 dedos = clique esquerdo
    dois_dedos = indicador and medio and not anelar and not minimo

    # 3 dedos = clique direito
    tres_dedos = indicador and medio and anelar and not minimo

    return {
        "indicador": indicador,
        "medio": medio,
        "anelar": anelar,
        "minimo": minimo,
        "polegar": polegar,
        "joinha": joinha,
        "mao_aberta": mao_aberta,
        "telefone": telefone,
        "punho": punho,
        "punho_copia": punho_copia,
        "quatro_dedos": quatro_dedos,
        "um_dedo": um_dedo,
        "dois_dedos": dois_dedos,
        "tres_dedos": tres_dedos,
    }


def desenhar_mao(frame, pontos):
    h, w, _ = frame.shape

    coords = [(int(p.x * w), int(p.y * h)) for p in pontos]

    # Linhas do esqueleto
    for a, b in CONEXOES:
        cv2.line(frame, coords[a], coords[b], (0, 200, 255), 2)

    # Bolinhas nas pontas dos dedos e articulações principais
    for idx in range(21):
        cor = (0, 255, 0) if idx in [4, 8, 12, 16, 20] else (255, 255, 255)
        raio = 8 if idx in [4, 8, 12, 16, 20] else 4
        cv2.circle(frame, coords[idx], raio, cor, -1)


def gravar_e_executar():
    global gravando_voz

    try:
        gravacao = []

        def callback(indata, frames, time_info, status):
            gravacao.append(indata.copy())

        stream = sd.InputStream(
            samplerate=vm.TAXA,
            channels=1,
            dtype="int16",
            callback=callback
        )
        stream.start()

        while gravando_voz:
            time.sleep(0.05)

        stream.stop()
        stream.close()

        caminho = vm.salvar_audio(gravacao)
        if caminho:
            texto = vm.transcrever_arquivo(caminho)
            if texto:
                falar(f"Executando: {texto}")
                from core.command_parser import processar_comando
                from core.command_router import executar_comando
                from core.plugin_loader import carregar_plugins
                plugins = carregar_plugins()
                cmd = processar_comando(texto)
                executar_comando(cmd, plugins)

    except Exception as e:
        falar(f"Erro ao gravar: {e}")


def iniciar_controle():
    global executando, detector
    global mouse_pausado, mouse_seguro, gravando_voz, joinha_inicio
    global ultimo_esquerdo, ultimo_direito, ultimo_win
    global ultimo_selecionar, ultimo_copiar
    global historico_x, historico_y

    executando = True
    mouse_pausado = False
    mouse_seguro = False
    gravando_voz = False
    joinha_inicio = None
    historico_x = []
    historico_y = []

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
        executando = False
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    largura_tela, altura_tela = pyautogui.size()

    # Zona morta para evitar micro-tremores
    ZONA_MORTA = 5
    ultimo_mouse_x = largura_tela // 2
    ultimo_mouse_y = altura_tela // 2

    falar("Controle por mão ativado.")

    # Confirmação visual do joinha na tela
    joinha_progresso = 0.0

    while executando:
        ok, frame = cap.read()
        if not ok:
            continue

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagem = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        resultado = detector.detect(imagem)
        agora = time.time()

        if resultado.hand_landmarks:
            pontos = resultado.hand_landmarks[0]
            g = detectar_gestos(pontos)

            desenhar_mao(frame, pontos)

            # ─── JOINHA por 3s = encerrar ───
            if g["joinha"]:
                if joinha_inicio is None:
                    joinha_inicio = agora
                decorrido = agora - joinha_inicio
                joinha_progresso = min(decorrido / 3.0, 1.0)

                # Barra de progresso na tela
                cv2.rectangle(frame, (20, 440), (620, 465), (50, 50, 50), -1)
                cv2.rectangle(frame, (20, 440), (20 + int(600 * joinha_progresso), 465), (0, 255, 100), -1)
                cv2.putText(frame, "Segure joinha para encerrar...", (20, 435),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 100), 2)

                if decorrido >= 3.0:
                    falar("Encerrando controle por mão.")
                    executando = False
                    break
            else:
                joinha_inicio = None
                joinha_progresso = 0.0

            # ─── TELEFONE = gravar voz ───
            if g["telefone"]:
                if not gravando_voz:
                    gravando_voz = True
                    falar("Ouvindo...")
                    threading.Thread(target=gravar_e_executar, daemon=True).start()
            else:
                if gravando_voz:
                    gravando_voz = False

            # ─── MÃO ABERTA = pausar (sem Win+Tab) ───
            if g["mao_aberta"] and not g["um_dedo"]:
                mouse_pausado = True
                cv2.putText(frame, "PAUSADO", (260, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 100, 255), 3)

            # ─── 1 DEDO = retoma e move mouse ───
            if g["um_dedo"]:
                mouse_pausado = False

                x_min, x_max = 0.30, 0.70
                y_min, y_max = 0.20, 0.80

                x = max(x_min, min(pontos[8].x, x_max))
                y = max(y_min, min(pontos[8].y, y_max))

                x = (x - x_min) / (x_max - x_min)
                y = (y - y_min) / (y_max - y_min)

                alvo_x = int(x * largura_tela)
                alvo_y = int(y * altura_tela)

                sx, sy = suavizar_posicao(alvo_x, alvo_y)

                # Zona morta: só move se deslocou o suficiente
                if abs(sx - ultimo_mouse_x) > ZONA_MORTA or abs(sy - ultimo_mouse_y) > ZONA_MORTA:
                    pyautogui.moveTo(sx, sy)
                    ultimo_mouse_x = sx
                    ultimo_mouse_y = sy

            if not mouse_pausado:

                # ─── 2 DEDOS = clique esquerdo ───
                if g["dois_dedos"] and not g["anelar"] and not g["minimo"]:
                    if agora - ultimo_esquerdo > 0.8:
                        pyautogui.click()
                        ultimo_esquerdo = agora

                # ─── 3 DEDOS = clique direito ───
                if g["tres_dedos"] and not g["minimo"]:
                    if agora - ultimo_direito > 0.8:
                        pyautogui.rightClick()
                        ultimo_direito = agora

                # ─── 4 DEDOS sem polegar = WIN ───
                if g["quatro_dedos"]:
                    if agora - ultimo_win > 1.5:
                        pyautogui.press("win")
                        ultimo_win = agora

                # ─── PUNHO ✊ = Ctrl+A ───
                if g["punho"] and not g["punho_copia"]:
                    if agora - ultimo_selecionar > 1.0:
                        pyautogui.hotkey("ctrl", "a")
                        ultimo_selecionar = agora

                # ─── PUNHO 👊 = Ctrl+C ───
                if g["punho_copia"]:
                    if agora - ultimo_copiar > 1.0:
                        pyautogui.hotkey("ctrl", "c")
                        ultimo_copiar = agora

        else:
            # Sem mão na tela
            historico_x.clear()
            historico_y.clear()

        # Label de gesto atual no canto
        if resultado.hand_landmarks:
            pontos = resultado.hand_landmarks[0]
            g = detectar_gestos(pontos)
            gesto_label = ""
            if g["joinha"]:        gesto_label = "👍 Joinha"
            elif g["telefone"]:    gesto_label = "🤙 Telefone (gravando)"
            elif g["mao_aberta"]:  gesto_label = "✋ Pausado"
            elif g["punho_copia"]: gesto_label = "👊 Ctrl+C"
            elif g["punho"]:       gesto_label = "✊ Ctrl+A"
            elif g["quatro_dedos"]:gesto_label = "4 dedos = Win"
            elif g["tres_dedos"]:  gesto_label = "3 dedos = clique direito"
            elif g["dois_dedos"]:  gesto_label = "2 dedos = clique esquerdo"
            elif g["um_dedo"]:     gesto_label = "☝️ Movendo mouse"
            if gesto_label:
                cv2.putText(frame, gesto_label, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("NORA - Controle por Mao", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    # Limpeza
    gravando_voz = False
    cap.release()
    cv2.destroyAllWindows()
    executando = False


def executar(acao, comando):
    global executando

    if executando:
        falar("Controle por mão já está ativo.")
        return

    threading.Thread(
        target=iniciar_controle,
        daemon=True
    ).start()