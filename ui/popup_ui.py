import os
import sys
import math
import customtkinter as ctk

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.input_manager import (
    alt_pressionado,
    gesto_pressionado,
    iniciar_listener,
    ativar_voz,
    desativar_voz
)

from ui.ui_manager import (
    get_status,
    get_mensagem
)

ctk.set_appearance_mode("dark")


def iniciar_interface():

    app = ctk.CTk()

    def fechar():
        os._exit(0)

    app.protocol(
        "WM_DELETE_WINDOW",
        fechar
    )

    app.title("NORA")

    largura = 420
    altura = 580

    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()

    x = largura_tela - largura - 20
    y = altura_tela - altura - 60

    app.geometry(
        f"{largura}x{altura}+{x}+{y}"
    )

    app.resizable(False, False)

    fundo = "#242424"

    app.configure(
        fg_color=fundo
    )

    titulo = ctk.CTkLabel(
        app,
        text="NORA",
        font=("Segoe UI", 24, "bold"),
        text_color="#00E5FF"
    )

    titulo.pack(
        pady=(15, 5)
    )

    canvas = ctk.CTkCanvas(
        app,
        width=320,
        height=320,
        bg=fundo,
        highlightthickness=0
    )

    canvas.pack()

    status = ctk.CTkLabel(
        app,
        text="Pronta.",
        font=("Segoe UI", 14),
        text_color="#00E5FF"
    )

    status.pack(
        pady=(10, 4)
    )

    mensagem = ctk.CTkLabel(
        app,
        text="[NORA]\nAguardando comando...",
        font=("Segoe UI", 13),
        justify="center",
        wraplength=360
    )

    mensagem.pack(
        pady=(0, 10)
    )

    centro_x = 160
    centro_y = 160

    angulo = 0
    pulso = 0

    def mouse_down(event):

        ativar_voz()

    def mouse_up(event):

        desativar_voz()

    def obter_visual():

        if gesto_pressionado():

            return {
                "cor": "#B347FF",
                "cor2": "#E0A6FF",
                "vel": 3.75,
                "nucleo": 30,
                "brilho": 1.6
            }

        if alt_pressionado():

            return {
                "cor": "#00FFFF",
                "cor2": "#B7FFFF",
                "vel": 3.75,
                "nucleo": 30,
                "brilho": 1.8
            }

        return {
            "cor": "#00E5FF",
            "cor2": "#B7FFFF",
            "vel": 1.5,
            "nucleo": 22,
            "brilho": 1.0
        }

    def desenhar():

        nonlocal angulo
        nonlocal pulso

        visual = obter_visual()

        cor = visual["cor"]
        cor2 = visual["cor2"]

        status.configure(
            text=get_status()
        )

        mensagem.configure(
            text=get_mensagem()
        )

        canvas.delete("all")

        angulo += visual["vel"]
        pulso += 0.05

        brilho = (
            math.sin(pulso)
            * 4
            * visual["brilho"]
        )

        raio_nucleo = (
            visual["nucleo"]
            + brilho
        )

        for i in range(20):

            a = math.radians(i * 18)

            x = centro_x + math.cos(a) * 145
            y = centro_y + math.sin(a) * 145

            canvas.create_oval(
                x - 1,
                y - 1,
                x + 1,
                y + 1,
                fill="#35555A",
                outline=""
            )

        for i in range(8):

            r = raio_nucleo + (i * 5)

            canvas.create_oval(
                centro_x-r,
                centro_y-r,
                centro_x+r,
                centro_y+r,
                outline=cor,
                width=1
            )

        canvas.create_oval(
            centro_x-raio_nucleo,
            centro_y-raio_nucleo,
            centro_x+raio_nucleo,
            centro_y+raio_nucleo,
            fill=cor,
            outline="",
            tags="nucleo"
        )

        canvas.create_oval(
            28, 28,
            292, 292,
            outline="#0E3940",
            width=2
        )

        canvas.create_oval(
            52, 52,
            268, 268,
            outline="#0B5865",
            width=2
        )

        canvas.create_oval(
            78, 78,
            242, 242,
            outline=cor,
            width=1
        )

        canvas.create_oval(
            102, 102,
            218, 218,
            outline=cor2,
            width=1
        )

        for i in range(48):

            a = math.radians(
                i * 7.5 + angulo
            )

            x1 = centro_x + math.cos(a) * 126
            y1 = centro_y + math.sin(a) * 126

            x2 = centro_x + math.cos(a) * 136
            y2 = centro_y + math.sin(a) * 136

            canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="#0A5C69",
                width=2
            )

        for offset in range(0, 360, 30):

            a = math.radians(
                angulo + offset
            )

            x1 = centro_x + math.cos(a) * 88
            y1 = centro_y + math.sin(a) * 88

            x2 = centro_x + math.cos(a) * 122
            y2 = centro_y + math.sin(a) * 122

            canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=cor,
                width=4
            )

        for offset in range(15, 360, 30):

            a = math.radians(
                -angulo * 0.7 + offset
            )

            x1 = centro_x + math.cos(a) * 58
            y1 = centro_y + math.sin(a) * 58

            x2 = centro_x + math.cos(a) * 82
            y2 = centro_y + math.sin(a) * 82

            canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=cor2,
                width=3
            )

        for i in range(8):

            a = math.radians(
                angulo + (i * 45)
            )

            x = centro_x + math.cos(a) * 110
            y = centro_y + math.sin(a) * 110

            canvas.create_oval(
                x - 2,
                y - 2,
                x + 2,
                y + 2,
                fill=cor,
                outline=""
            )

        app.after(
            16,
            desenhar
        )

    desenhar()

    desenhar()

    canvas.bind(
        "<ButtonPress-1>",
        mouse_down
    )

    canvas.bind(
        "<ButtonRelease-1>",
        mouse_up
    )

    app.mainloop()


if __name__ == "__main__":

    iniciar_listener()

    iniciar_interface()