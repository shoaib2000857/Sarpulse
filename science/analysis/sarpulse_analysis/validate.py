"""Accuracy assessment of a water map against an independent reference.

Metrics are only produced from a reference the user supplies (labelled points or a
reference water raster, e.g. a same-day cloud-free optical water mask). This module
never fabricates a reference, and a missing reference yields "not validated".
"""

import json
import math
from pathlib import Path

import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.warp import Resampling, reproject

from .stack import Grid


def wilson_interval(successes: int, n: int, z: float = 1.96) -> list[float] | None:
    if n == 0:
        return None
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return [round(centre - half, 4), round(centre + half, 4)]


def binary_metrics(pred: np.ndarray, ref: np.ndarray) -> dict:
    """Confusion matrix and summary metrics; water is the positive class."""
    pred, ref = pred.astype(bool), ref.astype(bool)
    tp = int(np.sum(pred & ref))
    fp = int(np.sum(pred & ~ref))
    fn = int(np.sum(~pred & ref))
    tn = int(np.sum(~pred & ~ref))
    n = tp + fp + fn + tn

    def ratio(a, b):
        return round(a / b, 4) if b else None

    oa = ratio(tp + tn, n)
    pe = ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / (n * n) if n else 0
    kappa = round(((tp + tn) / n - pe) / (1 - pe), 4) if n and pe < 1 else None
    precision, recall = ratio(tp, tp + fp), ratio(tp, tp + fn)
    f1 = ratio(2 * tp, 2 * tp + fp + fn)
    return {
        "n": n,
        "confusion_matrix": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "overall_accuracy": oa,
        "overall_accuracy_95ci": wilson_interval(tp + tn, n),
        "precision_water": precision,
        "recall_water": recall,
        "f1_water": f1,
        "iou_water": ratio(tp, tp + fp + fn),
        "cohens_kappa": kappa,
    }


def reference_from_points(path: Path, grid: Grid, label_field: str = "water") -> tuple[np.ndarray, np.ndarray]:
    """Grid indices (shape (2, n): rows, cols) and boolean labels for labelled GeoJSON points on the grid."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{grid.epsg}", always_xy=True)
    inv = ~grid.affine
    rows, cols, labels = [], [], []
    for f in doc["features"]:
        if f["geometry"]["type"] != "Point" or label_field not in f["properties"]:
            continue
        x, y = tr.transform(*f["geometry"]["coordinates"][:2])
        c, r = inv @ (x, y)
        r, c = int(math.floor(r)), int(math.floor(c))
        if 0 <= r < grid.height and 0 <= c < grid.width:
            rows.append(r)
            cols.append(c)
            label = f["properties"][label_field]
            if not isinstance(label, bool) and (not isinstance(label, (int, float)) or label not in (0, 1)):
                raise ValueError(f"Reference labels must be boolean or 0/1; got {label!r}")
            labels.append(bool(label))
    return np.array([rows, cols], dtype=int), np.array(labels, dtype=bool)


def reference_from_raster(path: Path, grid: Grid, water_values: set[int]) -> np.ndarray:
    """Reference raster resampled (nearest) onto the analysis grid; -1 = no reference."""
    dst = np.full((grid.height, grid.width), -1, dtype=np.int32)
    with rasterio.open(path) as src:
        data = src.read(1, masked=True)
        ref = np.where(np.isin(data, list(water_values)), 1, 0).astype(np.int32)
        ref[np.ma.getmaskarray(data) | ~np.isfinite(np.asarray(data))] = -1
        reproject(
            ref,
            dst,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=-1,
            dst_transform=grid.affine,
            dst_crs=f"EPSG:{grid.epsg}",
            dst_nodata=-1,
            resampling=Resampling.nearest,
        )
    return dst


def validate_water_map(water: np.ndarray, valid: np.ndarray, grid: Grid, reference: Path, reference_kind: str, water_values=(1,), label_field="water") -> dict:
    if reference_kind == "points":
        idx, labels = reference_from_points(reference, grid, label_field)
        keep = valid[idx[0], idx[1]] if idx.size else np.array([], dtype=bool)
        metrics = binary_metrics(water[idx[0], idx[1]][keep], labels[keep]) if idx.size else binary_metrics(np.array([]), np.array([]))
        metrics["n_reference_points_outside_valid_area"] = int((~keep).sum()) if idx.size else 0
    elif reference_kind == "raster":
        ref = reference_from_raster(reference, grid, set(water_values))
        m = valid & (ref >= 0)
        metrics = binary_metrics(water[m], ref[m] == 1)
    else:
        raise ValueError("reference_kind must be 'points' or 'raster'")
    return metrics
