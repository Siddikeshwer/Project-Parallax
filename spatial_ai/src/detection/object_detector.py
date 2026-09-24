"""YOLO detection with robust per-object depth summaries."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Detection:
    label: str
    confidence: float
    xyxy: tuple[int, int, int, int]
    distance_m: float | None

class ObjectDetector:
    def __init__(self, model_name: str = "yolo11n.pt", device: str = "cpu") -> None:
        self.model_name, self.device, self._model = model_name, device, None

    def _load(self) -> None:
        if self._model is None:
            from ultralytics import YOLO
            self._model = YOLO(self.model_name)

    def detect(self, rgb: np.ndarray, depth_m: np.ndarray | None, threshold: float = 0.4) -> list[Detection]:
        self._load()
        assert self._model is not None
        result: Any = self._model(rgb, conf=threshold, device=self.device, verbose=False)[0]
        output: list[Detection] = []
        for box in result.boxes:
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            distance = None
            if depth_m is not None:
                values = depth_m[max(y1, 0):max(y2, 0), max(x1, 0):max(x2, 0)]
                values = values[np.isfinite(values) & (values > 0)]
                if values.size:
                    distance = float(np.median(values))
            output.append(Detection(result.names[int(box.cls[0])], float(box.conf[0]), (x1, y1, x2, y2), distance))
        return output
