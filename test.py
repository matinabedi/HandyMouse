import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
from pynput.mouse import Button, Controller


def smooth_scroll(dy, steps=10, delay=0.01):
    scroll_amount = dy / steps
    for _ in range(steps):
        mouse.scroll(0, int(2 * scroll_amount))
        time.sleep(delay)


cap = cv2.VideoCapture(0)
detector = htm.handDetector(maxHands=1)

wCam, hCam = 640, 480
wScr, hScr = autopy.screen.size()
frameR = 100
smoothening = 7

cap.set(3, wCam)
cap.set(4, hCam)

click = True
scroll = False
plocX, plocY = 0, 0
clocX, clocY = 0, 0
prev_y = 0
mouse = Controller()

firstClick = 0

drag_active = False
drag_start_time = 0
drag_debounce = 0.15
pinch_start_detected = False

while True:
    pTime = time.time()

    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bBox = detector.findPosition(img)

    if len(lmList) > 0:
        x1, y1 = lmList[8][1:]  # index tip
        x2, y2 = lmList[12][1:]  # middle tip

        fingers = detector.fingersUp()
        cv2.rectangle(
            img,
            (frameR, frameR),
            (wCam - frameR, hCam - frameR),
            (255, 0, 255),
            2,
        )

        # Mouse movement (only index finger up)
        if fingers[1] == 1 and fingers[2] == 0:
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            mouse.position = (wScr - clocX, clocY)
            plocX, plocY = clocX, clocY

            scroll = False

        # Scroll (all fingers up)
        if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            if not scroll:
                prev_y = y1
                scroll = True

            dy = prev_y - y1
            if abs(dy) > 3:
                smooth_scroll(dy, steps=15, delay=0.005)
            prev_y = y1

        # ---- Click / Double Click (Thumb + Index) ----
        length_thumb_index, img, _ = detector.findDistance(8, 4, img)
        click_threshold = 25

        if length_thumb_index < click_threshold:
            if click:
                if firstClick == 0:
                    firstClick = time.time()
                    mouse.click(Button.left, 1)
                else:
                    if time.time() - firstClick < 2:
                        mouse.click(Button.left, 2)
                    firstClick = 0
                click = False
        else:
            click = True

        # ---- Drag with pinch (Thumb + Index) ----
        pinch_threshold = 25
        if length_thumb_index < pinch_threshold:
            if not pinch_start_detected:
                pinch_start_detected = True
                pinch_time = time.time()
            else:
                if (time.time() - pinch_time) > drag_debounce and not drag_active:
                    drag_active = True
                    mouse.press(Button.left)

            if drag_active:
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                x_mouse = np.clip(clocX, 0, wScr - 1)
                y_mouse = np.clip(clocY, 0, hScr - 1)
                mouse.position = (wScr - x_mouse, y_mouse)
                plocX, plocY = clocX, clocY
        else:
            pinch_start_detected = False
            if drag_active:
                mouse.release(Button.left)
                drag_active = False

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    cv2.putText(
        img,
        str(int(fps)),
        (100, 100),
        cv2.FONT_HERSHEY_COMPLEX,
        3,
        (255, 0, 0),
        3,
    )

    cv2.imshow("image", img)
    cv2.waitKey(1)