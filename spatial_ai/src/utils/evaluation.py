"""Ground-truth depth metrics for reproducible experiments."""
from __future__ import annotations
import numpy as np

def depth_metrics(prediction: np.ndarray, ground_truth: np.ndarray) -> dict[str, float]:
    """Compute MAE, RMSE, AbsRel and delta<1.25 over finite positive ground truth."""
    mask = np.isfinite(prediction) & np.isfinite(ground_truth) & (ground_truth > 0)
    if not mask.any():
        raise ValueError("No valid ground-truth depth pixels available.")
    p, g = prediction[mask], ground_truth[mask]
    ratio = np.maximum(p / np.maximum(g, 1e-6), g / np.maximum(p, 1e-6))
    return {"mae": float(np.mean(np.abs(p-g))), "rmse": float(np.sqrt(np.mean((p-g)**2))), "abs_rel": float(np.mean(np.abs(p-g)/g)), "delta_1_25": float(np.mean(ratio < 1.25))}
