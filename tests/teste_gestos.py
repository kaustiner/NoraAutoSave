import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

camera = cv2.VideoCapture(0)

with mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as hands:

    while True:

        sucesso, frame = camera.read()

        if not sucesso:
            break

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        resultado = hands.process(
            frame_rgb
        )

        if resultado.multi_hand_landmarks:

            for mao in resultado.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    mao,
                    mp_hands.HAND_CONNECTIONS
                )

        cv2.imshow(
            "NORA - Gestos",
            frame
        )

        if cv2.waitKey(1) & 0xFF == 27:
            break

camera.release()
cv2.destroyAllWindows()