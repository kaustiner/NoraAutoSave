from core.gesture_config_manager import (
    vincular
)

gesto = input(
    "Nome do gesto: "
)

plugin = input(
    "Plugin: "
)

vincular(
    gesto,
    plugin
)

print(
    "\n[NORA] Vinculado com sucesso."
)