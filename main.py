"""
Gesture Volume Controller
=========================
A real-time computer vision application that tracks the pinch distance
between the thumb tip and index finger tip via a webcam feed and maps
that distance smoothly to the Windows system master volume.

Tech stack:  Python · OpenCV · MediaPipe (Task API) · NumPy · PyCaw

Controls:
    - Pinch fingers together  → volume drops to 0 %
    - Spread fingers apart    → volume rises to 100 %
    - Press 'q'               → quit

Author:  Gesture-Volume-Control contributors
License: MIT
"""

# ──────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────
import os
import sys
import math
import time
import urllib.request

import cv2
import numpy as np
import mediapipe as mp

# MediaPipe Task API imports
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# ──────────────────────────────────────────────
# Volume backend — PyCaw (Windows) with fallback
# ──────────────────────────────────────────────
PYCAW_AVAILABLE = False
PYAUTOGUI_AVAILABLE = False

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    PYCAW_AVAILABLE = True
except ImportError:
    pass

if not PYCAW_AVAILABLE:
    try:
        import pyautogui

        PYAUTOGUI_AVAILABLE = True
        print("[WARN] PyCaw not found — falling back to PyAutoGUI volume keys.")
        print("       This may trigger the Windows volume OSD overlay.")
    except ImportError:
        pass

if not PYCAW_AVAILABLE and not PYAUTOGUI_AVAILABLE:
    print("[ERROR] Neither 'pycaw' nor 'pyautogui' is installed.")
    print("        Install with:  pip install pycaw comtypes pyautogui")
    sys.exit(1)


# ──────────────────────────────────────────────
# Tuneable Constants
# ──────────────────────────────────────────────
CAM_INDEX      = 0          # Webcam device index (0 = default)
CAM_WIDTH      = 640        # Capture width  (px)
CAM_HEIGHT     = 480        # Capture height (px)

MIN_DIST       = 20         # Minimum pinch distance (px) → 0 % volume
MAX_DIST       = 200        # Maximum pinch distance (px) → 100 % volume

EMA_ALPHA      = 0.3        # Exponential moving average smoothing factor
                            #   ↑ higher = more responsive, ↓ lower = smoother
VOL_EMA_ALPHA  = 0.25       # Exponential moving average smoothing factor for volume

DETECTION_CONF = 0.7        # MediaPipe minimum detection confidence
TRACKING_CONF  = 0.7        # MediaPipe minimum tracking confidence

# Landmark indices (MediaPipe hand model — 21 landmarks)
THUMB_TIP      = 4
INDEX_TIP      = 8

# Model file configuration
MODEL_URL  = ("https://storage.googleapis.com/mediapipe-models/"
              "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
MODEL_DIR  = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")

# UI colours (BGR)
COLOR_CYAN     = (255, 255, 0)
COLOR_GREEN    = (0, 255, 0)
COLOR_MAGENTA  = (255, 0, 255)
COLOR_RED      = (0, 0, 255)
COLOR_WHITE    = (255, 255, 255)
COLOR_BLACK    = (0, 0, 0)
COLOR_DARK_GRAY = (40, 40, 40)
COLOR_BAR_BG   = (50, 50, 50)
COLOR_BAR_FILL = (255, 178, 0)     # Warm amber fill
COLOR_BAR_MUTE = (0, 100, 255)     # Orange-red when muted
COLOR_BAR_MAX  = (0, 255, 100)     # Bright green when maxed

# Volume bar geometry
BAR_X          = 30         # Left edge of bar
BAR_W          = 28         # Bar width
BAR_TOP        = 80         # Top edge of bar
BAR_BOTTOM     = 380        # Bottom edge of bar
BAR_HEIGHT     = BAR_BOTTOM - BAR_TOP


# ──────────────────────────────────────────────
# Model Download Helper
# ──────────────────────────────────────────────
def ensure_model():
    """
    Download the MediaPipe hand_landmarker.task model if it does not
    already exist in the project directory.
    """
    if os.path.isfile(MODEL_PATH):
        return
    print(f"[INFO] Downloading hand landmarker model to {MODEL_PATH} ...")
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("[INFO] Model downloaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to download model: {e}")
        print(f"        Please download manually from:\n        {MODEL_URL}")
        print(f"        and place it at: {MODEL_PATH}")
        sys.exit(1)


# ──────────────────────────────────────────────
# Volume Initialisation
# ──────────────────────────────────────────────
def init_volume():
    """
    Initialise the system volume interface.

    Returns
    -------
    volume : IAudioEndpointVolume | None
        The COM volume endpoint (PyCaw), or None when using fallback.
    vol_min : float
        Minimum volume in dB (PyCaw) or 0 (fallback).
    vol_max : float
        Maximum volume in dB (PyCaw) or 100 (fallback).
    """
    if PYCAW_AVAILABLE:
        device = AudioUtilities.GetSpeakers()
        volume = device.EndpointVolume
        vol_range = volume.GetVolumeRange()  # (min_dB, max_dB, step_dB)
        return volume, vol_range[0], vol_range[1]

    # Fallback — PyAutoGUI operates in 0-100 percentage space
    return None, 0.0, 100.0


def set_volume(volume_iface, level_db):
    """
    Set the master volume.

    Parameters
    ----------
    volume_iface : IAudioEndpointVolume | None
    level_db : float
        Volume level in dB (PyCaw) or percentage 0-100 (fallback).
    """
    if PYCAW_AVAILABLE and volume_iface is not None:
        volume_iface.SetMasterVolumeLevel(level_db, None)
    elif PYAUTOGUI_AVAILABLE:
        # Approximate: press volume keys proportionally
        # (crude but functional fallback)
        pass  # handled in the main loop for the fallback path


# ──────────────────────────────────────────────
# Drawing Helpers
# ──────────────────────────────────────────────
def draw_volume_bar(frame, vol_pct, is_muted, is_maxed):
    """
    Draw a vertical volume bar on the left side of the frame.

    Parameters
    ----------
    frame : np.ndarray
        The BGR video frame to draw on (mutated in-place).
    vol_pct : float
        Current volume percentage (0–100).
    is_muted : bool
        True when volume is at 0 %.
    is_maxed : bool
        True when volume is at 100 %.
    """
    # Background track
    cv2.rectangle(
        frame,
        (BAR_X - 2, BAR_TOP - 2),
        (BAR_X + BAR_W + 2, BAR_BOTTOM + 2),
        COLOR_DARK_GRAY,
        cv2.FILLED,
    )
    cv2.rectangle(
        frame,
        (BAR_X, BAR_TOP),
        (BAR_X + BAR_W, BAR_BOTTOM),
        COLOR_BAR_BG,
        cv2.FILLED,
    )

    # Filled portion (bottom-up)
    fill_h = int(np.interp(vol_pct, [0, 100], [0, BAR_HEIGHT]))
    fill_top = BAR_BOTTOM - fill_h

    # Choose bar colour based on state
    if is_muted:
        fill_color = COLOR_BAR_MUTE
    elif is_maxed:
        fill_color = COLOR_BAR_MAX
    else:
        fill_color = COLOR_BAR_FILL

    if fill_h > 0:
        cv2.rectangle(
            frame,
            (BAR_X, fill_top),
            (BAR_X + BAR_W, BAR_BOTTOM),
            fill_color,
            cv2.FILLED,
        )

    # Border
    cv2.rectangle(
        frame,
        (BAR_X - 2, BAR_TOP - 2),
        (BAR_X + BAR_W + 2, BAR_BOTTOM + 2),
        COLOR_WHITE,
        1,
    )

    # Percentage text beside the bar
    label = f"{int(vol_pct)}%"
    label_y = fill_top - 10 if fill_top - 10 > BAR_TOP else BAR_TOP + 20
    cv2.putText(
        frame, label,
        (BAR_X - 5, label_y),
        cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_WHITE, 2,
    )

    # Tick marks
    for pct in (0, 25, 50, 75, 100):
        y = int(np.interp(pct, [0, 100], [BAR_BOTTOM, BAR_TOP]))
        cv2.line(frame, (BAR_X - 6, y), (BAR_X, y), COLOR_WHITE, 1)


def draw_landmarks(frame, thumb, index, vol_pct, is_muted, is_maxed):
    """
    Draw landmark circles, connecting line, and visual feedback.

    Parameters
    ----------
    frame : np.ndarray
    thumb : tuple[int, int]
        (x, y) of the thumb tip.
    index : tuple[int, int]
        (x, y) of the index finger tip.
    vol_pct : float
    is_muted : bool
    is_maxed : bool
    """
    # Connecting line — green at extremes, cyan otherwise
    if is_muted or is_maxed:
        line_color = COLOR_GREEN
        line_thickness = 3
    else:
        line_color = COLOR_CYAN
        line_thickness = 2

    cv2.line(frame, thumb, index, line_color, line_thickness)

    # Landmark circles
    cv2.circle(frame, thumb, 10, COLOR_MAGENTA, cv2.FILLED)
    cv2.circle(frame, thumb, 12, COLOR_WHITE, 1)
    cv2.circle(frame, index, 10, COLOR_MAGENTA, cv2.FILLED)
    cv2.circle(frame, index, 12, COLOR_WHITE, 1)

    # Midpoint
    mid_x = (thumb[0] + index[0]) // 2
    mid_y = (thumb[1] + index[1]) // 2

    # Pulse circle at extremes (animated via time-based radius oscillation)
    if is_muted or is_maxed:
        pulse = int(12 + 6 * math.sin(time.time() * 8))  # oscillates 6–18
        overlay = frame.copy()
        cv2.circle(overlay, (mid_x, mid_y), pulse, COLOR_GREEN, cv2.FILLED)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    else:
        cv2.circle(frame, (mid_x, mid_y), 6, COLOR_CYAN, cv2.FILLED)

    # Volume percentage near the midpoint
    cv2.putText(
        frame, f"{int(vol_pct)}%",
        (mid_x + 15, mid_y + 5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 2,
    )


def draw_fps(frame, fps):
    """Overlay FPS counter in the top-left corner."""
    cv2.putText(
        frame, f"FPS: {int(fps)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_GREEN, 2,
    )


def draw_no_hand(frame):
    """Show a hint message when no hand is detected."""
    cv2.putText(
        frame, "Show your hand to control volume",
        (CAM_WIDTH // 2 - 200, CAM_HEIGHT // 2),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WHITE, 1,
    )


# ──────────────────────────────────────────────
# Main Application Loop
# ──────────────────────────────────────────────
def main():
    """Entry point — initialise resources and run the tracking loop."""

    # ── Model download ─────────────────────
    ensure_model()

    # ── Volume backend ──────────────────────
    volume_iface, vol_min, vol_max = init_volume()
    print(f"[INFO] Volume backend: {'PyCaw (COM)' if PYCAW_AVAILABLE else 'PyAutoGUI'}")
    if PYCAW_AVAILABLE:
        print(f"[INFO] Volume range: {vol_min:.1f} dB → {vol_max:.1f} dB")

    # ── MediaPipe Hand Landmarker (Task API) ─
    #    Using VIDEO running mode for synchronous per-frame detection.
    base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
    options = mp_vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=DETECTION_CONF,
        min_hand_presence_confidence=DETECTION_CONF,
        min_tracking_confidence=TRACKING_CONF,
    )
    landmarker = mp_vision.HandLandmarker.create_from_options(options)
    print("[INFO] MediaPipe HandLandmarker initialised (Task API, VIDEO mode).")

    # ── Webcam ──────────────────────────────
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] Cannot open webcam at index {CAM_INDEX}.")
        print("        Check that your camera is connected and not in use.")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    print(f"[INFO] Webcam opened at {CAM_WIDTH}x{CAM_HEIGHT}.")

    # ── State variables ─────────────────────
    prev_time   = time.time()
    fps         = 0.0
    smooth_dist = None          # EMA-smoothed distance (initialised on first frame)
    smooth_vol_pct = None       # EMA-smoothed volume percentage
    smooth_vol_db = None        # EMA-smoothed volume dB
    vol_pct     = 0.0           # current volume percentage
    frame_drop_count = 0        # consecutive dropped frames counter
    frame_index = 0             # monotonic frame counter for timestamp_ms

    # ── Fallback volume state (PyAutoGUI) ───
    fallback_vol = 50           # approximate current level for key-press fallback

    print("[INFO] Starting gesture tracking — press 'q' to quit.\n")

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                frame_drop_count += 1
                if frame_drop_count > 30:
                    print("[ERROR] Too many consecutive dropped frames — exiting.")
                    break
                continue
            frame_drop_count = 0  # reset on successful read

            # ── Pre-processing ──────────────
            frame = cv2.flip(frame, 1)  # mirror / selfie view
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ── Hand detection (Task API) ───
            #    Convert the OpenCV RGB frame to a MediaPipe Image.
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame,
            )
            # detect_for_video requires a monotonically increasing timestamp_ms
            frame_index += 1
            timestamp_ms = int(frame_index * (1000 / 30))  # approximate 30 fps timestamps

            results = landmarker.detect_for_video(mp_image, timestamp_ms)

            if results.hand_landmarks:
                # results.hand_landmarks is a list of lists of NormalizedLandmark
                hand_lm = results.hand_landmarks[0]  # first (only) hand
                h, w, _ = frame.shape

                # Extract thumb tip & index tip pixel coordinates
                thumb_lm = hand_lm[THUMB_TIP]
                index_lm = hand_lm[INDEX_TIP]

                tx, ty = int(thumb_lm.x * w), int(thumb_lm.y * h)
                ix, iy = int(index_lm.x * w), int(index_lm.y * h)

                # ── Euclidean distance ──────
                raw_dist = math.hypot(ix - tx, iy - ty)

                # ── EMA smoothing ───────────
                if smooth_dist is None:
                    smooth_dist = raw_dist
                else:
                    smooth_dist = EMA_ALPHA * raw_dist + (1 - EMA_ALPHA) * smooth_dist

                # ── Map to volume ───────────
                # Clamp smoothed distance to [MIN_DIST, MAX_DIST]
                clamped = np.clip(smooth_dist, MIN_DIST, MAX_DIST)

                if PYCAW_AVAILABLE:
                    # Interpolate to dB range for perceptually smooth control
                    target_vol_db = np.interp(clamped, [MIN_DIST, MAX_DIST], [vol_min, vol_max])
                    if smooth_vol_db is None:
                        smooth_vol_db = target_vol_db
                    else:
                        smooth_vol_db = VOL_EMA_ALPHA * target_vol_db + (1 - VOL_EMA_ALPHA) * smooth_vol_db
                    set_volume(volume_iface, float(smooth_vol_db))

                target_vol_pct = float(np.interp(clamped, [MIN_DIST, MAX_DIST], [0, 100]))
                if smooth_vol_pct is None:
                    smooth_vol_pct = target_vol_pct
                else:
                    smooth_vol_pct = VOL_EMA_ALPHA * target_vol_pct + (1 - VOL_EMA_ALPHA) * smooth_vol_pct
                vol_pct = smooth_vol_pct

                # ── PyAutoGUI fallback ──────
                if not PYCAW_AVAILABLE and PYAUTOGUI_AVAILABLE:
                    target = int(vol_pct)
                    diff = target - fallback_vol
                    steps = abs(diff) // 2  # each key press ≈ 2 %
                    key = "volumeup" if diff > 0 else "volumedown"
                    for _ in range(min(steps, 5)):  # cap to avoid lag
                        pyautogui.press(key)
                    fallback_vol = target

                # ── Draw landmarks & line ───
                is_muted = vol_pct <= 0.5
                is_maxed = vol_pct >= 99.5
                draw_landmarks(frame, (tx, ty), (ix, iy), vol_pct, is_muted, is_maxed)
            else:
                draw_no_hand(frame)

            # ── Volume bar (always visible) ─
            draw_volume_bar(frame, vol_pct, vol_pct <= 0.5, vol_pct >= 99.5)

            # ── FPS calculation ─────────────
            curr_time = time.time()
            fps = 1.0 / (curr_time - prev_time + 1e-9)
            prev_time = curr_time
            draw_fps(frame, fps)

            # ── Display ────────────────────
            cv2.imshow("Gesture Volume Controller", frame)

            # ── Keyboard listener ──────────
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("[INFO] 'q' pressed — shutting down.")
                break

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user (Ctrl+C).")

    finally:
        # ── Cleanup ────────────────────────
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()
        print("[INFO] Resources released. Goodbye!")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
