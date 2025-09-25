import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
from pynput.mouse import Button, Controller

# -------------------- Settings --------------------
wCam, hCam = 640, 480
wScr, hScr = autopy.screen.size()
frameR = 100
smoothening = 7
sensitivity = 1.5
click_threshold = 25
pinch_threshold = 25
drag_debounce = 0.15

# -------------------- State Variables --------------------
plocX, plocY = 0, 0
clocX, clocY = 0, 0
prev_x, prev_y = 0, 0
click = True
scroll = False
rightClick = True
firstClick = 0
drag_active = False
pinch_start_detected = False
pinch_time = 0

# -------------------- Tools --------------------
mouse = Controller()
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)


# -------------------- Functions --------------------
def get_mouse_coords(x1, y1, plocX, plocY):
    """Calculate smoothed mouse coordinates"""
    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr)) * sensitivity
    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr)) * sensitivity
    x3, y3 = np.clip(x3, 0, wScr - 1), np.clip(y3, 0, hScr - 1)

    clocX = plocX + (x3 - plocX) / smoothening
    clocY = plocY + (y3 - plocY) / smoothening

    return clocX, clocY


def move_mouse(x1, y1):
    global plocX, plocY
    clocX, clocY = get_mouse_coords(x1, y1, plocX, plocY)
    mouse.position = (wScr - clocX, clocY)
    plocX, plocY = clocX, clocY


def scroll_mouse(x1, y1):
    global prev_x, prev_y, scroll
    clocX, clocY = get_mouse_coords(x1, y1, prev_x, prev_y)

    if not scroll:
        prev_x, prev_y = clocX, clocY
        scroll = True

    dx, dy = prev_x - clocX, prev_y - clocY

    if abs(dy) > 15:
        dySign, dyAbs = np.sign(dy), abs(dy)
        dy = (0.0006 * dyAbs**2 - 0.015 * dyAbs + 1.5) * dySign * 1.5
    else:
        dy = 0

    if abs(dx) > 15:
        dxSign, dxAbs = np.sign(dx), abs(dx)
        dx = (0.0006 * dxAbs**2 - 0.015 * dxAbs + 1.5) * dxSign * 1.5
    else:
        dx = 0

    if dx != 0 or dy != 0:
        mouse.scroll(dx, dy)

    prev_x, prev_y = clocX, clocY


def handle_clicks(fingers, length_thumb_index):
    global click, rightClick, firstClick

    # Right click
    if fingers == [0, 0, 0, 0, 1]:
        if rightClick:
            mouse.click(Button.right, 1)
            rightClick = False
    else:
        rightClick = True

    # Left click & double click
    if fingers == [1, 1, 0, 0, 0]:
        if length_thumb_index < click_threshold:
            if click:
                if firstClick == 0:
                    firstClick = time.time()
                    mouse.click(Button.left, 1)
                    print("one click")
                else:
                    if time.time() - firstClick < 1:
                        mouse.click(Button.left, 2)
                        print("double click")
                    firstClick = 0
                click = False
        else:
            click = True


def handle_drag(x1, y1, length_thumb_index):
    global drag_active, pinch_start_detected, pinch_time, plocX, plocY

    if length_thumb_index < pinch_threshold:
        if not pinch_start_detected:
            pinch_start_detected = True
            pinch_time = time.time()
        else:
            if (time.time() - pinch_time) > drag_debounce and not drag_active:
                drag_active = True
                mouse.press(Button.left)
                print("hold mouse")

        if drag_active:
            clocX, clocY = get_mouse_coords(x1, y1, plocX, plocY)
            mouse.position = (wScr - clocX, clocY)
            plocX, plocY = clocX, clocY
    else:
        pinch_start_detected = False
        if drag_active:
            mouse.release(Button.left)
            print("release mouse")
            drag_active = False


# -------------------- Main Loop --------------------
while True:
    pTime = time.time()
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bBox = detector.findPosition(img)

    if len(lmList) > 0:
        x1, y1 = lmList[8][1], lmList[8][2]  # index finger tip
        fingers = detector.fingersUp()
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        if fingers[1] == 1 and all(f == 0 for i, f in enumerate(fingers) if i != 1):
            move_mouse(x1, y1)
            scroll = False

        if fingers[1:] == [1, 1, 1, 1]:
            scroll_mouse(x1, y1)

        length_thumb_index, img, _ = detector.findDistance(8, 4, img)
        handle_clicks(fingers, length_thumb_index)
        handle_drag(x1, y1, length_thumb_index)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    cv2.putText(img, str(int(fps)), (100, 100), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0), 3)

    cv2.imshow("image", img)
    cv2.waitKey(1)
