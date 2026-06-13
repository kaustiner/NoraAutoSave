import random
from datetime import datetime

NOME = "Data Hora Comprimento"

FRASES_MANHA = [
    "Bom dia, Kaio. Dormiu bem?",
    "Bom dia. Tudo pronto por aqui.",
    "Olá. Pronta para mais um dia.",
    "Que seu dia seja produtivo."
]

FRASES_TARDE = [
    "Boa tarde, Kaio.",
    "Olá. Como está indo seu dia?",
    "Pronta para ajudar.",
    "Tudo certo por aqui."
]

FRASES_NOITE = [
    "Boa noite, Kaio.",
    "Trabalhando até tarde hoje?",
    "Pronta para receber comandos.",
    "Bem-vindo de volta."
]


def executar():

    agora = datetime.now()

    dias = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo"
    ]

    if agora.hour < 12:
        frase = random.choice(FRASES_MANHA)

    elif agora.hour < 18:
        frase = random.choice(FRASES_TARDE)

    else:
        frase = random.choice(FRASES_NOITE)

    print()
    print(f"[NORA] {frase}")
    print(
        f"[NORA] Hoje é {dias[agora.weekday()]}, "
        f"{agora.strftime('%d/%m/%Y')}."
    )
    print(
        f"[NORA] Agora são "
        f"{agora.strftime('%H:%M')}."
    )
    print()