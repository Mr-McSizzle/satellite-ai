"""Robust image loading for GAIA.

Browsers and PIL cannot decode most real satellite GeoTIFFs (16-bit, multi-band,
float). Every consumer (Gemini chat, browser preview, offline ingest) goes through
`load_rgb`, which returns an 8-bit RGB PIL image for any supported upload.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
from PIL import Image

# Sentinel-2 stacks staged by sentinel_index use [B, G, R, NIR, SWIR16, SCL].
_S2_STACK_RGB = (2, 1, 0)


def _stretch(band: np.ndarray, lo_pct: float = 2.0, hi_pct: float = 98.0) -> np.ndarray:
    band = band.astype(np.float32)
    finite = band[np.isfinite(band)]
    if finite.size == 0:
        return np.zeros(band.shape, dtype=np.uint8)
    lo, hi = np.percentile(finite, [lo_pct, hi_pct])
    if hi <= lo:
        hi = lo + 1.0
    out = np.clip((band - lo) / (hi - lo), 0.0, 1.0) * 255.0
    return np.nan_to_num(out).astype(np.uint8)


def _load_with_rasterio(path: Path) -> Image.Image:
    import rasterio

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # NotGeoreferencedWarning on plain TIFFs
        with rasterio.open(path) as src:
            count = src.count
            if count >= 6:
                idx = [i + 1 for i in _S2_STACK_RGB]
            elif count >= 3:
                idx = [1, 2, 3]
            else:
                idx = [1, 1, 1]  # single band (e.g. SAR) -> greyscale
            data = src.read(idx)
            dtype = src.dtypes[0]

    if dtype == "uint8":
        rgb = np.transpose(data, (1, 2, 0))
    else:
        rgb = np.dstack([_stretch(b) for b in data])
    return Image.fromarray(np.ascontiguousarray(rgb), mode="RGB")


def load_rgb(path: str | Path) -> Image.Image:
    """Open any PNG/JPG/TIFF/GeoTIFF as an 8-bit RGB image."""
    path = Path(path)
    if path.suffix.lower() in {".tif", ".tiff"}:
        try:
            return _load_with_rasterio(path)
        except Exception:
            pass  # fall back to PIL for exotic TIFFs rasterio can't read
    with Image.open(path) as im:
        im.load()
        if im.mode in ("I;16", "I;16B", "I", "F"):
            arr = _stretch(np.asarray(im))
            return Image.fromarray(arr).convert("RGB")
        return im.convert("RGB")


def make_preview(path: str | Path, out_path: str | Path, max_side: int = 1600) -> Path:
    """Write a browser-displayable PNG preview next to the upload."""
    img = load_rgb(path)
    img.thumbnail((max_side, max_side))
    out_path = Path(out_path)
    img.save(out_path, format="PNG")
    return out_path
