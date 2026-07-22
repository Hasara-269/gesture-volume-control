<div align="center">

<!-- ANIMATED / DYNAMIC HEADER BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=auto&height=220&section=header&text=Gesture%20Volume%20Control&fontSize=50&fontAlignY=35&animation=twinkling&desc=Precision%20Audio%20Management%20via%20Computer%20Vision&descSize=18&descAlignY=60" width="100%" alt="Header Banner" />

<br/>

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-00C7B7?style=for-the-badge&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Pycaw](https://img.shields.io/badge/Pycaw-Windows_Audio-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/AndreMiras/pycaw)
[![License: MIT](https://img.shields.io/badge/License-MIT-43A047?style=for-the-badge&logo=open-source-initiative&logoColor=white)](https://opensource.org/licenses/MIT)

<br/>

A real-time, touchless volume controller that maps hand gestures directly to Windows system audio levels. Built on top of **MediaPipe** and **Pycaw**, it delivers buttery-smooth volume transitions by tracking precise finger distances and applying advanced signal smoothing to mitigate camera jitter.

</div>

---

## 🎮 Interactive Demo

<div align="center">
  <!-- Replace demo.gif with your recorded GIF or video clip of the app in action -->
  <img src="./demo.gif" alt="Gesture Volume Control Demonstration" width="750" style="border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);">
  <p><sub><em>Live pinch-to-volume adjustments featuring engagement toggling and real-time visual feedback.</em></sub></p>
</div>

---

## 🏗️ Key Architectural Features

| Feature | Description |
| :--- | :--- |
| 🎯 **Precision Pinch Tracking** | Calculates the real-time Euclidean distance between **Thumb (Landmark 4)** and **Index (Landmark 8)** to establish a dynamic volume interpolation curve. |
| 📈 **Signal Smoothing Filter** | Employs an **Exponential Moving Average (EMA)** filter on the output signal to eliminate frame-by-frame jitter, offering a premium, fluid audio adjustment experience. |
| 🔒 **Gestural Lock Switch** | Features a dedicated engagement toggle by monitoring the **Pinky tip (Landmark 20)** relative to its **MCP joint (Landmark 17)**, preventing accidental volume triggers. |
| ⚡ **Core Audio API Integration** | Direct low-latency hooks into the Windows Core Audio API via **Pycaw**, updating system levels natively without triggering intrusive OS overlays. |

---

## ✋ Gesture Controls Guide

> **Note:** Raise your pinky to unlock volume modification. Lowering your pinky locks the volume at its current setting.

```text
    [UNLOCKED STATE]                 [VOLUME PINCH]                 [LOCKED STATE]
       
      🖐️ Pinky Raised               🤌 Pinch / Spread             ✊ Pinky Lowered
   (Tip higher than MCP)           (Thumb ↔ Index Distance)          (Hand Closed)
             │                                 │                            │
             ▼                                 ▼                            ▼
   Activates Volume Switch           Scales Audio 0% ➔ 100%       Locks Current Volume Level