<div align="center">

# Gesture Volume Control
**Precision Audio Management via Computer Vision**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red.svg?logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-orange.svg?logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Pycaw](https://img.shields.io/badge/Pycaw-Audio-yellow.svg)](https://github.com/AndreMiras/pycaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A real-time, touchless volume controller that maps hand gestures directly to Windows system audio levels. Built on top of MediaPipe and Pycaw, it delivers buttery-smooth volume transitions by tracking precise finger distances and applying advanced signal smoothing to mitigate camera jitter.

</div>

<br>

## 🎮 Interactive Demo

<!-- PLACEHOLDER: Replace demo.png with an actual GIF/Screenshot of the gesture control in action -->
<div align="center">
  <img src="./demo.png" alt="Gesture Volume Control Demonstration" width="700" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
  <p><em>Demonstrating live pinch-to-volume adjustments and engagement toggling.</em></p>
</div>

---

## 🏗️ Key Architectural Features

- **Precision Pinch Tracking:** Calculates the real-time Euclidean distance between Thumb (Landmark 4) and Index (Landmark 8) to establish a dynamic volume interpolation curve.
- **Signal Smoothing:** Employs an Exponential Moving Average (EMA) filter on the output volume signal to eliminate frame-by-frame jitter and provide a premium, smooth audio adjustment experience.
- **Gestural Lock Switch:** Incorporates an engagement toggle by continuously monitoring the Pinky tip (Landmark 20) relative to its MCP joint (Landmark 17), preventing accidental system volume modifications when not actively controlling.
- **Background Windows Core Audio Integration:** Directly hooks into the Windows Core Audio API via Pycaw, executing volume changes natively and instantaneously without triggering disruptive OS popups.

---

## 🚀 Getting Started & Installation

### Prerequisites
- Python 3.8 or higher
- Windows Operating System (Required for Pycaw integration)
- A working webcam

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/Hasara-269/gesture-volume-control.git
cd gesture-volume-control

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux (if testing UI without Pycaw):
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Launch the application
python main.py
```

---

## ✋ Gesture Controls Guide

| Action | Gesture | System Response |
| :--- | :--- | :--- |
| **Engage Control** | Raise pinky finger (Tip higher than MCP joint) | Unlocks the volume modification state. The visualizer will turn active. |
| **Adjust Volume** | Pinch/Spread Thumb and Index fingers | Dynamically scales system volume relative to finger distance. |
| **Lock Control** | Lower pinky finger (Close hand / fist) | Locks the volume modification state. Hand movements will no longer affect audio. |
| **Exit App** | Press `q` on the keyboard | Closes the webcam feed and securely terminates the process. |

---

## 🧰 Tech Stack & Dependencies

- **[OpenCV (`opencv-python`)](https://opencv.org/):** Core library for capturing webcam feeds and rendering the real-time feedback UI.
- **[MediaPipe (`mediapipe`)](https://developers.google.com/mediapipe):** High-performance Google ML framework utilized for complex 21-point hand landmark detection.
- **[NumPy (`numpy`)](https://numpy.org/):** Handles mathematical interpolations and array-based Euclidean distance calculations.
- **[Pycaw (`pycaw`)](https://github.com/AndreMiras/pycaw) & `comtypes`:** Powers the native integration with the Windows Core Audio API.

---

## 📂 Project Structure

```text
gesture-volume-control/
│
├── .gitignore          # Git exclusion rules
├── demo.png            # Placeholder for the application demonstration
├── main.py             # Core application entry point and logic
├── README.md           # Project documentation (You are here)
└── requirements.txt    # Frozen dependency specifications
```
