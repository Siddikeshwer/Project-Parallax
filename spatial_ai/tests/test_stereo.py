import numpy as np
from src.depth.stereo import StereoSettings, compute_stereo

def test_stereo_returns_matching_maps():
    left = np.tile(np.arange(160, dtype=np.uint8), (80, 1))
    left = np.repeat(left[..., None], 3, axis=2)
    right = np.roll(left, 4, axis=1)
    result = compute_stereo(left, right, StereoSettings(num_disparities=16))
    assert result.disparity.shape == left.shape[:2]
    assert result.depth_m.shape == left.shape[:2]
