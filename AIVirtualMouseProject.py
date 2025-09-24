import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy
import pyautogui
from pynput.mouse import Button, Controller



def smooth_scroll(dy, steps=10, delay=0.01):
    scroll_amount = dy / steps
    for _ in range(steps):
        mouse.scroll(0, int(scroll_amount))
        time.sleep(delay)




cap = cv2.VideoCapture(0)
detector= htm.handDetector(maxHands=1)

wCam, hCam = 640, 480
wScr , hScr = autopy.screen.size()
frameR = 100
smoothening = 7
scroll_speed = 5  


cap.set(3, wCam)
cap.set(4, hCam)


click = True
scroll = False
plocX , plocY = 0 ,0
clocX , clocY = 0 , 0
prev_y = 0
mouse = Controller()


firstClick , secondClick = 0,0

while True:
    pTime = time.time()
    
    success , img = cap.read()
    img = detector.findHands(img)
    lmList , bBox = detector.findPosition(img)
     
     
    if len(lmList)> 0 :
         x1 , y1 = lmList[8][1:]
         x2 , y2 = lmList[12][1:]
         
         
         fingers = detector.fingersUp()
         cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
            (255, 0, 255), 2)
         
         if fingers[1] == 1 and fingers[2]==0:
             x3 = np.interp(x1 , (frameR , wCam-frameR) , (0, wScr)) 
             y3 = np.interp(y1 , (frameR , hCam-frameR) , (0, hScr)) 
             
             clocX = plocX + (x3 - plocX) / smoothening
             clocY = plocY + (y3 - plocY) / smoothening
             
            
             mouse.position = (wScr-clocX, clocY)
             plocX, plocY = clocX, clocY
             
             scroll= False
          
          
         if fingers[1] == 1 and fingers[2]==1 and fingers[3]==1 and fingers[4]==1: 
             
            if not scroll:
                prev_y = y1
                scroll = True
             
                
            dy = prev_y - y1   # اختلاف حرکت دست
    
            if abs(dy) > 4:  # فقط وقتی حرکت قابل توجه باشه
                smooth_scroll(dy, steps=15, delay=0.005)
            prev_y = y1

          
             
         elif fingers[1] == 1 and fingers[2]==1:
            scroll = False
            length , img , _ =  detector.findDistance(8,12,img)
            if length <25:
                if click==True:
                    if firstClick == 0:
                        firstClick = time.time()
                        mouse.click(Button.left, 1)
                    elif firstClick != 0:
                        if time.time()-firstClick <2:
                            mouse.click(Button.left, 2)
                        firstClick =0 
                    click = False
            else:
                click = True
            
                

               
                
        
    
    
    cTime = time.time()
    fps =  1/ (cTime-pTime)
    cv2.putText(img , str(int(fps)) , (100 ,100)  , 3, 3 ,(255,0,0) , cv2.FONT_HERSHEY_COMPLEX  )
    
    
    
    
    cv2.imshow("image" , img)
    cv2.waitKey(1)
    