from datetime import datetime
from datetime import timedelta
import re


def interpretar(texto):

    texto = texto.lower().strip()

    hoje = datetime.now()

    # ------------------
    # RELATIVAS
    # ------------------

    if texto in ["hoje"]:
        return hoje

    if texto in ["amanha", "amanhã"]:
        return hoje + timedelta(days=1)

    if texto in [
        "depois de amanha",
        "depois de amanhã"
    ]:
        return hoje + timedelta(days=2)

    if texto == "semana que vem":
        return hoje + timedelta(days=7)

    if texto == "mes que vem":
        return hoje + timedelta(days=30)

    if texto == "mês que vem":
        return hoje + timedelta(days=30)

    # ------------------
    # DIAS DA SEMANA
    # ------------------

    dias_semana = {
        "segunda": 0,
        "terça": 1,
        "terca": 1,
        "quarta": 2,
        "quinta": 3,
        "sexta": 4,
        "sábado": 5,
        "sabado": 5,
        "domingo": 6
    }

    if texto in dias_semana:

        alvo = dias_semana[texto]

        dias = (
            alvo - hoje.weekday()
        ) % 7

        if dias == 0:
            dias = 7

        return hoje + timedelta(
            days=dias
        )

    # ------------------
    # DIA NUMÉRICO
    # ------------------

    match = re.search(
        r"dia\s+(\d+)",
        texto
    )

    if match:

        dia = int(
            match.group(1)
        )

        try:

            data = hoje.replace(
                day=dia
            )

            if data < hoje:

                if data.month == 12:

                    data = data.replace(
                        year=data.year + 1,
                        month=1
                    )

                else:

                    data = data.replace(
                        month=data.month + 1
                    )

            return data

        except:

            return None

    return None