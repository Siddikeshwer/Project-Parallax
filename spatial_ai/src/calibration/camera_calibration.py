"""Chessboard camera calibration utilities."""
from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np

@dataclass
class CameraCalibration:
    matrix: np.ndarray
    distortion: np.ndarray
    rvecs: list[np.ndarray]
    tvecs: list[np.ndarray]
    rms: float

def calibrate_camera(images: list[np.ndarray], board: tuple[int, int], square_size_m: float) -> CameraCalibration:
    obj = np.zeros((board[0] * board[1], 3), np.float32)
    obj[:, :2] = np.mgrid[0:board[0], 0:board[1]].T.reshape(-1, 2) * square_size_m
    object_points, image_points = [], []
    image_size = None
    for image in images:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        found, corners = cv2.findChessboardCorners(gray, board)
        if found:
            object_points.append(obj)
            image_points.append(cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, .001)))
            image_size = gray.shape[::-1]
    if len(object_points) < 3 or image_size is None:
        raise ValueError("At least three chessboard detections are required.")
    rms, matrix, distortion, rvecs, tvecs = cv2.calibrateCamera(object_points, image_points, image_size, None, None)
    return CameraCalibration(matrix, distortion, rvecs, tvecs, rms)
