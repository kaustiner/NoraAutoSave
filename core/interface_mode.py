import json


ARQUIVO = "config/interface.json"


def obter_modo():

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as f:

            dados = json.load(f)

            return dados.get(
                "modo",
                "ambos"
            )

    except:

        return "ambos"