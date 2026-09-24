"""Display helpers for annotated detections and normalized maps."""
from __future__ import annotations
import cv2
import numpy as np
from src.detection.object_detector import Detection

def normalize_for_display(depth: np.ndarray) -> np.ndarray:
    valid = np.isfinite(depth)
    if not valid.any(): return np.zeros_like(depth, dtype=np.float32)
    lo, hi = np.percentile(depth[valid], [2, 98])
    return np.clip((depth - lo) / max(hi - lo, 1e-6), 0, 1)

def draw_detections(rgb: np.ndarray, detections: list[Detection], metric: bool) -> np.ndarray:
    image = rgb.copy()
    for item in detections:
        x1, y1, x2, y2 = item.xyxy
        cv2.rectangle(image, (x1,y1), (x2,y2), (34,211,238), 2)
        distance = f"{item.distance_m:.1f}m" if item.distance_m is not None else "depth unavailable"
        prefix = "" if metric else "~"
        cv2.putText(image, f"{item.label} {item.confidence:.2f} | {prefix}{distance}", (x1,max(18,y1-7)), cv2.FONT_HERSHEY_SIMPLEX, .5, (255,255,255), 2)
        cv2.putText(image, f"{item.label} {item.confidence:.2f} | {prefix}{distance}", (x1,max(18,y1-7)), cv2.FONT_HERSHEY_SIMPLEX, .5, (9,30,66), 1)
    return image
