import time

from core.input_manager import (
    iniciar_listener,
    gesto_pressionado
)

iniciar_listener()

print("Aguardando tecla 1...")

while True:

    if gesto_pressionado():

        print("GESTO ATIVO")

        while gesto_pressionado():

            time.sleep(0.1)

    time.sleep(0.05)