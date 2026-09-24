"""Paired chessboard stereo calibration and rectification serialization."""
from __future__ import annotations
import json
from pathlib import Path
import cv2
import numpy as np

def calibrate_stereo(left_images: list[np.ndarray], right_images: list[np.ndarray], board: tuple[int, int], square_size_m: float, output: str | Path) -> dict:
    """Estimate intrinsics, relative R/T, essential/fundamental matrices and rectification transforms."""
    if len(left_images) != len(right_images):
        raise ValueError("Stereo calibration requires equal numbers of paired images.")
    obj = np.zeros((board[0] * board[1], 3), np.float32)
    obj[:, :2] = np.mgrid[0:board[0], 0:board[1]].T.reshape(-1, 2) * square_size_m
    objects, left_points, right_points = [], [], []
    image_size = None
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, .001)
    for left, right in zip(left_images, right_images):
        lg, rg = cv2.cvtColor(left, cv2.COLOR_RGB2GRAY), cv2.cvtColor(right, cv2.COLOR_RGB2GRAY)
        found_l, corners_l = cv2.findChessboardCorners(lg, board)
        found_r, corners_r = cv2.findChessboardCorners(rg, board)
        if found_l and found_r:
            objects.append(obj)
            left_points.append(cv2.cornerSubPix(lg, corners_l, (11, 11), (-1, -1), criteria))
            right_points.append(cv2.cornerSubPix(rg, corners_r, (11, 11), (-1, -1), criteria))
            image_size = lg.shape[::-1]
    if len(objects) < 3 or image_size is None:
        raise ValueError("At least three paired chessboard detections are required.")
    _, K1, d1, _, _ = cv2.calibrateCamera(objects, left_points, image_size, None, None)
    _, K2, d2, _, _ = cv2.calibrateCamera(objects, right_points, image_size, None, None)
    rms, K1, d1, K2, d2, R, T, E, F = cv2.stereoCalibrate(objects, left_points, right_points, K1, d1, K2, d2, image_size, flags=cv2.CALIB_FIX_INTRINSIC, criteria=criteria)
    R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(K1, d1, K2, d2, image_size, R, T, alpha=0)
    payload = {"rms": rms, "image_size": list(image_size), "left_camera_matrix": K1.tolist(), "left_distortion": d1.tolist(), "right_camera_matrix": K2.tolist(), "right_distortion": d2.tolist(), "rotation": R.tolist(), "translation": T.tolist(), "essential_matrix": E.tolist(), "fundamental_matrix": F.tolist(), "rectification_left": R1.tolist(), "rectification_right": R2.tolist(), "projection_left": P1.tolist(), "projection_right": P2.tolist(), "disparity_to_depth_Q": Q.tolist(), "pairs_used": len(objects)}
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(payload, indent=2))
    return payload
