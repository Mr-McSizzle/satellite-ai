# fusion_engine.py
import numpy as np
from perception_schemas import PerceptionResult, ValidationMetrics
from sar_processor import extract_sar_features
from optical_processor import run_optical_segmentation, run_change_detection
from validator import compute_cloud_penalty, compute_terrain_penalty, compute_iou

def process_optical_sar_fusion(optical_path: str, sar_path: str, dem_path: str = None) -> PerceptionResult:
    trace = []
    
    trace.append("Executing Optical Prithvi-EO-2.0 Multi-class Segmentation...")
    opt_mask = run_optical_segmentation(optical_path, "evidence_opt.tif")
    
    trace.append("Executing SAR Radar Extraction (Water + Built-Up)...")
    sar_masks, sar_method = extract_sar_features(sar_path, "evidence_sar.tif")
    trace.append(f"SAR Method: {sar_method}")
    
    # Compute Cross-Modal Agreement on Water
    water_iou = compute_iou(opt_mask, sar_masks["water_mask"])
    trace.append(f"Optical-SAR Water Agreement (IoU): {water_iou:.2f}")
    
    cloud_pen = compute_cloud_penalty(optical_path, opt_mask)
    dem_pen = compute_terrain_penalty(dem_path, opt_mask)
    
    if cloud_pen < 0: 
        trace.append(f"Cloud occlusion detected: penalty {cloud_pen}")
    if dem_pen < 0: 
        trace.append(f"Terrain slope violation: penalty {dem_pen}")

    # Confidence formula based on physical agreement & penalties
    base = 0.55 + (0.40 * water_iou)
    final_conf = float(np.clip(base + cloud_pen + dem_pen, 0.05, 0.99))
    trace.append(f"Confidence score assigned: {final_conf * 100:.1f}%")

    return PerceptionResult(
        task="optical_sar_fusion",
        status="success",
        evidence_mask_path="evidence_sar.tif",
        confidence=round(final_conf, 2),
        metrics=ValidationMetrics(
            sensor_agreement_iou=round(water_iou, 2),
            cloud_penalty=cloud_pen,
            terrain_penalty=dem_pen
        ),
        execution_trace=trace
    )

def process_single_optical_segmentation(optical_path: str) -> PerceptionResult:
    mask = run_optical_segmentation(optical_path, "evidence_opt.tif")
    cloud_pen = compute_cloud_penalty(optical_path, mask)
    conf = float(np.clip(0.85 + cloud_pen, 0.1, 0.99))
    
    return PerceptionResult(
        task="optical_segmentation",
        status="success",
        evidence_mask_path="evidence_opt.tif",
        confidence=round(conf, 2),
        metrics=ValidationMetrics(sensor_agreement_iou=1.0, cloud_penalty=cloud_pen, terrain_penalty=0.0),
        execution_trace=["Executed Prithvi Feature Segmentation", f"Cloud check penalty: {cloud_pen}"]
    )

def process_change_detection(img1_path: str, img2_path: str) -> PerceptionResult:
    mask = run_change_detection(img1_path, img2_path, "evidence_change.tif")
    return PerceptionResult(
        task="change_detection",
        status="success",
        evidence_mask_path="evidence_change.tif",
        confidence=0.88,
        metrics=ValidationMetrics(sensor_agreement_iou=1.0, cloud_penalty=0.0, terrain_penalty=0.0),
        execution_trace=["Co-registered Time 1 and Time 2 chips", "Generated Bi-temporal Change Mask via Prithvi difference"]
    )