# 🖐 Hand Gesture Mouse Controller  

This project is a **mouse controller using hand gestures**, built with **OpenCV**, **MediaPipe**, and **Pynput**.  
With your laptop camera or webcam, you can move the cursor, perform left/right clicks, double-click, drag-and-drop, and scroll — all with simple hand gestures.  

---

## ✨ Features
- Smooth mouse movement with index finger  
- Left click & double click using index + thumb  
- Right click with pinky finger  
- Vertical & horizontal scrolling with four fingers  
- Drag & drop using pinch gesture (index + thumb held together)  
- Adjustable sensitivity & smoothing for better control  

---

## 🛠 Requirements
Python (>=3.9) and the following libraries are required:  

```txt
opencv-python==4.12.0.88
numpy==1.26.4
mediapipe==0.10.20
autopy==4.0.1
pynput==1.8.1
```
## 🚀 How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/matinabedi/HandyMouse.git
   cd HandyMouse
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
3. Run the program:
    ```bash
    python AIVirtualMouseProject.py
4. The camera will activate, and you can start controlling your mouse with gestures 

##  Supported Gestures
- 🖱 **Move Mouse** → Only index finger up, all others down  
-  **Left Click** → Tap index finger + thumb together  
-  **Double Click** → Tap index finger + thumb twice quickly (short interval)  
-  **Drag & Drop** → Pinch (index + thumb together) and hold  
-  **Right Click** → Only pinky finger up, all others down  
-  **Scroll** → Four fingers (except thumb) up  

## 📌 Notes
- You can adjust parameters like `sensitivity`, `smoothening`, and `frameR` in the code to improve accuracy and smoothness.  
- Good lighting improves MediaPipe’s detection accuracy.  
- On some systems, installing `autopy` may require additional tools (like Xcode Command Line Tools or Rust on macOS).  
    
