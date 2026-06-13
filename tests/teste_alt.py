import time

from core.input_manager import (
    iniciar_listener,
    alt_pressionado
)

print(
    "Segure ALT..."
)

iniciar_listener()

while True:

    if alt_pressionado():

        print(
            "ALT pressionado"
        )

        time.sleep(0.5)