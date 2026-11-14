"""Build an analysis-ready (ARD) stack: every scene resampled onto one shared AOI grid.

Backscatter stays in physical units (gamma-0 linear power). Multilooking averages
k x k native pixels in linear power and is only valid where all k x k inputs are valid,
so no edge or masked pixel is silently filled.
"""

import json
from contextlib import AbstractContextManager
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import h5py
import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.transform import Affine
from rasterio.warp import Resampling, reproject

from . import __version__
from .aoi import AOI, Grid, aoi_grid, grid_bbox_wgs84
from .catalog import CandidateScene
from .comparability import Stack
from .gcov import GcovSubset, noise_equivalent_backscatter_db, read_grid, read_identification, read_subset, window_for_bounds

SCHEMA_VERSION = "sarpulse.ard_stack.v0"
SYNTHETIC = "SYNTHETIC/DEMO — NOT NASA OBSERVATIONS"
OBSERVED = "observed"
TERMS = ("HHHH", "HVHV")
UNITS = {
    "HHHH": "gamma-0 RTC backscatter, linear power (unitless); HH polarization",
    "HVHV": "gamma-0 RTC backscatter, linear power (unitless); HV polarization",
    "valid": "1 = valid in every term, 0 = invalid / outside acquisition",
    "number_of_looks": "number of radar looks averaged per output pixel (sum over multilook block)",
}
NISAR_LICENSE = "NASA Earth Science open data policy; cite NASA/JPL-Caltech NISAR and ASF DAAC"
MIN_VALID_FRACTION = 0.5

Opener = Callable[[CandidateScene], AbstractContextManager]


def _north_up(sub: GcovSubset) -> GcovSubset:
    if sub.dy < 0:
        return sub
    flip = lambda a: None if a is None else a[::-1]  # noqa: E731
    return GcovSubset(
        terms={k: v[::-1] for k, v in sub.terms.items()},
        valid=sub.valid[::-1],
        number_of_looks=flip(sub.number_of_looks),
        x=sub.x,
        y=sub.y[::-1],
        dx=sub.dx,
        dy=-sub.dy,
        epsg=sub.epsg,
        receive_only_terms=sub.receive_only_terms,
    )


def _aligned_factor(sub: GcovSubset, grid: Grid) -> tuple[int, int, int] | None:
    """(k, row_offset, col_offset) if native pixels nest exactly inside grid pixels."""
    if sub.epsg != grid.epsg or not np.isclose(abs(sub.dx), abs(sub.dy)):
        return None
    k = grid.spacing / abs(sub.dx)
    if not np.isclose(k, round(k)) or round(k) < 1:
        return None
    left = sub.x[0] - abs(sub.dx) / 2
    top = sub.y[0] + abs(sub.dy) / 2
    col_off = (left - grid.x0) / abs(sub.dx)
    row_off = (grid.y0 - top) / abs(sub.dy)
    if not (np.isclose(col_off, round(col_off), atol=1e-3) and np.isclose(row_off, round(row_off), atol=1e-3)):
        return None
    return round(k), round(row_off), round(col_off)


def _place(arr: np.ndarray, shape: tuple[int, int], row_off: int, col_off: int, fill) -> np.ndarray:
    out = np.full(shape, fill, dtype=arr.dtype)
    r0, c0 = max(row_off, 0), max(col_off, 0)
    sr0, sc0 = max(-row_off, 0), max(-col_off, 0)
    h = min(shape[0] - r0, arr.shape[0] - sr0)
    w = min(shape[1] - c0, arr.shape[1] - sc0)
    if h > 0 and w > 0:
        out[r0 : r0 + h, c0 : c0 + w] = arr[sr0 : sr0 + h, sc0 : sc0 + w]
    return out


def _block(arr: np.ndarray, k: int, reducer) -> np.ndarray:
    h, w = arr.shape[0] // k, arr.shape[1] // k
    return reducer(arr[: h * k, : w * k].reshape(h, k, w, k), axis=(1, 3))


def resample_to_grid(sub: GcovSubset, grid: Grid) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray | None, str]:
    """Return (terms, valid, number_of_looks, method) on `grid`."""
    sub = _north_up(sub)
    aligned = _aligned_factor(sub, grid)
    if aligned:
        k, row_off, col_off = aligned
        shape = (grid.height * k, grid.width * k)
        # NaN propagates through mean, so any invalid native pixel invalidates its block.
        terms = {t: _block(_place(a, shape, row_off, col_off, np.nan), k, np.mean) for t, a in sub.terms.items()}
        nlooks = None
        if sub.number_of_looks is not None:
            nlooks = _block(_place(sub.number_of_looks, shape, row_off, col_off, np.nan), k, np.sum)
        method = f"exact {k}x{k} block average of linear power (all inputs valid)"
    else:
        src_transform = Affine(abs(sub.dx), 0, sub.x[0] - abs(sub.dx) / 2, 0, -abs(sub.dy), sub.y[0] + abs(sub.dy) / 2)
        dst_transform = Affine(*grid.transform)

        def warp(a: np.ndarray, how: Resampling) -> np.ndarray:
            dst = np.full((grid.height, grid.width), np.nan, dtype=np.float32)
            reproject(
                a.astype(np.float32),
                dst,
                src_transform=src_transform,
                src_crs=f"EPSG:{sub.epsg}",
                src_nodata=np.nan,
                dst_transform=dst_transform,
                dst_crs=f"EPSG:{grid.epsg}",
                dst_nodata=np.nan,
                resampling=how,
            )
            return dst

        terms = {t: warp(a, Resampling.average) for t, a in sub.terms.items()}
        frac_valid = warp(sub.valid.astype(np.float32), Resampling.average)
        for a in terms.values():
            a[~(frac_valid > 0.999)] = np.nan
        nlooks = warp(sub.number_of_looks, Resampling.average) if sub.number_of_looks is not None else None
        method = "rasterio average reprojection of linear power (grid not nested)"

    valid = np.logical_and.reduce([np.isfinite(a) & (a > 0) for a in terms.values()])
    for a in terms.values():
        a[~valid] = np.nan
    if nlooks is not None:
        nlooks[~valid] = np.nan
    return {t: a.astype(np.float32) for t, a in terms.items()}, valid, nlooks, method


def write_geotiff(path: Path, arr: np.ndarray, grid: Grid, nodata, tags: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": grid.height,
        "width": grid.width,
        "count": 1,
        "dtype": arr.dtype.name,
        "crs": f"EPSG:{grid.epsg}",
        "transform": Affine(*grid.transform),
        "nodata": nodata,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)
        dst.update_tags(**{k: str(v) for k, v in tags.items()})


def scene_record(c: CandidateScene, grid: Grid, data_status: str, acquired_utc: str) -> dict:
    """Scene record matching the draft API `Scene` schema (api/app/schemas.py)."""
    return {
        "scene_id": c.scene_id,
        "source": f"NASA/JPL NISAR L2 GCOV via ASF DAAC ({c.collection})",
        "acquired_at_utc": acquired_utc,
        "maturity": c.maturity,
        "crid": c.crid,
        "orbit_direction": c.direction,
        "relative_orbit": c.track,
        "polarizations": list(TERMS),
        "grid_epsg": grid.epsg,
        "pixel_spacing_m": grid.spacing,
        "footprint": c.footprint_bbox,
        "license": NISAR_LICENSE,
        "data_url": c.url,
        "data_status": data_status,
    }


def _utc_from_ident(ident: dict, fallback: str) -> str:
    t = ident.get("zeroDopplerStartTime")
    if not t:
        return fallback
    return t.split(".")[0] + "Z" if not t.endswith("Z") else t


def _parse_utc(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def build_ard_stack(stack: Stack, aoi: AOI, out_dir: Path, opener: Opener, multilook: int = 2) -> dict:
    out_dir = Path(out_dir)
    grid: Grid | None = None
    records, excluded = [], []
    statuses = set()

    for c in stack.scenes:
        with opener(c) as src, h5py.File(src, "r") as h5:
            ident = read_identification(h5)
            status = SYNTHETIC if h5.attrs.get("sarpulse_synthetic") else OBSERVED
            gg = read_grid(h5)
            if grid is None:
                grid = aoi_grid(aoi, gg.epsg, abs(gg.dx) * multilook)
            x1 = grid.x0 + grid.width * grid.spacing
            y1 = grid.y0 - grid.height * grid.spacing
            if gg.epsg != grid.epsg:
                tr = Transformer.from_crs(f"EPSG:{grid.epsg}", f"EPSG:{gg.epsg}", always_xy=True)
                bounds = tr.transform_bounds(grid.x0, y1, x1, grid.y0, densify_pts=21)
            else:
                bounds = (grid.x0, y1, x1, grid.y0)
            window = window_for_bounds(gg, *bounds)
            if window is None:
                excluded.append({"scene_id": c.scene_id, "reason": "product grid does not overlap AOI"})
                continue
            sub = read_subset(h5, gg, window, TERMS)
            nesb = noise_equivalent_backscatter_db(h5)

        if sub.receive_only_terms:
            excluded.append({"scene_id": c.scene_id, "reason": f"receive-only (noise) channels: {sub.receive_only_terms}"})
            continue
        terms, valid, nlooks, method = resample_to_grid(sub, grid)
        valid_fraction = float(valid.mean())
        if valid_fraction < MIN_VALID_FRACTION:
            excluded.append({"scene_id": c.scene_id, "reason": f"only {valid_fraction:.1%} of AOI valid"})
            continue

        warnings = []
        if ident.get("granuleId") and ident["granuleId"].removesuffix(".h5") != c.scene_id:
            warnings.append(f"identification/granuleId {ident['granuleId']} differs from catalogue name")
        if ident.get("compositeReleaseId") and ident["compositeReleaseId"] != c.crid:
            warnings.append(f"identification/compositeReleaseId {ident['compositeReleaseId']} differs from catalogue CRID")

        acquired = _utc_from_ident(ident, c.start_utc)
        if abs((_parse_utc(acquired) - _parse_utc(c.start_utc)).total_seconds()) > 60:
            warnings.append(f"identification start {acquired} differs from catalogue start {c.start_utc}")
        scene_dir = out_dir / "ard" / c.scene_id
        tags = {"scene_id": c.scene_id, "acquired_at_utc": acquired, "data_status": status}
        files = {}
        for t, a in terms.items():
            write_geotiff(scene_dir / f"{t}.tif", a, grid, np.nan, {**tags, "units": UNITS[t]})
            files[t] = f"ard/{c.scene_id}/{t}.tif"
        write_geotiff(scene_dir / "valid.tif", valid.astype(np.uint8), grid, None, {**tags, "units": UNITS["valid"]})
        files["valid"] = f"ard/{c.scene_id}/valid.tif"
        if nlooks is not None:
            write_geotiff(scene_dir / "number_of_looks.tif", nlooks, grid, np.nan, {**tags, "units": UNITS["number_of_looks"]})
            files["number_of_looks"] = f"ard/{c.scene_id}/number_of_looks.tif"

        statuses.add(status)
        records.append(
            {
                "scene_id": c.scene_id,
                "acquired_at_utc": acquired,
                "files": files,
                "valid_fraction": round(valid_fraction, 4),
                "resampling": method,
                "noise_equivalent_backscatter_db_median": nesb,
                "warnings": warnings,
                "identification": ident,
                "catalogue": c.to_dict(),
                "scene": scene_record(c, grid, status, acquired),
                "data_status": status,
            }
        )

    if grid is None or len(records) < 2:
        raise RuntimeError(f"Fewer than two usable scenes for {stack.stack_id}: excluded={excluded}")

    data_status = OBSERVED if statuses == {OBSERVED} else SYNTHETIC
    doc = {
        "schema_version": SCHEMA_VERSION,
        "aoi": {"id": aoi.id, "name": aoi.name, "bbox": aoi.bbox()},
        "stack_id": stack.stack_id,
        "comparability_key": stack.key,
        "comparability_warnings": stack.warnings,
        "grid": grid.to_dict(),
        "grid_bbox_wgs84": grid_bbox_wgs84(grid),
        "units": UNITS,
        "data_status": data_status,
        "processing": {
            "software": f"sarpulse_ingest {__version__}",
            "multilook": multilook,
            "valid_rule": "GCOV mask in 1..5, inputDataExceptionMask == 0, finite and > 0 in HHHH and HVHV",
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        },
        "scenes": sorted(records, key=lambda r: r["acquired_at_utc"]),
        "excluded_scenes": excluded,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "stack.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    (out_dir / "scenes.json").write_text(json.dumps([r["scene"] for r in doc["scenes"]], indent=2), encoding="utf-8")
    return doc
