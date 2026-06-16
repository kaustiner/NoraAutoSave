from core.reminder_manager import (
    carregar,
    salvar
)


def criar_lembrete(
    titulo,
    data=None,
    startup=False
):

    lembrete = {
        "titulo": titulo
    }

    if data:

        lembrete["data"] = (
            data.strftime(
                "%d/%m/%Y"
            )
        )

    elif startup:

        lembrete["startup"] = True

    lembretes = carregar()

    lembretes.append(
        lembrete
    )

    salvar(
        lembretes
    )

    return lembrete


def listar_lembretes():

    return carregar()


def apagar_todos():

    salvar([])


def apagar_indice(indice):

    lembretes = carregar()

    if indice < 0:

        return None

    if indice >= len(lembretes):

        return None

    removido = lembretes.pop(
        indice
    )

    salvar(
        lembretes
    )

    return removido


def total():

    return len(
        carregar()
    )


def total_startup():

    contador = 0

    for lembrete in carregar():

        if lembrete.get(
            "startup"
        ):

            contador += 1

    return contador