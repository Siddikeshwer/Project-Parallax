"""Scale alignment and configurable mono/stereo depth fusion."""
from __future__ import annotations
import numpy as np


def align_monocular_to_stereo(mono: np.ndarray, stereo_m: np.ndarray) -> np.ndarray:
    """Robustly fit scale and shift on valid stereo pixels; preserves relative output if no overlap."""
    mask = np.isfinite(stereo_m) & np.isfinite(mono) & (stereo_m > 0)
    if mask.sum() < 100:
        return mono.astype(np.float32)
    x, y = mono[mask], stereo_m[mask]
    low, high = np.percentile(x, [5, 95])
    use = mask & (mono >= low) & (mono <= high)
    scale, shift = np.polyfit(mono[use], stereo_m[use], 1)
    return (mono * scale + shift).astype(np.float32)


def fuse_depth(mono: np.ndarray, stereo: np.ndarray, stereo_confidence: np.ndarray, method: str = "confidence", stereo_weight: float = 0.7, mono_weight: float = 0.3) -> np.ndarray:
    """Fuse aligned maps. Confidence mode defers to mono in weak/invalid stereo regions."""
    aligned = align_monocular_to_stereo(mono, stereo)
    valid_stereo = np.isfinite(stereo) & (stereo > 0)
    if method == "simple":
        result = aligned.copy()
        result[valid_stereo] = stereo_weight * stereo[valid_stereo] + mono_weight * aligned[valid_stereo]
        return result
    stereo_c = np.where(valid_stereo, np.clip(stereo_confidence, 0.02, 1), 0)
    mono_c = np.where(np.isfinite(aligned), 0.35, 0)
    denominator = stereo_c + mono_c
    return np.divide(stereo_c * np.nan_to_num(stereo) + mono_c * aligned, denominator, out=aligned.copy(), where=denominator > 0)
