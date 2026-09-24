"""DepthForge Streamlit dashboard — run with: streamlit run app.py"""
from __future__ import annotations
import sys
from pathlib import Path
import tempfile
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import yaml

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from src.depth.monocular import MonocularDepthEstimator, colorize_depth
from src.depth.stereo import StereoSettings, compute_stereo, colorize_disparity
from src.fusion.depth_fusion import fuse_depth
from src.detection.object_detector import ObjectDetector
from src.pointcloud.point_cloud import rgbd_to_points, save_ply
from src.utils.visualization import normalize_for_display, draw_detections

st.set_page_config(page_title="DepthForge — Spatial AI", page_icon="◈", layout="wide")
config = yaml.safe_load((ROOT / "configs/config.yaml").read_text())

@st.cache_resource(show_spinner="Loading depth model…")
def depth_engine(model_id: str, device: str): return MonocularDepthEstimator(model_id, device)
@st.cache_resource(show_spinner="Loading YOLO…")
def detector_engine(model: str, device: str): return ObjectDetector(model, device)
def upload_rgb(file): return np.asarray(Image.open(file).convert("RGB"))

def cloud_figure(points, colors):
    return go.Figure(go.Scatter3d(x=points[:,0], y=points[:,1], z=points[:,2], mode="markers", marker={"size":2,"color":colors,"opacity":.8}, hoverinfo="skip"), layout={"height":460,"margin":{"l":0,"r":0,"b":0,"t":20},"scene":{"xaxis_title":"X (m)","yaxis_title":"Y (m)","zaxis_title":"Z (m)","aspectmode":"data"}})

st.title("SPATIAL AI")
st.caption("Camera-based 3D scene understanding • monocular + stereo depth fusion")
with st.sidebar:
    mode = st.radio("INPUT MODE", ["Single Image", "Stereo Pair", "Video", "Webcam"], index=0)
    st.divider(); st.subheader("MODEL SETTINGS")
    model_id = st.selectbox("Depth model", [config["runtime"]["depth_model"]])
    device = st.selectbox("Device", ["auto", "cpu", "cuda"])
    enable_yolo = st.toggle("Object detection", True)
    threshold = st.slider("Detection confidence", .1, .9, .4)
    st.divider(); st.subheader("STEREO SETTINGS")
    focal = st.number_input("Focal length (px)", 50.0, 5000.0, float(config["stereo"]["focal_length_px"]))
    baseline = st.number_input("Baseline (m)", .01, 2.0, float(config["stereo"]["baseline_m"]), .01)
    disparities = st.select_slider("Number of disparities", options=[16,32,64,96,128,160,192], value=128)
    block = st.select_slider("Block size", options=[3,5,7,9,11], value=5)
    st.caption("Metric output requires rectified, calibrated imagery. Otherwise distances are approximate.")

if mode == "Webcam":
    st.info("Browser-native webcam streaming varies by Streamlit host. Use uploaded video for reliable processing, or capture a still below.")
    single = st.camera_input("Capture scene")
    right = None
elif mode == "Video":
    st.info("Video processing is frame-skipped by design to keep inference bounded. Upload a short clip for analysis.")
    single = st.file_uploader("Upload video", type=["mp4", "mov", "avi"])
    right = None
elif mode == "Stereo Pair":
    left_col, right_col = st.columns(2)
    with left_col: single = st.file_uploader("Left image", type=["png","jpg","jpeg"])
    with right_col: right = st.file_uploader("Right image", type=["png","jpg","jpeg"])
else:
    single = st.file_uploader("Upload RGB image", type=["png","jpg","jpeg"])
    right = None

if mode == "Video" and single:
    st.warning("Use the Video section in the README for batch processing. The interactive dashboard prioritizes image and stereo-pair inspection.")
elif single:
    rgb = upload_rgb(single)
    mono = depth_engine(model_id, device).predict(rgb)
    stereo = None
    if right:
        stereo = compute_stereo(rgb, upload_rgb(right), StereoSettings(focal, baseline, 0, disparities, block), calibrated=False)
        fused = fuse_depth(mono.raw_depth, stereo.depth_m, stereo.confidence, "confidence")
        display_depth = fused
        metric = False
        subtitle = "Approximate metric alignment — camera calibration and rectification unavailable"
    else:
        display_depth = mono.normalized_depth
        metric = False
        subtitle = "Relative monocular depth — not metric distance"
    detection_depth = display_depth if stereo else None
    detections = detector_engine(config["runtime"]["yolo_model"], mono.device).detect(rgb, detection_depth, threshold) if enable_yolo else []
    cards = st.columns(4)
    cards[0].metric("Depth inference", f"{mono.elapsed_ms:.0f} ms", mono.device.upper())
    cards[1].metric("Stereo depth", "Active" if stereo else "Inactive", "SGBM" if stereo else "single view")
    cards[2].metric("Fusion", "Confidence" if stereo else "N/A", "stereo + mono" if stereo else "relative depth")
    cards[3].metric("Objects", len(detections), f"{rgb.shape[1]} × {rgb.shape[0]}")
    st.caption(subtitle)
    panels = st.columns(4 if stereo else 2)
    with panels[0]: st.image(rgb, caption="Original RGB", use_container_width=True)
    with panels[1]: st.image(colorize_depth(mono.normalized_depth), caption="Monocular depth (relative)", use_container_width=True)
    if stereo:
        with panels[2]: st.image(colorize_disparity(stereo.disparity), caption="Stereo disparity (invalid = black)", use_container_width=True)
        with panels[3]: st.image(colorize_depth(normalize_for_display(display_depth)), caption="Confidence-aware fused depth", use_container_width=True)
    if enable_yolo:
        st.subheader("Object distance estimates")
        st.image(draw_detections(rgb, detections, metric), caption="Distances are approximate unless a valid metric calibration is used.", use_container_width=True)
        st.dataframe([{"Object": d.label, "Confidence": f"{d.confidence:.2f}", "Distance": f"~{d.distance_m:.2f} m" if d.distance_m else "Unavailable"} for d in detections], use_container_width=True, hide_index=True)
    if stereo:
        points, colors = rgbd_to_points(rgb, display_depth, focal, focal)
        if len(points):
            st.subheader("Interactive 3D point cloud")
            st.plotly_chart(cloud_figure(points, colors), use_container_width=True)
            if st.button("Export PLY"):
                destination = ROOT / "data" / "exports" / "fused_cloud.ply"; destination.parent.mkdir(parents=True, exist_ok=True)
                save_ply(destination, points, colors); st.success(f"Saved {destination.relative_to(ROOT)}")
else:
    st.markdown("### Ready for a scene\nUpload an RGB image for **relative monocular depth**, or a matched left/right pair for **approximate stereo fusion**. See README for calibration, video, evaluation, and dataset workflows.")
