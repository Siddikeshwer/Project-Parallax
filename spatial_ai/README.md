# DepthForge — Spatial AI

A camera-based spatial perception research prototype. DepthForge combines **Depth Anything V2** relative monocular depth with **OpenCV StereoSGBM** geometric depth, aligns their scales where valid overlap exists, and produces a confidence-aware fused map for object distance estimation and RGB-D point clouds.

> **Not an autonomous-driving system.** This project is an inspectable computer-vision prototype. It does not present learned depth, uncalibrated stereo, or fused output as ground truth.

## What is included

- Streamlit dashboard for RGB images, matched stereo pairs, captured stills, and an honest video-processing fallback
- Cached Hugging Face Depth Anything V2 inference with CUDA auto-selection and CPU fallback
- OpenCV StereoSGBM disparity and `Z = f × B / d` conversion
- Robust monocular-to-stereo scale/shift alignment
- Simple and confidence-aware fusion modes
- YOLO object detections using median depth inside each bounding box
- Plotly 3D point-cloud preview and Open3D `.ply` export
- Chessboard intrinsic calibration scripts
- Config-driven defaults, unit tests, and dataset/evaluation guidance

## Architecture

```text
RGB image ──► monocular depth ─┐
                               ├─► alignment ─► confidence fusion ─► objects / RGB-D cloud
Stereo pair ─► SGBM disparity ─┘
```

See [`docs/architecture.md`](docs/architecture.md) for the module map.

## Depth methodology

### Monocular

The pretrained Depth Anything V2 model predicts scene-relative depth from learned visual cues. Its output is useful for ordering surfaces, but has no guaranteed metric scale. It is normalized for display; lighter inferno tones denote higher normalized values.

### Stereo

For rectified cameras, the project converts disparity to depth using:

```text
Z = (f × B) / d
```

`f` is focal length in pixels, `B` is baseline in metres, and `d` is horizontal disparity in pixels. This is metric only when intrinsics, baseline, and rectification are valid. The dashboard otherwise calls it **approximate**.

### Fusion

`simple` fusion blends valid stereo and aligned monocular depth at fixed weights. `confidence` fusion assigns higher stereo influence in textured, valid-disparity areas and allows the monocular prior to fill stereo holes. Fusion is not assumed to improve accuracy; evaluate it against ground truth.

## Installation and usage

Use Python 3.11+ in an isolated environment, then install `requirements.txt`. Start the dashboard from this directory with Streamlit's standard app launcher pointing to `app.py`.

At first use, Transformers downloads the selected depth model and Ultralytics downloads the selected YOLO weights. For a setup/demo-only environment, the React companion dashboard remains available without these heavy Python packages.

## Input modes

- **Single image:** relative monocular depth, optional detections; distances are not metric.
- **Stereo pair:** same-sized, horizontally aligned left/right images. Metric-looking values remain approximate until calibration and rectification are supplied.
- **Video:** `src/processing/video_processor.py` processes a bounded set of frame-skipped frames; this avoids falsely calling expensive full-frame inference real time.
- **Webcam:** Streamlit still capture is available. For reliable streaming, use local capture or uploaded video because browser/host support differs.

## Calibration

Capture at least 3, preferably 15–30, sharp chessboard views across the image. The inner-corner board dimensions and real square size must be correct. `scripts/calibrate_camera.py` writes intrinsics; `scripts/calibrate_stereo.py` stores paired intrinsic results in `configs/calibration.json` as a basis for a proper paired corner / `stereoCalibrate` session.

## Evaluation protocol

No benchmark values are committed because this repository does not ship ground-truth data or fabricated results. Use a licensed subset of KITTI (outdoor stereo), Middlebury (stereo), or NYU Depth V2 (indoor RGB-D), and record:

| Method | MAE | RMSE | AbsRel | δ<1.25 |
|---|---:|---:|---:|---:|
| Monocular | run experiment | run experiment | run experiment | run experiment |
| Stereo | run experiment | run experiment | run experiment | run experiment |
| Simple fusion | run experiment | run experiment | run experiment | run experiment |
| Confidence fusion | run experiment | run experiment | run experiment | run experiment |

For each method, mask invalid ground truth consistently, state whether depth is metric, and publish the sample IDs, calibration, resize policy, and code revision. Dataset licenses and terms must be accepted from the original publishers before download.

## Limitations

- Monocular predictions can be relative rather than metric.
- Stereo requires calibration and rectification for reliable geometry.
- Weak texture, occlusions, reflections, transparent surfaces, repeated patterns, and motion degrade disparity.
- Baseline, focal length, and disparity uncertainty all affect depth accuracy, especially far from the cameras.
- Object distance is a robust median estimate, not object pose or ground truth range.
- Fusion can hurt results where either input is systematically wrong.

## References

- Depth Anything V2, Yang et al. (2024)
- Hirschmüller, *Stereo Processing by Semi-Global Matching* (2008)
- OpenCV StereoSGBM documentation
- Ultralytics YOLO documentation
- KITTI, Middlebury Stereo, and NYU Depth V2 dataset documentation

## Project layout

```text
spatial_ai/
├── app.py                 # Streamlit application
├── src/                   # depth, fusion, calibration, detection, point cloud, video
├── scripts/               # chessboard utilities
├── configs/config.yaml    # runtime parameters
├── tests/                 # focused unit tests
└── docs/architecture.md
```

The root React application is the visual companion dashboard; it describes the research workflow and does not pretend to execute server-side CV inference.
