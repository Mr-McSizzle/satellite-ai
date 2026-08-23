import numpy as np
import rasterio
from typing import Optional

def compute_cloud_penalty(optical_path: str, mask: np.ndarray) -> float:
    with rasterio.open(optical_path) as src:
        optical = src.read()
    brightness = np.mean(optical, axis=0)
    cloud_pixels = brightness > 200
    
    overlap = np.logical_and(mask == 1, cloud_pixels).sum()
    total = (mask == 1).sum() + 1e-6
    return -0.20 if (overlap / total) > 0.3 else 0.0

def compute_terrain_penalty(dem_path: Optional[str], mask: np.ndarray) -> float:
    if not dem_path:
        return 0.0
    with rasterio.open(dem_path) as src:
        elevation = src.read(1)
    
    gy, gx = np.gradient(elevation)
    slope = np.sqrt(gx**2 + gy**2)
    steep_water = np.logical_and(mask == 1, slope > 15).sum()
    total_water = (mask == 1).sum() + 1e-6
    return -0.25 if (steep_water / total_water) > 0.2 else 0.0

def compute_iou(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    intersection = np.logical_and(mask_a == 1, mask_b == 1).sum()
    union = np.logical_or(mask_a == 1, mask_b == 1).sum() + 1e-6
    return float(intersection / union)