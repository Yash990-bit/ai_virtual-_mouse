# AI Virtual Mouse with Advanced Gesture Recognition 🏆

A high-performance Human-Computer Interaction (HCI) system that allows you to control your computer using nothing but a webcam and AI. Built with **OpenCV**, **MediaPipe**, and **PyAutoGUI**.

![AI Demo](https://img.shields.io/badge/AI-Computer%20Vision-blue) ![Python](https://img.shields.io/badge/Python-3.13-green) ![macOS](https://img.shields.io/badge/OS-macOS%20Tahoe-black)

## 🚀 Key Features

- **Touchless Cursor Control**: Smooth, high-precision movement with M3-optimized tracking.
- **Elite Control Set**:
  - 🎬 **Media Center**:
    - **Play/Pause**: Close hand into a Fist.
    - **Mute**: Make an "OK" gesture (Index + Thumb touch).
  - 🖱️ **Advanced Interactions**:
    - **App Switcher**: Thumb ONLY UP.
    - **Browser Nav (Swipe)**: All 5 fingers UP + Horizontal swipe.
    - **Whiteboard Mode**: Pinky ONLY UP to toggle.
- **Real-Time Diagnostics**: On-screen Finger Dashboard (T,I,M,R,P) and Performance Monitor (CPU/RAM/FPS).

## 🎮 Hand Gesture Guide

| Gesture | Action |
| :--- | :--- |
| **Index UP** | Move Cursor |
| **Index + Middle Pinch** | Left Click |
| **3 Fingers UP** | Right Click |
| **4 Fingers UP** | Scroll Mode (Hand Up/Down) |
| **5 Fingers UP + Swipe** | Browser Back/Forward |
| **Thumb ONLY UP** | App Switcher (Cmd+Tab) |
| **Thumb + Index UP** | Volume Control (Vertical) |
| **Thumb + Pinky UP** | Save Screenshot to Desktop |
| **Pinky ONLY UP** | **Toggle Whiteboard Mode ON/OFF** |
| **Fist (0 fingers)** | **Play/Pause Media** |
| **OK Sign (Thumb+Index)**| **Mute/Unmute** |

## 🛠️ Tech Stack

- **Computer Vision**: OpenCV
- **Machine Learning**: MediaPipe Tasks API (Hand Landmarker)
- **Automation**: PyAutoGUI
- **UI**: Custom Dashboard Overlay (Native OpenCV)

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Yash990-bit/ai_virtual-_mouse.git
   cd ai_virtual-_mouse
   ```

2. **Setup Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install opencv-python mediapipe pyautogui customtkinter screeninfo psutil
   ```

4. **Run the App**:
   ```bash
   python3 main.py
   ```
