"""Monocular depth inference backed by Hugging Face Depth Anything V2."""
from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

import cv2
import numpy as np
import torch
from PIL import Image


@dataclass
class MonocularResult:
    raw_depth: np.ndarray
    normalized_depth: np.ndarray
    elapsed_ms: float
    device: str


def choose_device(requested: str = "auto") -> str:
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return requested


class MonocularDepthEstimator:
    """Lazy-loading Depth Anything V2 estimator with a CPU-safe fallback."""

    def __init__(self, model_id: str, device: str = "auto") -> None:
        self.model_id = model_id
        self.device = choose_device(device)
        self._processor: Any | None = None
        self._model: Any | None = None

    def _load(self) -> None:
        if self._model is not None:
            return
        from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        self._processor = AutoImageProcessor.from_pretrained(self.model_id)
        self._model = AutoModelForDepthEstimation.from_pretrained(self.model_id).to(self.device).eval()

    def predict(self, rgb: np.ndarray) -> MonocularResult:
        """Infer relative depth. Values are not metric without calibration/alignment."""
        if rgb.ndim != 3 or rgb.shape[2] != 3:
            raise ValueError("Expected an RGB image with three channels.")
        self._load()
        assert self._processor is not None and self._model is not None
        inputs = self._processor(images=Image.fromarray(rgb), return_tensors="pt").to(self.device)
        started = perf_counter()
        with torch.inference_mode():
            prediction = self._model(**inputs).predicted_depth
        depth = torch.nn.functional.interpolate(
            prediction.unsqueeze(1), size=rgb.shape[:2], mode="bicubic", align_corners=False
        ).squeeze().float().cpu().numpy()
        elapsed = (perf_counter() - started) * 1000
        lo, hi = np.percentile(depth, [2, 98])
        normalized = np.clip((depth - lo) / max(hi - lo, 1e-6), 0, 1)
        return MonocularResult(depth, normalized.astype(np.float32), elapsed, self.device)


def colorize_depth(depth: np.ndarray) -> np.ndarray:
    """Render normalized depth with a consistent inferno color convention."""
    scaled = (np.clip(depth, 0, 1) * 255).astype(np.uint8)
    return cv2.cvtColor(cv2.applyColorMap(scaled, cv2.COLORMAP_INFERNO), cv2.COLOR_BGR2RGB)
