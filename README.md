<div align="center">

<!-- ANIMATED HEADER BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,100:1e1b4b&height=240&section=header&text=Gesture%20Volume%20Control&fontSize=48&fontAlignY=36&animation=twinkling&desc=Precision%20Audio%20Management%20via%20Computer%20Vision&descSize=18&descAlignY=62&stroke=6366f1&strokeWidth=1" width="100%" alt="Gesture Volume Control Header Banner" />

<br/>

<!-- BADGES -->
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+"/></a>
<a href="https://opencv.org/"><img src="https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV"/></a>
<a href="https://developers.google.com/mediapipe"><img src="https://img.shields.io/badge/MediaPipe-0.10%2B-00C7B7?style=for-the-badge&logo=google&logoColor=white" alt="MediaPipe"/></a>
<a href="https://github.com/AndreMiras/pycaw"><img src="https://img.shields.io/badge/Pycaw-Audio_API-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Pycaw"/></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-43A047?style=for-the-badge&logo=open-source-initiative&logoColor=white" alt="License MIT"/></a>

<br/><br/>

> **A touchless, real-time volume controller mapping computer vision hand gestures directly to Windows system audio.**  
> Built with MediaPipe and Pycaw, featuring exponential signal smoothing to eliminate camera jitter and an integrated gestural lock switch.

</div>

---

## 🎮 Interactive Demo

<div align="center">

<!-- Replace demo.gif with your actual recorded GIF/video asset -->
<img src="./demo.gif" alt="Gesture Volume Control Demonstration" width="80%" style="border-radius: 12px; border: 1px solid #30363d; box-shadow: 0 12px 32px rgba(0,0,0,0.35);">

<p align="center">
  <sub><em>Demonstrating live pinch-to-volume adjustments, real-time status HUD, and pinky engagement toggling.</em></sub>
</p>

</div>

---

## ⚡ Technical Highlights

<table>
  <tr>
    <td width="50%">
      <h3>🎯 Precision Pinch Tracking</h3>
      <p>Computes the continuous 2D/3D Euclidean distance between <code>Thumb (Landmark 4)</code> and <code>Index (Landmark 8)</code>, mapping physical spatial gap directly to normalized audio levels (0% to 100%).</p>
    </td>
    <td width="50%">
      <h3>📈 Signal Smoothing (EMA)</h3>
      <p>Applies an <strong>Exponential Moving Average (EMA)</strong> filter to the calculated output signal, filtering out frame-to-frame webcam noise and hand tremors for butter-smooth adjustments.</p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <h3>🔒 Gestural Lock Switch</h3>
      <p>Continuously monitors <code>Pinky tip (Landmark 20)</code> against its <code>MCP joint (Landmark 17)</code>. The control loop stays locked until deliberately engaged, preventing accidental volume triggers.</p>
    </td>
    <td width="50%">
      <h3>🔊 Native Audio Integration</h3>
      <p>Direct low-latency hooks into the <strong>Windows Core Audio API</strong> via <code>Pycaw</code> and <code>comtypes</code>. Adjusts master audio natively in the background without disruptive OS popups.</p>
    </td>
  </tr>
</table>

---

## ✋ Gesture Controls Guide

```text
               ┌─────────────────────────────────────────────────────────┐
               │                  CONTROL STATE PIPELINE                 │
               └─────────────────────────────────────────────────────────┘

     [UNLOCKED STATE]                  [VOLUME PINCH]                  [LOCKED STATE]
        
       🖐️ Pinky Raised                🤌 Pinch / Spread              ✊ Pinky Lowered
    (Tip higher than MCP)            (Thumb ↔ Index Distance)           (Hand Closed)
              │                                 │                             │
              ▼                                 ▼                             ▼
    Activates Volume Switch            Scales Audio 0% ➔ 100%       Locks Current Volume Level