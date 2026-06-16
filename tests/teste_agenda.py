from core.agenda_manager import (
    criar_lembrete,
    listar_lembretes
)

criar_lembrete(
    "teste agenda",
    startup=True
)

print(
    listar_lembretes()
)