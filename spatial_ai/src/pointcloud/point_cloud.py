"""RGB-D point cloud construction and safe PLY export."""
from __future__ import annotations
from pathlib import Path
import numpy as np


def rgbd_to_points(rgb: np.ndarray, depth_m: np.ndarray, fx: float, fy: float, cx: float | None = None, cy: float | None = None, stride: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Project valid RGB-D pixels using pinhole intrinsics."""
    h, w = depth_m.shape
    cx, cy = (w - 1) / 2 if cx is None else cx, (h - 1) / 2 if cy is None else cy
    yy, xx = np.mgrid[0:h:stride, 0:w:stride]
    z = depth_m[::stride, ::stride]
    valid = np.isfinite(z) & (z > 0) & (z < 100)
    points = np.column_stack(((xx[valid] - cx) * z[valid] / fx, (yy[valid] - cy) * z[valid] / fy, z[valid]))
    return points.astype(np.float32), (rgb[::stride, ::stride][valid] / 255.0).astype(np.float32)


def save_ply(path: str | Path, points: np.ndarray, colors: np.ndarray) -> None:
    import open3d as o3d
    cloud = o3d.geometry.PointCloud()
    cloud.points = o3d.utility.Vector3dVector(points)
    cloud.colors = o3d.utility.Vector3dVector(colors)
    o3d.io.write_point_cloud(str(path), cloud)
