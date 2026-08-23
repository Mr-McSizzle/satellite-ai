# sar_processor.py
import os
import json
import torch
import numpy as np
import rasterio
from skimage.filters import threshold_otsu, median
from skimage.morphology import disk
import segmentation_models_pytorch as smp

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
UNET_WEIGHTS_PATH = "./weights/sar_unet_water.pth"
META_PATH = "./weights/sar_benchmark_meta.json"

def get_sar_config():
    if os.path.exists(META_PATH):
        try:
            with open(META_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"active_method": "otsu", "detected_channels": 1}

SAR_CONFIG = get_sar_config()

def load_sar_unet():
    if SAR_CONFIG.get("active_method") == "unet" and os.path.exists(UNET_WEIGHTS_PATH):
        try:
            chans = SAR_CONFIG.get("detected_channels", 1)
            model = smp.Unet(encoder_name="resnet18", in_channels=chans, classes=1, activation=None)
            model.load_state_dict(torch.load(UNET_WEIGHTS_PATH, map_location=DEVICE))
            model.to(DEVICE)
            model.eval()
            return model
        except Exception as e:
            print(f"Warning: Failed to load U-Net ({e}), falling back to Otsu.")
            return None
    return None

SAR_UNET_MODEL = load_sar_unet()

def extract_sar_features(sar_geotiff_path: str, output_mask_path: str = "evidence_sar.tif") -> tuple[dict, str]:
    with rasterio.open(sar_geotiff_path) as src:
        profile = src.profile
        bands = src.read()
        sar_raw = bands[0].astype(np.float32)

    # 1. Clean data and Despeckle
    valid_mask = np.isfinite(sar_raw)
    min_val = np.nanmin(sar_raw) if np.any(valid_mask) else 0.0
    sar_clean = np.nan_to_num(sar_raw, nan=float(min_val))
    smoothed = median(sar_clean, disk(3))

    water_mask = None
    water_method = ""

    # 2. Extract Water (U-Net if benchmark won, else Otsu)
    if SAR_UNET_MODEL is not None and bands.shape[0] >= SAR_CONFIG.get("detected_channels", 1):
        try:
            if SAR_CONFIG.get("detected_channels") == 2 and bands.shape[0] >= 2:
                vv = np.clip((bands[0].astype(np.float32) + 25.0) / 25.0, 0, 1)
                vh = np.clip((bands[1].astype(np.float32) + 32.0) / 27.0, 0, 1)
                x_tensor = torch.from_numpy(np.stack([vv, vh], axis=0)).unsqueeze(0).to(DEVICE)
            else:
                vv = np.clip((bands[0].astype(np.float32) + 25.0) / 25.0, 0, 1)
                x_tensor = torch.from_numpy(vv).unsqueeze(0).unsqueeze(0).to(DEVICE)

            with torch.no_grad():
                logits = SAR_UNET_MODEL(x_tensor)
                probs = torch.sigmoid(logits).squeeze().cpu().numpy()
                water_mask = (probs > 0.5).astype(np.uint8)
            water_method = f"Trained U-Net (in_channels={SAR_CONFIG.get('detected_channels', 1)})"
        except Exception:
            water_thresh = threshold_otsu(smoothed)
            water_mask = (smoothed < water_thresh).astype(np.uint8)
            water_method = "Otsu Fallback"
    else:
        water_thresh = threshold_otsu(smoothed)
        water_mask = (smoothed < water_thresh).astype(np.uint8)
        water_method = "Otsu Baseline"

    # 3. Extract Built-up (Always use percentile thresholding)
    water_thresh_val = threshold_otsu(smoothed) # needed for indexing if U-Net was used
    urban_thresh = np.percentile(smoothed[smoothed >= water_thresh_val], 85) if np.any(smoothed >= water_thresh_val) else np.percentile(smoothed, 85)
    built_up_mask = (smoothed > urban_thresh).astype(np.uint8)

    # 4. Combine (0=BG, 1=Water, 2=Built-up)
    combined_mask = np.zeros_like(water_mask, dtype=np.uint8)
    combined_mask[water_mask == 1] = 1
    combined_mask[built_up_mask == 1] = 2

    profile.update(dtype=rasterio.uint8, count=1)
    with rasterio.open(output_mask_path, 'w', **profile) as dst:
        dst.write(combined_mask, 1)

    masks = {"water_mask": water_mask, "built_up_mask": built_up_mask, "combined_mask": combined_mask}
    method_used = f"Water: {water_method}, Built-Up: Double-Bounce Threshold"
    
    return masks, method_used