"""Frame-skipped video processing for bounded Streamlit workloads."""
from __future__ import annotations
from typing import Callable
import cv2

def process_video(path: str, process_frame: Callable, interval: int = 3, max_frames: int = 180):
    capture = cv2.VideoCapture(path)
    index = 0
    try:
        while index < max_frames:
            ok, frame = capture.read()
            if not ok: break
            if index % interval == 0:
                yield index, process_frame(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            index += 1
    finally:
        capture.release()
