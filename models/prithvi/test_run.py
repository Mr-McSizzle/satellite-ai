# test_run.py
import numpy as np
import rasterio
from rasterio.transform import from_origin
from fusion_engine import process_optical_sar_fusion

transform = from_origin(0, 0, 10, 10)
dummy_optical = np.random.randint(0, 255, (4, 128, 128), dtype=np.uint8)
# 2 Channels: Band 1 (VV), Band 2 (VH)
dummy_sar = np.random.randint(0, 255, (2, 128, 128), dtype=np.uint8)

with rasterio.open("test_opt.tif", "w", driver="GTiff", height=128, width=128, count=4, dtype="uint8", transform=transform) as dst:
    dst.write(dummy_optical)

with rasterio.open("test_sar.tif", "w", driver="GTiff", height=128, width=128, count=2, dtype="uint8", transform=transform) as dst:
    dst.write(dummy_sar)

result = process_optical_sar_fusion("test_opt.tif", "test_sar.tif")
print("\n=== PERSON 2 PIPELINE (UPGRADED WITH SAR U-NET) ===")
print(result.model_dump_json(indent=2))