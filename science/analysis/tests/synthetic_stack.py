"""Write small analysis-ready stacks (sarpulse.ard_stack.v0) for tests.

SYNTHETIC/DEMO — NOT NASA OBSERVATIONS. Backscatter is simulated as gamma-distributed
speckle around made-up land/water levels so the classifier is exercised realistically.
"""

import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine

SYNTHETIC = "SYNTHETIC/DEMO — NOT NASA OBSERVATIONS"
EPSG = 32646
SPACING = 20.0
X0, Y0 = 600_000.0, 2_980_000.0  # UTM 46N, about 94.0E 26.9N
LAND_HH_DB, WATER_HH_DB = -8.0, -22.0
LAND_HV_DB, WATER_HV_DB = -15.0, -29.0


def speckled(mean_db: np.ndarray, looks: int, rng) -> np.ndarray:
    mean = 10 ** (mean_db / 10)
    return (mean * rng.gamma(looks, 1.0 / looks, mean.shape)).astype(np.float32)


def _write(path: Path, arr: np.ndarray, nodata) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        path, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1, dtype=arr.dtype.name,
        crs=f"EPSG:{EPSG}", transform=Affine(SPACING, 0, X0, 0, -SPACING, Y0), nodata=nodata,
    ) as dst:
        dst.write(arr, 1)


def write_stack(root: Path, water_masks: list[np.ndarray], dates: list[str], looks: int = 8, seed: int = 0, invalid: np.ndarray | None = None) -> Path:
    """One scene per (water_mask, date). Returns the stack.json path."""
    rng = np.random.default_rng(seed)
    h, w = water_masks[0].shape
    scenes = []
    for water, date in zip(water_masks, dates):
        sid = f"SYNTHETIC_GCOV_{date.replace('-', '')}"
        hh = speckled(np.where(water, WATER_HH_DB, LAND_HH_DB), looks, rng)
        hv = speckled(np.where(water, WATER_HV_DB, LAND_HV_DB), looks, rng)
        valid = np.ones((h, w), dtype=np.uint8)
        if invalid is not None:
            valid[invalid] = 0
            hh[invalid] = np.nan
            hv[invalid] = np.nan
        files = {t: f"ard/{sid}/{t}.tif" for t in ("HHHH", "HVHV", "valid")}
        _write(root / files["HHHH"], hh, np.nan)
        _write(root / files["HVHV"], hv, np.nan)
        _write(root / files["valid"], valid, None)
        scenes.append(
            {
                "scene_id": sid,
                "acquired_at_utc": f"{date}T23:05:28Z",
                "files": files,
                "data_status": SYNTHETIC,
                "scene": {"scene_id": sid, "maturity": "SYNTHETIC", "data_status": SYNTHETIC, "acquired_at_utc": f"{date}T23:05:28Z"},
            }
        )
    doc = {
        "schema_version": "sarpulse.ard_stack.v0",
        "aoi": {"id": "synthetic-aoi", "name": "Synthetic test AOI", "bbox": {"west": 94.0, "south": 26.9, "east": 94.1, "north": 27.0}},
        "stack_id": "SYNTHETIC_STACK",
        "comparability_key": {},
        "comparability_warnings": [],
        "grid": {"crs": f"EPSG:{EPSG}", "epsg": EPSG, "transform": [SPACING, 0.0, X0, 0.0, -SPACING, Y0], "width": w, "height": h, "pixel_spacing_m": SPACING},
        "data_status": SYNTHETIC,
        "processing": {"software": "tests"},
        "scenes": scenes,
        "excluded_scenes": [],
    }
    root.mkdir(parents=True, exist_ok=True)
    path = root / "stack.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def river_masks(h: int = 256, w: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """A river (before) that widens and floods a rectangular plain (after)."""
    before = np.zeros((h, w), dtype=bool)
    before[:, 100:130] = True
    after = before.copy()
    after[40:140, 130:200] = True  # 100 x 70 px flooded
    return before, after
