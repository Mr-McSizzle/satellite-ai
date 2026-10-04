"""
Radiometric harmonisation, quality masking and per-tile thematic statistics.

These are the false-alarm suppression primitives (PS 2.2.3):
  * SCL quality mask removes cloud, cloud-shadow, cirrus, snow, saturated and no-data pixels.
  * Processing-baseline offset correction harmonises reflectance across the 2022 L2A change.
  * A fixed (not per-image) display stretch keeps appearance comparable across dates.
  * Thematic statistics are computed as *fractions of valid pixels* within a 640 m cell,
    which is robust to sub-tile co-registration error and to partial cloud cover.
"""
from __future__ import annotations

import numpy as np

from . import config

# Sentinel-2 Scene Classification Layer classes
SCL_NODATA, SCL_SATURATED, SCL_DARK, SCL_SHADOW = 0, 1, 2, 3
SCL_VEG, SCL_BARE, SCL_WATER, SCL_UNCLASS = 4, 5, 6, 7
SCL_CLOUD_MED, SCL_CLOUD_HIGH, SCL_CIRRUS, SCL_SNOW = 8, 9, 10, 11

INVALID_SCL = {SCL_NODATA, SCL_SATURATED, SCL_SHADOW, SCL_CLOUD_MED, SCL_CLOUD_HIGH, SCL_CIRRUS, SCL_SNOW}
CLOUD_SCL = {SCL_SHADOW, SCL_CLOUD_MED, SCL_CLOUD_HIGH, SCL_CIRRUS}

BAND_INDEX = {"blue": 0, "green": 1, "red": 2, "nir": 3, "swir16": 4, "scl": 5}

# Thresholds for thematic fractions (on harmonised surface reflectance)
NDVI_VEG = 0.40
NDWI_WATER = 0.05      # McFeeters NDWI (green, nir)
NDBI_BUILT = 0.00      # NDBI (swir16, nir) with low NDVI
NDVI_BUILT_MAX = 0.25


def to_reflectance(stack_dn: np.ndarray, boa_offset: int) -> np.ndarray:
    """uint16 DN (bands x H x W, excluding SCL) -> float32 surface reflectance."""
    refl = (stack_dn.astype(np.float32) + float(boa_offset)) / 10000.0
    return np.clip(refl, 0.0, 1.5)


def valid_mask(scl: np.ndarray) -> np.ndarray:
    return ~np.isin(scl, list(INVALID_SCL))


def _nd(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (a - b) / (a + b)
    return np.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)


def indices(refl: np.ndarray) -> dict[str, np.ndarray]:
    b = BAND_INDEX
    ndvi = _nd(refl[b["nir"]], refl[b["red"]])
    ndwi = _nd(refl[b["green"]], refl[b["nir"]])
    ndbi = _nd(refl[b["swir16"]], refl[b["nir"]])
    return {"ndvi": ndvi, "ndwi": ndwi, "ndbi": ndbi}


def tile_stats(refl: np.ndarray, scl: np.ndarray) -> dict[str, float]:
    """Per-tile quality + thematic statistics over valid pixels only."""
    valid = valid_mask(scl)
    n = scl.size
    n_valid = int(valid.sum())
    stats = {
        "valid_frac": n_valid / n,
        "cloud_frac": float(np.isin(scl, list(CLOUD_SCL)).sum()) / n,
    }
    if n_valid < 0.05 * n:
        stats.update(ndvi=None, ndwi=None, ndbi=None, frac_veg=None, frac_water=None, frac_built=None, brightness=None)
        return stats

    idx = indices(refl)
    ndvi, ndwi, ndbi = idx["ndvi"][valid], idx["ndwi"][valid], idx["ndbi"][valid]
    water = (ndwi > NDWI_WATER) | (scl[valid] == SCL_WATER)
    veg = (ndvi > NDVI_VEG) & ~water
    built = (ndbi > NDBI_BUILT) & (ndvi < NDVI_BUILT_MAX) & ~water
    rgb = refl[[BAND_INDEX["red"], BAND_INDEX["green"], BAND_INDEX["blue"]]][:, valid]
    stats.update(
        ndvi=float(ndvi.mean()),
        ndwi=float(ndwi.mean()),
        ndbi=float(ndbi.mean()),
        frac_veg=float(veg.mean()),
        frac_water=float(water.mean()),
        frac_built=float(built.mean()),
        brightness=float(rgb.mean()),
    )
    return stats


def to_rgb8(refl: np.ndarray, scl: np.ndarray | None = None) -> np.ndarray:
    """Fixed-stretch true-colour uint8 (H x W x 3). Invalid pixels are greyed, not hidden."""
    b = BAND_INDEX
    rgb = np.stack([refl[b["red"]], refl[b["green"]], refl[b["blue"]]], axis=-1)
    rgb = np.clip(rgb / config.STRETCH_MAX_REFL, 0, 1) ** config.GAMMA
    out = (rgb * 255).astype(np.uint8)
    if scl is not None:
        bad = ~valid_mask(scl)
        out[bad] = (out[bad] * 0.35 + 90).astype(np.uint8)
    return out
