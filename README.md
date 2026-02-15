# AI Virtual Mouse with Advanced Gesture Recognition 🏆

A high-performance Human-Computer Interaction (HCI) system that allows you to control your computer using nothing but a webcam and AI. Built with **OpenCV**, **MediaPipe**, and **PyAutoGUI**.

![AI Demo](https://img.shields.io/badge/AI-Computer%20Vision-blue) ![Python](https://img.shields.io/badge/Python-3.13-green) ![macOS](https://img.shields.io/badge/OS-macOS%20Tahoe-black)

## 🚀 Key Features

- **Touchless Cursor Control**: Smooth, high-precision movement with M3-optimized tracking.
- **Advanced Gestures**:
  - 🖱️ **Pinch-to-Click**: Intuitive haptic-free clicking logic.
  - 📜 **Adaptive Scrolling**: Vertical hand-tracking for natural scrolling.
  - 🔊 **Dynamic Volume Control**: Gesture-based scaling for OS-level volume.
  - 🌐 **Browser Navigation**: 5-finger swipe for Back/Forward navigation.
  - 📑 **App Switcher**: One-handed Command+Tab automation.
  - 🎨 **Whiteboard Mode**: Draw on your screen using AI hand mesh.
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

## 🛠️ Tech Stack

- **Computer Vision**: OpenCV
- **Machine Learning**: MediaPipe Tasks API (Hand Landmarker)
- **Automation**: PyAutoGUI, Rubicon-ObjC
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

## 📈 Optimization for macOS
This project includes specific optimizations for the **macOS SDK (Tahoe)** and **Apple Silicon (M1/M2/M3)**, including asynchronous frame processing to ensure 0% lag in gesture recognition.
