"""
NORA Canvas App — roda como processo independente
Usa HandLandmarker (mesma API do controle_por_mao.py)

CONTROLES:
  Pinça        = Mover bloco (arrastar)
  1 dedo       = Mover cursor do canvas
  2 dedos      = Conectar blocos (1º gesto = origem, 2º = destino)
  3 dedos      = Editar bloco (microfone ligado enquanto segura, para ao tirar)
  4 dedos      = Deletar bloco sob o cursor
  Mão aberta   = Criar bloco na posição do cursor
  ESC          = Sair
  Mouse botão direito = Criar bloco
  Mouse botão esquerdo = Selecionar / conectar blocos
"""

import os
import math
import random
import threading
import time

import cv2
import mediapipe as mp
import pygame
from mediapipe.tasks.python import BaseOptions, vision

try:
    import sounddevice as sd
    import speech_recognition as sr
    import numpy as np
    import tempfile
    from scipy.io.wavfile import write as wav_write
    AUDIO_OK = True
except Exception:
    AUDIO_OK = False

_BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(_BASE, "models", "hand_landmarker.task")

# ── Paleta ──────────────────────────────────────────────────────────────────
BG      = (5, 7, 20)
ACCENT  = (0, 220, 255)
ACCENT2 = (160, 80, 255)
ACCENT3 = (0, 255, 140)
WARN    = (255, 80, 80)
WHITE   = (220, 230, 255)
GRAY    = (80, 100, 140)
NODE_BG = (10, 18, 45)
NODE_BRD = (0, 180, 220)
CURSOR_C = (0, 255, 200)

W, H       = 1400, 900
CAM_W, CAM_H = 280, 210
FPS        = 60
NODE_MIN_W = 140
CURSOR_RAD = 14
TAXA_VOZ   = 44100

# Zona de movimento da mão (evita bordas da câmera)
X_MIN, X_MAX = 0.20, 0.80
Y_MIN, Y_MAX = 0.15, 0.85

# Suavização do cursor
SMOOTH = 0.18   # menor = mais suave / lento; maior = mais ágil
DEAD_ZONE = 5   # pixels — ignora micro-tremores


def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, v))


# ── Detecção de gestos ──────────────────────────────────────────────────────

def _tam(pts):
    dx, dy = pts[0].x - pts[12].x, pts[0].y - pts[12].y
    return (dx * dx + dy * dy) ** 0.5


def _levantado(pts, tip, pip):
    return pts[tip].y < pts[pip].y - _tam(pts) * 0.15


def _polegar(pts):
    # Aceita polegar pra qualquer lado (câmera espelhada inverte a mão)
    return abs(pts[4].x - pts[3].x) > _tam(pts) * 0.10


def _dist(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


def gestos(pts):
    i = _levantado(pts, 8,  6)
    m = _levantado(pts, 12, 10)
    a = _levantado(pts, 16, 14)
    p = _levantado(pts, 20, 18)
    t = _polegar(pts)
    n = sum([i, m, a, p])
    # Pinça: só indicador levantado E polegar perto da ponta do indicador
    pinch = (i and not m and not a and not p
             and _dist(pts[4], pts[8]) < _tam(pts) * 0.35)
    # Mão aberta = todos os 4 dedos levantados (polegar opcional — difícil detectar)
    aberta = n == 4
    # Quatro = 4 dedos SEM polegar levantado (polegar dobrado/junto)
    quatro = i and m and a and p and not t
    return {
        "um":     i and not m and not a and not p and not pinch,
        "dois":   i and m and not a and not p,
        "tres":   i and m and a and not p,
        "quatro": quatro,
        "aberta": aberta and not quatro,
        "punho":  n == 0,
        "pinca":  pinch,
    }


# ── Suavizador de cursor ────────────────────────────────────────────────────

class Suavizador:
    def __init__(self, n=8):
        self.hx, self.hy = [], []
        self.n = n

    def add(self, x, y):
        self.hx.append(x)
        self.hy.append(y)
        if len(self.hx) > self.n:
            self.hx.pop(0)
            self.hy.pop(0)

    def media(self):
        n = len(self.hx)
        if n == 0:
            return 0, 0
        # Média ponderada (frames mais recentes têm mais peso)
        pesos = list(range(1, n + 1))
        s = sum(pesos)
        return (int(sum(self.hx[i] * pesos[i] for i in range(n)) / s),
                int(sum(self.hy[i] * pesos[i] for i in range(n)) / s))

    def clear(self):
        self.hx.clear()
        self.hy.clear()


# ── Partículas ──────────────────────────────────────────────────────────────

class Particula:
    def __init__(self, x, y, cor=ACCENT3):
        self.x, self.y = float(x), float(y)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -0.5)
        self.life = self.max_life = random.randint(25, 55)
        self.cor = cor
        self.r = random.randint(2, 4)

    def tick(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.06
        self.life -= 1

    def draw(self, s):
        a = self.life / self.max_life
        r, g, b = self.cor
        pygame.draw.circle(s, (int(r * a), int(g * a), int(b * a)),
                           (int(self.x), int(self.y)), self.r)


# ── Nó (bloco) ──────────────────────────────────────────────────────────────

class No:
    _uid = 0

    def __init__(self, x, y, txt="Novo bloco"):
        No._uid += 1
        self.id  = No._uid
        self.x, self.y = x, y
        self.txt = txt
        self.w   = max(NODE_MIN_W, len(txt) * 11 + 28)
        self.h   = 52
        self.sel = self.hov = self.ed = False
        self.pulso = random.uniform(0, math.pi * 2)
        self.born  = time.time()

    def resize(self):
        self.w = max(NODE_MIN_W, len(self.txt) * 11 + 28)

    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y - self.h // 2,
                           self.w, self.h)

    def hit(self, px, py):
        return self.rect().collidepoint(px, py)

    def draw(self, surf, font, tick):
        self.pulso += 0.05
        age = min(1.0, (time.time() - self.born) * 3)
        r = self.rect()
        s = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
        bx, by = 10, 10

        ga = 80 if self.sel else int(25 + 18 * math.sin(self.pulso))
        pygame.draw.rect(s, (*ACCENT, _clamp(ga)),
                         (4, 4, r.w + 12, r.h + 12), border_radius=14)

        bg = (15, 28, 65) if self.sel else NODE_BG
        pygame.draw.rect(s, bg, (bx, by, r.w, r.h), border_radius=10)

        bc = ACCENT2 if self.sel else (ACCENT3 if self.hov else NODE_BRD)
        pygame.draw.rect(s, bc, (bx, by, r.w, r.h),
                         border_radius=10, width=2 if self.sel else 1)
        pygame.draw.rect(s, ACCENT2 if self.sel else ACCENT,
                         (bx, by, int(r.w * age), 2), border_radius=2)

        # Borda piscando em vermelho se em edição
        if self.ed:
            pulso_ed = int(128 + 127 * math.sin(tick * 0.15))
            pygame.draw.rect(s, (255, 80, 80, _clamp(pulso_ed)),
                             (bx, by, r.w, r.h), border_radius=10, width=2)

        lbl = self.txt + ("|" if self.ed and tick % 60 < 30 else "")
        tc  = ACCENT if self.sel else WHITE
        t   = font.render(lbl, True, tc)
        s.blit(t, (bx + (r.w - t.get_width()) // 2,
                   by + (r.h - t.get_height()) // 2))
        surf.blit(s, (r.x - 10, r.y - 10))


# ── Conexão ──────────────────────────────────────────────────────────────────

class Conn:
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.p = random.uniform(0, math.pi * 2)

    def draw(self, surf, tick):
        self.p += 0.03
        ax, ay, bx, by = self.a.x, self.a.y, self.b.x, self.b.y
        s = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.line(s, (*ACCENT, _clamp(int(90 + 55 * math.sin(self.p)))),
                         (ax, ay), (bx, by), 2)
        t = (tick % 120) / 120
        px, py = int(ax + (bx - ax) * t), int(ay + (by - ay) * t)
        pygame.draw.circle(s, (*ACCENT3, 200), (px, py), 4)
        pygame.draw.circle(s, (*ACCENT3, 70),  (px, py), 9)
        surf.blit(s, (0, 0))


# ── App principal ────────────────────────────────────────────────────────────

class App:
    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption("NORA Canvas")
        self.clock   = pygame.time.Clock()
        self.font    = pygame.font.SysFont("Segoe UI", 18)
        self.font_s  = pygame.font.SysFont("Segoe UI", 13)
        self.font_l  = pygame.font.SysFont("Segoe UI", 26, bold=True)

        self.nos   = []
        self.cons  = []
        self.parts = []
        self.hist  = []

        # Posição bruta da câmera (atualizada pela thread)
        self.cur_raw = [W // 2, H // 2]
        # Posição suavizada (atualizada no loop principal)
        self.cur_s   = [float(W // 2), float(H // 2)]
        self.suav    = Suavizador(8)

        self.gesto     = "none"
        self.gesto_ant = "none"

        self.arr      = None   # nó sendo arrastado
        self.sel      = None   # nó selecionado
        self.conn_src = None   # nó fonte de conexão

        # Debounces (em ticks)
        self.cd_criar   = 0
        self.cd_deletar = 0
        self.cd_desf    = 0

        self.tick = 0
        self.msg  = ""
        self.msg_t = 0

        self.stars = [(random.randint(0, W), random.randint(0, H),
                       random.uniform(0.3, 1.5)) for _ in range(100)]

        # Microfone (3 dedos)
        self.gravando      = False
        self.voz_frames    = []
        self.voz_stream    = None
        self.no_editando   = None

        # Câmera
        self.cam_frame    = None
        self.cam_ok       = False
        self.cap          = None
        self._cam_running = True

        n0 = No(W // 2, H // 2, "NORA Canvas")
        self.nos.append(n0)
        self._save()

        self._cam_thread = threading.Thread(target=self._cam_loop, daemon=True)
        self._cam_thread.start()

    # ── Thread da câmera ────────────────────────────────────────────────────

    def _cam_loop(self):
        model = os.path.abspath(MODEL_PATH)
        detector = None
        if os.path.exists(model):
            try:
                opts = vision.HandLandmarkerOptions(
                    base_options=BaseOptions(model_asset_path=model),
                    num_hands=1,
                    min_hand_detection_confidence=0.55,
                    min_hand_presence_confidence=0.55,
                    min_tracking_confidence=0.45,
                )
                detector = vision.HandLandmarker.create_from_options(opts)
            except Exception as e:
                print(f"[Canvas] Erro ao carregar detector: {e}")
        else:
            print(f"[Canvas] Modelo não encontrado: {model}")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[Canvas] Câmera indisponível — use o mouse.")
            cap.release()
            return

        self.cap = cap
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cam_ok = True

        while self._cam_running:
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.02)
                continue

            # Espelha horizontalmente (câmera frontal)
            frame = cv2.flip(frame, 1)

            if detector:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                try:
                    res = detector.detect(img)
                except Exception:
                    res = None

                if res and res.hand_landmarks:
                    pts = res.hand_landmarks[0]
                    g   = gestos(pts)
                    self.gesto = (
                        "pinca"  if g["pinca"]  else
                        "punho"  if g["punho"]  else
                        "quatro" if g["quatro"] else
                        "tres"   if g["tres"]   else
                        "dois"   if g["dois"]   else
                        "um"     if g["um"]     else
                        "none"
                    )

                    # Ponto de controle: ponta do indicador (landmark 8)
                    # Normaliza dentro da zona de movimento
                    rx = pts[8].x
                    ry = pts[8].y
                    rx = (max(X_MIN, min(rx, X_MAX)) - X_MIN) / (X_MAX - X_MIN)
                    ry = (max(Y_MIN, min(ry, Y_MAX)) - Y_MIN) / (Y_MAX - Y_MIN)
                    self.cur_raw = [int(rx * W), int(ry * H)]
                else:
                    self.gesto = "none"

            # Desenha esqueleto da mão no frame
            if res and res.hand_landmarks:
                fh, fw = frame.shape[:2]
                CONEXOES_MAO = [
                    (0,1),(1,2),(2,3),(3,4),
                    (0,5),(5,6),(6,7),(7,8),
                    (0,9),(9,10),(10,11),(11,12),
                    (0,13),(13,14),(14,15),(15,16),
                    (0,17),(17,18),(18,19),(19,20),
                    (5,9),(9,13),(13,17),(0,17)
                ]
                for landmarks in res.hand_landmarks:
                    coords = [(int(lm.x * fw), int(lm.y * fh)) for lm in landmarks]
                    # Conexões
                    for a, b in CONEXOES_MAO:
                        cv2.line(frame, coords[a], coords[b], (0, 180, 220), 2)
                    # Pontos
                    for idx, (px, py) in enumerate(coords):
                        cor = (0, 255, 140) if idx in [4,8,12,16,20] else (255, 255, 255)
                        r   = 6 if idx in [4,8,12,16,20] else 3
                        cv2.circle(frame, (px, py), r, cor, -1)
                    # Destaca ponta do indicador (controle)
                    cv2.circle(frame, coords[8], 10, (0, 220, 255), 2)

            small = cv2.resize(frame, (CAM_W, CAM_H))
            self.cam_frame = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            time.sleep(0.016)

        cap.release()
        self.cap    = None
        self.cam_ok = False

    # ── Histórico ────────────────────────────────────────────────────────────

    def _save(self):
        snap  = [(n.id, n.x, n.y, n.txt) for n in self.nos]
        conns = [(c.a.id, c.b.id) for c in self.cons]
        self.hist.append((snap, conns))
        if len(self.hist) > 30:
            self.hist.pop(0)

    def _undo(self):
        if len(self.hist) < 2:
            self._info("Nada para desfazer")
            return
        self.hist.pop()
        snap, conns = self.hist[-1]
        self.nos = []
        for sid, sx, sy, st in snap:
            n    = No(sx, sy, st)
            n.id = sid
            self.nos.append(n)
        nd = {n.id: n for n in self.nos}
        self.cons = [Conn(nd[a], nd[b]) for a, b in conns
                     if a in nd and b in nd]
        self._info("Desfeito")

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _info(self, t, d=90):
        self.msg   = t
        self.msg_t = d

    def _no_em(self, x, y):
        for n in reversed(self.nos):
            if n.hit(x, y):
                return n
        return None

    def _criar(self, x, y):
        n = No(x, y)
        self.nos.append(n)
        for _ in range(10):
            self.parts.append(Particula(x, y))
        self._save()
        self._info("Bloco criado!")
        return n

    def _deletar(self, n):
        self.cons = [c for c in self.cons if c.a is not n and c.b is not n]
        if n in self.nos:
            self.nos.remove(n)
        self._save()
        self._info("Bloco deletado")

    def _link(self, a, b):
        if a is b:
            return
        for c in self.cons:
            if (c.a is a and c.b is b) or (c.a is b and c.b is a):
                return
        self.cons.append(Conn(a, b))
        self._save()
        self._info("Blocos conectados!")

    # ── Microfone ────────────────────────────────────────────────────────────

    def _iniciar_voz(self, no):
        if not AUDIO_OK or self.gravando:
            return
        self.gravando   = True
        self.voz_frames = []
        self.no_editando = no
        self._info("🎤 Ouvindo… tire 3 dedos para confirmar")

        def cb(indata, frames, t, status):
            self.voz_frames.append(indata.copy())

        try:
            self.voz_stream = sd.InputStream(
                samplerate=TAXA_VOZ, channels=1,
                dtype="int16", callback=cb)
            self.voz_stream.start()
        except Exception as e:
            self._info(f"Erro mic: {e}")
            self.gravando = False

    def _parar_voz(self):
        if not self.gravando:
            return
        self.gravando = False
        if self.voz_stream:
            try:
                self.voz_stream.stop()
                self.voz_stream.close()
            except Exception:
                pass
            self.voz_stream = None

        frames  = self.voz_frames
        no_alvo = self.no_editando
        self.voz_frames  = []
        self.no_editando = None

        def processar():
            if not frames or no_alvo is None:
                return
            try:
                audio = np.concatenate(frames, axis=0)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    caminho = f.name
                wav_write(caminho, TAXA_VOZ, audio)
                rec  = sr.Recognizer()
                with sr.AudioFile(caminho) as src:
                    data = rec.record(src)
                texto = rec.recognize_google(data, language="pt-BR")
                if texto:
                    no_alvo.txt = texto.strip()
                    no_alvo.resize()
                    self._info(f"Nome: {texto.strip()}")
                    self._save()
                os.remove(caminho)
            except Exception as e:
                self._info(f"Erro ao transcrever: {e}")

        threading.Thread(target=processar, daemon=True).start()

    # ── Lógica de gesto por frame ─────────────────────────────────────────

    def _update_gesto(self):
        # Suavização do cursor
        self.suav.add(self.cur_raw[0], self.cur_raw[1])
        sx, sy = self.suav.media()

        # Dead zone — só atualiza cursor se movimento for significativo
        dx = sx - self.cur_s[0]
        dy = sy - self.cur_s[1]
        if abs(dx) > DEAD_ZONE or abs(dy) > DEAD_ZONE:
            self.cur_s[0] += dx * SMOOTH
            self.cur_s[1] += dy * SMOOTH

        cx, cy = int(self.cur_s[0]), int(self.cur_s[1])
        g      = self.gesto
        ant    = self.gesto_ant

        # Hover
        hov = self._no_em(cx, cy)
        for n in self.nos:
            n.hov = (n is hov)

        # Cooldowns
        if self.cd_criar   > 0: self.cd_criar   -= 1
        if self.cd_deletar > 0: self.cd_deletar -= 1
        if self.cd_desf    > 0: self.cd_desf    -= 1

        # ── PINÇA: mover bloco ──────────────────────────────────────────────
        if g == "pinca":
            if self.arr:
                self.arr.x = cx
                self.arr.y = cy
            elif ant != "pinca":
                # Inicia arraste
                n = self._no_em(cx, cy)
                if n:
                    self.arr = n
                    for o in self.nos: o.sel = False
                    n.sel    = True
                    self.sel = n
        else:
            if self.arr:
                self._save()    # salva posição final ao soltar
            self.arr = None

        # ── 1 DEDO: mover cursor (só move, sem criar nada) ──────────────────
        # (o cursor já foi atualizado acima)

        # ── PUNHO: criar bloco ──────────────────────────────────────────────
        if g == "punho" and ant != "punho" and self.cd_criar == 0:
            self._criar(cx, cy)
            self.cd_criar = 45   # ~0.75s de cooldown

        # ── 2 DEDOS: conectar blocos ────────────────────────────────────────
        if g == "dois":
            if hov:
                if self.conn_src is None:
                    if ant != "dois":
                        self.conn_src = hov
                        self._info(f"Origem: {hov.txt[:16]}  →  aponte para o destino")
                elif self.conn_src is not hov:
                    self._link(self.conn_src, hov)
                    self.conn_src = None
        else:
            self.conn_src = None

        # ── 3 DEDOS: editar bloco com voz ───────────────────────────────────
        if g == "tres":
            if ant != "tres":
                # Acabou de entrar no gesto
                alvo = hov if hov else self.sel
                if alvo:
                    for n in self.nos: n.ed = False
                    alvo.ed = True
                    self._iniciar_voz(alvo)
                else:
                    self._info("Aponte para um bloco com 3 dedos")
        else:
            if ant == "tres":
                # Saiu do gesto → para de ouvir
                for n in self.nos: n.ed = False
                self._parar_voz()

        # ── 4 DEDOS: deletar bloco ──────────────────────────────────────────
        if g == "quatro" and ant != "quatro" and self.cd_deletar == 0:
            alvo = hov if hov else None
            if alvo:
                self._deletar(alvo)
                self.cd_deletar = 60
            else:
                self._info("Aponte para um bloco com 4 dedos")

        self.gesto_ant = g

    # ── HUD ──────────────────────────────────────────────────────────────────

    def _draw_hud(self):
        t = self.font_l.render("NORA CANVAS", True, ACCENT)
        self.screen.blit(t, (W // 2 - t.get_width() // 2, 12))
        sub = self.font_s.render(
            f"Blocos:{len(self.nos)}  Conexões:{len(self.cons)}  "
            f"[ESC sair]  [Mouse D=criar  E=selecionar/conectar]",
            True, GRAY)
        self.screen.blit(sub, (W // 2 - sub.get_width() // 2, 44))

        # Painel de ajuda
        info = [
            ("Pinça",      "Mover bloco"),
            ("1 dedo",     "Mover cursor"),
            ("2 dedos",    "Conectar blocos"),
            ("3 dedos",    "Editar (voz)"),
            ("4 dedos",    "Deletar bloco"),
            ("Punho",      "Criar bloco"),
        ]
        ps = pygame.Surface((210, 215), pygame.SRCALPHA)
        pygame.draw.rect(ps, (8, 12, 35, 200), (0, 0, 210, 215), border_radius=10)
        pygame.draw.rect(ps, (*ACCENT, 70), (0, 0, 210, 215), border_radius=10, width=1)
        ps.blit(self.font_s.render("GESTOS (1 MÃO)", True, ACCENT), (10, 8))
        for i, (g, d) in enumerate(info):
            y2 = 30 + i * 30
            ps.blit(self.font_s.render(g, True, ACCENT3), (10, y2))
            ps.blit(self.font_s.render(d, True, GRAY),    (10, y2 + 14))
        self.screen.blit(ps, (12, 68))

        # Gesto atual
        g   = self.gesto
        cor = (ACCENT3     if g == "pinca"  else
               ACCENT2     if g == "dois"   else
               WARN        if g == "quatro" else
               (255,200,0) if g == "tres"   else
               ACCENT3     if g == "punho"  else
               ACCENT      if g == "um"     else WHITE)
        self.screen.blit(self.font.render(f"Gesto: {g}", True, cor), (12, H - 38))

        # Indicador de gravação
        if self.gravando:
            r_col = (255, 60, 60) if self.tick % 30 < 15 else (180, 30, 30)
            pygame.draw.circle(self.screen, r_col, (W // 2, 16), 8)
            self.screen.blit(
                self.font_s.render("● GRAVANDO VOZ", True, (255, 80, 80)),
                (W // 2 + 14, 9))

        # Preview da câmera
        if self.cam_frame is not None:
            try:
                cs = pygame.surfarray.make_surface(self.cam_frame.swapaxes(0, 1))
                cs = pygame.transform.scale(cs, (CAM_W, CAM_H))
                self.screen.blit(cs, (W - CAM_W - 12, H - CAM_H - 12))
                bo = pygame.Surface((CAM_W + 4, CAM_H + 4), pygame.SRCALPHA)
                pygame.draw.rect(bo, (*ACCENT, 110), (0, 0, CAM_W + 4, CAM_H + 4),
                                 border_radius=8, width=2)
                self.screen.blit(bo, (W - CAM_W - 14, H - CAM_H - 14))
            except Exception:
                pass
        elif not self.cam_ok:
            t2 = self.font_s.render("Câmera: use o mouse", True, GRAY)
            self.screen.blit(t2, (W - t2.get_width() - 14, H - 30))

        # Mensagem de feedback
        if self.msg_t > 0:
            self.msg_t -= 1
            al = _clamp(self.msg_t * 6)
            ms = self.font.render(self.msg, True, ACCENT)
            mx2 = W // 2 - ms.get_width() // 2
            bs  = pygame.Surface((ms.get_width() + 24, ms.get_height() + 12),
                                  pygame.SRCALPHA)
            pygame.draw.rect(bs, (8, 12, 35, al), (0, 0, bs.get_width(), bs.get_height()),
                             border_radius=8)
            pygame.draw.rect(bs, (*ACCENT, al), (0, 0, bs.get_width(), bs.get_height()),
                             border_radius=8, width=1)
            bs.blit(ms, (12, 6))
            self.screen.blit(bs, (mx2 - 12, H - 78))

    def _draw_cursor(self):
        cx, cy = int(self.cur_s[0]), int(self.cur_s[1])
        g   = self.gesto
        col = (ACCENT3     if g == "pinca"  else
               ACCENT2     if g == "dois"   else
               WARN        if g == "quatro" else
               (255,200,0) if g == "tres"   else
               ACCENT3     if g == "punho"  else
               CURSOR_C)
        cs = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.circle(cs, (*col, 45),  (cx, cy), CURSOR_RAD + 6)
        pygame.draw.circle(cs, (*col, 170), (cx, cy), CURSOR_RAD, 2)
        pygame.draw.circle(cs, col,         (cx, cy), 4)
        for ddx, ddy in [(-22,0),(-8,0),(8,0),(22,0),(0,-22),(0,-8),(0,8),(0,22)]:
            pygame.draw.line(cs, (*col, 100), (cx, cy), (cx+ddx, cy+ddy), 1)
        self.screen.blit(cs, (0, 0))

    def _draw_fundo(self):
        self.screen.fill(BG)
        for sx, sy, b in self.stars:
            c = _clamp(int(35 * b + 18 * math.sin(self.tick * 0.02 + sx)))
            pygame.draw.circle(self.screen, (c, c, _clamp(c + 40)), (sx, sy), 1)
        grid = pygame.Surface((W, H), pygame.SRCALPHA)
        for gx in range(0, W, 60):
            a = _clamp(12 + int(6 * math.sin(self.tick * 0.01 + gx * 0.05)))
            pygame.draw.line(grid, (*ACCENT, a), (gx, 0), (gx, H))
        for gy in range(0, H, 60):
            a = _clamp(12 + int(6 * math.sin(self.tick * 0.01 + gy * 0.05)))
            pygame.draw.line(grid, (*ACCENT, a), (0, gy), (W, gy))
        self.screen.blit(grid, (0, 0))

    # ── Loop principal ───────────────────────────────────────────────────────

    def run(self):
        self.running = True
        try:
            while self.running:
                self.clock.tick(FPS)
                self.tick += 1

                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        self.running = False

                    elif ev.type == pygame.KEYDOWN:
                        if ev.key == pygame.K_ESCAPE:
                            self.running = False
                        elif ev.key == pygame.K_z and (
                                pygame.key.get_mods() & pygame.KMOD_CTRL):
                            self._undo()
                        else:
                            # Edição por teclado
                            ed = next((n for n in self.nos if n.ed), None)
                            if ed:
                                if ev.key == pygame.K_BACKSPACE:
                                    ed.txt = ed.txt[:-1]
                                elif ev.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                    ed.ed = False
                                    self._save()
                                elif ev.key == pygame.K_DELETE:
                                    ed.txt = ""
                                elif ev.unicode:
                                    ed.txt += ev.unicode
                                ed.resize()

                    elif ev.type == pygame.MOUSEBUTTONDOWN:
                        mx, my = ev.pos
                        self.cur_raw = [mx, my]
                        if ev.button == 3:
                            self._criar(mx, my)
                        elif ev.button == 1:
                            n = self._no_em(mx, my)
                            if n:
                                if self.sel and self.sel is not n:
                                    self._link(self.sel, n)
                                    self.sel.sel = False
                                    self.sel     = None
                                else:
                                    for o in self.nos: o.sel = False
                                    n.sel    = True
                                    self.sel = n
                                    self.arr = n
                            else:
                                for o in self.nos: o.sel = False
                                self.sel = None

                    elif ev.type == pygame.MOUSEBUTTONUP:
                        if self.arr:
                            self._save()
                        self.arr = None

                    elif ev.type == pygame.MOUSEMOTION:
                        mx, my = ev.pos
                        self.cur_raw = [mx, my]
                        if self.arr:
                            self.arr.x, self.arr.y = mx, my

                self._update_gesto()

                # Partículas
                self.parts = [p for p in self.parts if p.life > 0]
                for p in self.parts:
                    p.tick()

                # Renderização
                self._draw_fundo()
                for c in self.cons:
                    c.draw(self.screen, self.tick)
                for n in self.nos:
                    n.draw(self.screen, self.font, self.tick)
                for p in self.parts:
                    p.draw(self.screen)
                self._draw_cursor()
                self._draw_hud()
                pygame.display.flip()

        finally:
            # Limpeza garantida
            self._cam_running = False
            if self.gravando:
                self._parar_voz()
            if self.cap is not None:
                try:
                    self.cap.release()
                except Exception:
                    pass
            pygame.quit()


if __name__ == "__main__":
    App().run()