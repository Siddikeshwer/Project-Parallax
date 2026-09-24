import numpy as np
from src.fusion.depth_fusion import fuse_depth

def test_confidence_fusion_prefers_valid_stereo():
    mono = np.ones((12, 12), dtype=np.float32)
    stereo = np.full((12, 12), 2.0, dtype=np.float32)
    stereo[0, 0] = np.nan
    result = fuse_depth(mono, stereo, np.ones_like(mono), "confidence")
    assert np.isfinite(result).all()
    assert result[5, 5] > 1.5
