# 🖐️ Gesture Volume Controller

> A real-time computer vision application built with **Python**, **OpenCV**, and **MediaPipe** that tracks hand gestures via webcam and dynamically adjusts system audio levels using the **PyCaw** Windows audio API.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-00A98F)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖐️ **Real-time Hand Tracking** | MediaPipe Hands detects thumb tip & index finger tip with high confidence |
| 🔊 **Smooth Volume Control** | Pinch distance mapped to system volume via PyCaw (no popup OSD) |
| 📊 **Live Volume Bar** | Animated vertical bar overlay with tick marks and percentage readout |
| 🎯 **EMA Smoothing** | Exponential moving average eliminates jitter for buttery-smooth control |
| 🟢 **Visual Extremes Feedback** | Pulsing circle + green line when volume hits 0 % (mute) or 100 % (max) |
| ⚡ **FPS Counter** | Live frames-per-second overlay to monitor performance |
| 🔄 **Mirror View** | Selfie-style horizontal flip for natural interaction |
| 🛡️ **Defensive Coding** | Graceful fallback to PyAutoGUI, frame-drop detection, clean shutdown |

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Webcam Feed │────▶│   OpenCV     │────▶│  MediaPipe Hands  │
│  640 × 480   │     │  Flip + BGR  │     │  Landmark 4 & 8   │
└──────────────┘     └──────────────┘     └────────┬─────────┘
                                                   │
                                          Euclidean Distance
                                                   │
                                          ┌────────▼─────────┐
                                          │   EMA Smoothing   │
                                          │   (α = 0.3)       │
                                          └────────┬─────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                    ┌─────────▼────────┐ ┌────────▼────────┐ ┌───────▼────────┐
                    │  np.interp → dB  │ │ np.interp → %   │ │  UI Overlay    │
                    │  PyCaw COM API   │ │ Volume Bar + %   │ │  Landmarks     │
                    └──────────────────┘ └─────────────────┘ └────────────────┘
```

---

## 📋 Prerequisites

- **Python 3.9+**
- **Windows 10/11** (PyCaw requires the Windows Core Audio API)
- A working **webcam** (built-in or USB)

---

## 🚀 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Hasara-269/gesture-volume-control.git
   cd gesture-volume-control
   ```

2. **Switch to the dev branch**

   ```bash
   git checkout dev
   ```

3. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

```bash
python main.py
```

| Action | Result |
|--------|--------|
| **Pinch thumb + index together** | Volume → 0 % (mute) |
| **Spread thumb + index apart** | Volume → 100 % (max) |
| **Press `q`** | Quit cleanly |

---

## ⚙️ Configuration

All tuneable constants are defined at the top of `main.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `CAM_INDEX` | `0` | Webcam device index |
| `CAM_WIDTH` | `640` | Capture width (px) |
| `CAM_HEIGHT` | `480` | Capture height (px) |
| `MIN_DIST` | `20` | Minimum pinch distance → 0 % volume |
| `MAX_DIST` | `200` | Maximum pinch distance → 100 % volume |
| `EMA_ALPHA` | `0.3` | Smoothing factor (higher = more responsive) |
| `DETECTION_CONF` | `0.7` | MediaPipe detection confidence threshold |
| `TRACKING_CONF` | `0.7` | MediaPipe tracking confidence threshold |

### Distance Calibration

The default `MIN_DIST=20` / `MAX_DIST=200` works well at **50–80 cm** from the webcam at 640×480. If you sit closer or further away, adjust these values:

- **Closer to camera** → increase `MAX_DIST` (e.g., 250–300)
- **Further from camera** → decrease `MAX_DIST` (e.g., 120–150)

---

## 🗂️ Project Structure

```
gesture-volume-control/
├── main.py              # Complete application (entry point)
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── LICENSE              # MIT License
└── .gitignore           # Python gitignore
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `Cannot open webcam at index 0` | Check camera connection. Try `CAM_INDEX = 1` for external cameras. |
| `Neither pycaw nor pyautogui is installed` | Run `pip install pycaw comtypes pyautogui` |
| PyCaw import error on non-Windows | PyCaw is Windows-only. On macOS/Linux, the app falls back to PyAutoGUI volume keys (less smooth). |
| Jittery volume changes | Lower `EMA_ALPHA` (e.g., `0.15`) for heavier smoothing. |
| Low FPS | Reduce `CAM_WIDTH`/`CAM_HEIGHT` or lower MediaPipe confidence thresholds. |
| Hand not detected | Ensure good lighting. Face your palm toward the camera. |

---

## 🛠️ Tech Stack

| Library | Purpose |
|---------|---------|
| [OpenCV](https://opencv.org/) | Webcam capture, image processing, UI rendering |
| [MediaPipe](https://mediapipe.dev/) | Real-time hand landmark detection |
| [NumPy](https://numpy.org/) | Numerical interpolation and array ops |
| [PyCaw](https://github.com/AndreMiras/pycaw) | Windows Core Audio API (COM) volume control |
| [comtypes](https://github.com/enthought/comtypes) | COM interface support for PyCaw |
| [PyAutoGUI](https://pyautogui.readthedocs.io/) | Cross-platform fallback via volume keys |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
