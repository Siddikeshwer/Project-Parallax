"""CLI for intrinsic calibration: python scripts/calibrate_camera.py images/*.png --board 9 6 --square 0.024"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
import cv2
sys.path.insert(0, str(Path(__file__).parents[1]))
from src.calibration.camera_calibration import calibrate_camera
p=argparse.ArgumentParser(); p.add_argument("images", nargs="+"); p.add_argument("--board", nargs=2, type=int, default=[9,6]); p.add_argument("--square", type=float, required=True); p.add_argument("--output", default="configs/camera_calibration.json")
a=p.parse_args(); images=[cv2.cvtColor(cv2.imread(x), cv2.COLOR_BGR2RGB) for x in a.images]; result=calibrate_camera(images, tuple(a.board), a.square)
Path(a.output).write_text(json.dumps({"camera_matrix":result.matrix.tolist(),"distortion":result.distortion.tolist(),"rms":result.rms}, indent=2)); print(f"Saved {a.output}; RMS={result.rms:.4f}")
