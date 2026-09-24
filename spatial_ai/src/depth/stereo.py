"""Classical stereo matching and depth conversion.
Z = f * B / d, where focal length f is pixels, baseline B is metres, and disparity d is pixels.
"""
from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np


@dataclass
class StereoSettings:
    focal_length_px: float = 700.0
    baseline_m: float = 0.12
    min_disparity: int = 0
    num_disparities: int = 128
    block_size: int = 5


@dataclass
class StereoResult:
    disparity: np.ndarray
    depth_m: np.ndarray
    confidence: np.ndarray
    calibrated: bool


def compute_stereo(left_rgb: np.ndarray, right_rgb: np.ndarray, settings: StereoSettings, calibrated: bool = False) -> StereoResult:
    """Compute SGBM disparity; metric units are approximate unless images are rectified/calibrated."""
    if left_rgb.shape != right_rgb.shape:
        raise ValueError("Left and right images must have identical dimensions.")
    disparities = max(16, int(settings.num_disparities / 16) * 16)
    block = max(3, settings.block_size | 1)
    matcher = cv2.StereoSGBM_create(
        minDisparity=settings.min_disparity, numDisparities=disparities, blockSize=block,
        P1=8 * 3 * block**2, P2=32 * 3 * block**2, uniquenessRatio=8,
        speckleWindowSize=80, speckleRange=2, disp12MaxDiff=1, mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
    )
    left = cv2.cvtColor(left_rgb, cv2.COLOR_RGB2GRAY)
    right = cv2.cvtColor(right_rgb, cv2.COLOR_RGB2GRAY)
    disparity = matcher.compute(left, right).astype(np.float32) / 16.0
    valid = disparity > max(settings.min_disparity, 0)
    depth = np.full_like(disparity, np.nan, dtype=np.float32)
    depth[valid] = settings.focal_length_px * settings.baseline_m / disparity[valid]
    texture = cv2.normalize(cv2.Laplacian(left, cv2.CV_32F), None, 0, 1, cv2.NORM_MINMAX)
    confidence = np.where(valid, np.clip(texture + 0.25, 0, 1), 0).astype(np.float32)
    return StereoResult(disparity, depth, confidence, calibrated)


def colorize_disparity(disparity: np.ndarray) -> np.ndarray:
    valid = np.isfinite(disparity) & (disparity > 0)
    output = np.zeros((*disparity.shape, 3), dtype=np.uint8)
    if valid.any():
        values = disparity[valid]
        normalized = np.clip((disparity - values.min()) / max(values.max() - values.min(), 1e-6), 0, 1)
        output = cv2.cvtColor(cv2.applyColorMap((normalized * 255).astype(np.uint8), cv2.COLORMAP_TURBO), cv2.COLOR_BGR2RGB)
        output[~valid] = 0
    return output
