import time

from core.input_manager import (
    iniciar_listener,
    alt_pressionado
)

print("Listener iniciado")

iniciar_listener()

while True:

    if alt_pressionado():

        print("ALT DETECTADO")

        while alt_pressionado():
            time.sleep(0.1)

    time.sleep(0.05)