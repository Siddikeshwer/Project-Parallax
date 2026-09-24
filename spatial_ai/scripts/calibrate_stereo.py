"""CLI for paired chessboard intrinsic calibration output."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import cv2
sys.path.insert(0, str(Path(__file__).parents[1]))
from src.calibration.stereo_calibration import calibrate_stereo
p=argparse.ArgumentParser(); p.add_argument("--left", nargs="+", required=True); p.add_argument("--right", nargs="+", required=True); p.add_argument("--board", nargs=2,type=int,default=[9,6]); p.add_argument("--square",type=float,required=True); p.add_argument("--output",default="configs/calibration.json")
a=p.parse_args()
if len(a.left)!=len(a.right): p.error("--left and --right must contain equal numbers of paired images")
read=lambda paths:[cv2.cvtColor(cv2.imread(x),cv2.COLOR_BGR2RGB) for x in paths]
calibrate_stereo(read(a.left),read(a.right),tuple(a.board),a.square,a.output); print(f"Saved {a.output}")
