from core.date_parser import interpretar


GATILHOS = [
    "não me deixa esquecer",
    "nao me deixa esquecer",
    "preciso lembrar",
    "me lembre",
    "me lembra",
    "lembra de"
]


DATAS = [
    "depois de amanhã",
    "depois de amanha",
    "amanhã",
    "amanha",
    "hoje",
    "segunda",
    "terça",
    "terca",
    "quarta",
    "quinta",
    "sexta",
    "sábado",
    "sabado",
    "domingo",
    "semana que vem",
    "mês que vem",
    "mes que vem"
]


def extrair(texto):

    texto = texto.strip()

    texto_lower = texto.lower()

    encontrou = False

    for gatilho in GATILHOS:

        if texto_lower.startswith(gatilho):

            texto = texto[
                len(gatilho):
            ].strip()

            texto_lower = texto.lower()

            encontrou = True

            break

    if not encontrou:
        return None

    data = None

    for termo in DATAS:

        if texto_lower.endswith(termo):

            data = interpretar(
                termo
            )

            texto = texto[
                :-len(termo)
            ].strip()

            break

    while texto.lower().startswith("de "):

        texto = texto[3:].strip()

    while texto.lower().startswith("que "):

        texto = texto[5:].strip()

    while texto.lower().startswith(
        "eu tenho que "
    ):

        texto = texto[13:].strip()

    while texto.lower().startswith(
        "tenho que "
    ):

        texto = texto[10:].strip()

    while texto.lower().startswith(
        "eu preciso "
    ):

        texto = texto[11:].strip()

    while texto.lower().startswith(
        "preciso "
    ):

        texto = texto[8:].strip()

    if not texto:
        return None

    return {
        "titulo": texto,
        "data": data
    }