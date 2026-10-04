"""
Phase 0 — Stage public Sentinel-2 L2A imagery for an AOI to local GeoTIFFs.

This is the ONLY component that touches the network. Run it once while online;
everything downstream (ingest, index, search, change) reads the local archive.

Source : Element84 Earth Search STAC (public, no auth) -> Copernicus Sentinel-2 L2A COGs
Licence: Copernicus Sentinel data, free & open (see PROVENANCE.md)

Usage:
    python -m sentinel_index.stage_data --aoi navi_mumbai --start 2017-01-01 --end 2025-12-31
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

STAC_URL = "https://earth-search.aws.element84.com/v1"
COLLECTION = "sentinel-2-l2a"

# Band order of every staged GeoTIFF. SCL = Sen2Cor scene classification (quality mask).
BANDS = ["blue", "green", "red", "nir", "swir16", "scl"]

AOIS = {
    # lon_min, lat_min, lon_max, lat_max (EPSG:4326)
    "navi_mumbai": (73.030, 18.960, 73.100, 19.025),
}

ARCHIVE_DIR = Path(__file__).resolve().parents[1] / "data" / "archive"


def pick_items(bbox, start, end, max_cloud, per_year):
    from pystac_client import Client

    client = Client.open(STAC_URL)
    search = client.search(
        collections=[COLLECTION],
        bbox=bbox,
        datetime=f"{start}/{end}",
        query={"eo:cloud_cover": {"lt": max_cloud}},
        max_items=1000,
    )
    items = list(search.items())
    if not items:
        raise SystemExit("No scenes found for AOI/time window.")

    # Keep a single MGRS tile so every scene shares one pixel grid.
    tile_of = lambda it: it.properties.get("grid:code") or it.properties.get("s2:mgrs_tile")
    tile = Counter(tile_of(i) for i in items).most_common(1)[0][0]
    items = [i for i in items if tile_of(i) == tile]

    # Spread across the timeline: per year, take the clearest scenes in
    # dry season (Jan-May) and post-monsoon (Oct-Dec) so we have season-matched pairs.
    by_bucket: dict[tuple, list] = {}
    for it in items:
        dt = it.datetime
        season = "dry" if dt.month <= 5 else ("post" if dt.month >= 10 else "monsoon")
        if season == "monsoon":
            continue
        by_bucket.setdefault((dt.year, season), []).append(it)

    chosen = []
    for key in sorted(by_bucket):
        best = sorted(by_bucket[key], key=lambda i: i.properties["eo:cloud_cover"])[: max(1, per_year // 2)]
        chosen.extend(best)
    return tile, sorted(chosen, key=lambda i: i.datetime)


def stage_item(item, bbox, out_dir: Path) -> Path | None:
    out = out_dir / f"{item.id}.tif"
    if out.exists():
        return out

    ref_href = item.assets["red"].href
    with rasterio.open(ref_href) as ref:
        dst_bounds = transform_bounds("EPSG:4326", ref.crs, *bbox)
        win = from_bounds(*dst_bounds, transform=ref.transform).round_offsets().round_lengths()
        transform = ref.window_transform(win)
        h, w = int(win.height), int(win.width)
        crs = ref.crs

    stack = np.zeros((len(BANDS), h, w), dtype=np.uint16)
    for bi, band in enumerate(BANDS):
        with rasterio.open(item.assets[band].href) as src:
            bwin = from_bounds(*dst_bounds, transform=src.transform)
            stack[bi] = src.read(
                1,
                window=bwin,
                out_shape=(h, w),
                resampling=Resampling.nearest if band == "scl" else Resampling.bilinear,
                boundless=True,
                fill_value=0,
            )

    profile = dict(
        driver="GTiff", height=h, width=w, count=len(BANDS), dtype="uint16",
        crs=crs, transform=transform, compress="deflate", tiled=True,
        blockxsize=256, blockysize=256,
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out, "w", **profile) as dst:
        dst.write(stack)
        for i, b in enumerate(BANDS, start=1):
            dst.set_band_description(i, b)
        dst.update_tags(
            ACQUISITION_DATETIME=item.datetime.isoformat(),
            PLATFORM=item.properties.get("platform", "sentinel-2"),
            SENSOR="MSI",
            PRODUCT="S2_L2A",
            SCENE_ID=item.id,
            CLOUD_COVER=str(item.properties.get("eo:cloud_cover")),
            MGRS_TILE=str(item.properties.get("grid:code") or item.properties.get("s2:mgrs_tile")),
            SOURCE_STAC=f"{STAC_URL}/collections/{COLLECTION}/items/{item.id}",
            SOURCE_HREF_RED=ref_href,
            BANDS=",".join(BANDS),
            PROCESSING_BASELINE=str(item.properties.get("s2:processing_baseline", "")),
            # Baseline >= 04.00 (Jan 2022+) adds +1000 DN to L2A BOA reflectance.
            BOA_ADD_OFFSET=str(-1000 if _baseline(item) >= 4.0 else 0),
        )
    return out


def _baseline(item) -> float:
    try:
        return float(item.properties.get("s2:processing_baseline", "0"))
    except ValueError:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aoi", default="navi_mumbai", choices=list(AOIS))
    ap.add_argument("--start", default="2017-01-01")
    ap.add_argument("--end", default="2025-12-31")
    ap.add_argument("--max-cloud", type=float, default=15)
    ap.add_argument("--per-year", type=int, default=2)
    ap.add_argument("--out", type=Path, default=ARCHIVE_DIR)
    args = ap.parse_args()

    bbox = AOIS[args.aoi]
    tile, items = pick_items(bbox, args.start, args.end, args.max_cloud, args.per_year)
    print(f"[stage] AOI={args.aoi} tile={tile} scenes={len(items)}")

    manifest = []
    for it in items:
        try:
            path = stage_item(it, bbox, args.out)
            print(f"[stage] {it.datetime.date()}  cloud={it.properties['eo:cloud_cover']:.1f}%  -> {path.name}")
            manifest.append({"scene_id": it.id, "datetime": it.datetime.isoformat(), "path": str(path)})
        except Exception as e:  # keep going; one bad COG shouldn't stop staging
            print(f"[stage] FAILED {it.id}: {e}")

    (args.out / f"manifest_{args.aoi}.json").write_text(json.dumps({"aoi": args.aoi, "bbox": bbox, "tile": tile, "scenes": manifest}, indent=2))


if __name__ == "__main__":
    main()
