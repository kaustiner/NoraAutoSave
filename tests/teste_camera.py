import cv2

camera = cv2.VideoCapture(0)

while True:

    ok, frame = camera.read()

    if not ok:
        break

    cv2.imshow(
        "NORA Camera",
        frame
    )

    tecla = cv2.waitKey(1)

    if tecla == 27:
        break

camera.release()
cv2.destroyAllWindows()