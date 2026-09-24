import numpy as np
from src.depth.monocular import colorize_depth

def test_depth_colorization_returns_rgb():
    rendered = colorize_depth(np.linspace(0, 1, 20, dtype=np.float32).reshape(4, 5))
    assert rendered.shape == (4, 5, 3)
    assert rendered.dtype == np.uint8
