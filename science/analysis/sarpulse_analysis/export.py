"""Write analysis outputs: GeoTIFFs, web PNG overlays (EPSG:4326) and JSON."""

import json
import warnings
from pathlib import Path

import numpy as np
import rasterio
from rasterio.errors import NotGeoreferencedWarning
from rasterio.warp import Resampling, calculate_default_transform, reproject

from .change import CLASS_CODES, NODATA
from .stack import Grid

CLASS_COLORS = {
    "stable_land": None,  # transparent
    "water_gained": "#2166ac",
    "water_lost": "#e08214",
    "stable_water": "#92c5de",
    "ambiguous": "#bdbdbd",
}
HH_DISPLAY_RANGE_DB = (-25.0, 0.0)


def write_json(path: Path, doc) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_geotiff(path: Path, arr: np.ndarray, grid: Grid, nodata, tags: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": grid.height,
        "width": grid.width,
        "count": 1,
        "dtype": arr.dtype.name,
        "crs": f"EPSG:{grid.epsg}",
        "transform": grid.affine,
        "nodata": nodata,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)
        dst.update_tags(**{k: str(v) for k, v in tags.items()})


class WebProjector:
    """Reprojects grid rasters to EPSG:4326 for map overlays (e.g. a MapLibre image source)."""

    def __init__(self, grid: Grid):
        self.grid = grid
        x1 = grid.transform[2] + grid.width * grid.transform[0]
        y1 = grid.transform[5] + grid.height * grid.transform[4]
        self.transform, self.width, self.height = calculate_default_transform(
            f"EPSG:{grid.epsg}", "EPSG:4326", grid.width, grid.height, left=grid.transform[2], bottom=y1, right=x1, top=grid.transform[5]
        )
        w, n = self.transform @ (0, 0)
        e, s = self.transform @ (self.width, self.height)
        self.bounds = [round(w, 6), round(s, 6), round(e, 6), round(n, 6)]

    def warp(self, arr: np.ndarray, nodata) -> np.ndarray:
        dst = np.full((self.height, self.width), nodata, dtype=arr.dtype)
        reproject(
            arr,
            dst,
            src_transform=self.grid.affine,
            src_crs=f"EPSG:{self.grid.epsg}",
            src_nodata=nodata,
            dst_transform=self.transform,
            dst_crs="EPSG:4326",
            dst_nodata=nodata,
            resampling=Resampling.nearest,
        )
        return dst

    def image_coordinates(self) -> list[list[float]]:
        w, s, e, n = self.bounds
        return [[w, n], [e, n], [e, s], [w, s]]


def _hex(c: str) -> tuple[int, int, int]:
    return int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)


def write_png(path: Path, rgba: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Plain PNG overlay: georeferencing is carried by layers.json (bounds_wgs84).
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", NotGeoreferencedWarning)
        with rasterio.open(path, "w", driver="PNG", width=rgba.shape[2], height=rgba.shape[1], count=4, dtype="uint8") as dst:
            dst.write(rgba)


def classes_rgba(cls: np.ndarray, alpha: int = 200) -> np.ndarray:
    rgba = np.zeros((4,) + cls.shape, dtype=np.uint8)
    for name, code in CLASS_CODES.items():
        color = CLASS_COLORS[name]
        if color is None:
            continue
        m = cls == code
        for i, v in enumerate(_hex(color)):
            rgba[i][m] = v
        rgba[3][m] = alpha
    return rgba


def water_rgba(water: np.ndarray, color: str = "#2166ac", alpha: int = 200) -> np.ndarray:
    """water: uint8 1 water / 0 land / NODATA."""
    rgba = np.zeros((4,) + water.shape, dtype=np.uint8)
    m = water == 1
    for i, v in enumerate(_hex(color)):
        rgba[i][m] = v
    rgba[3][m] = alpha
    return rgba


def backscatter_rgba(db: np.ndarray, display_range=HH_DISPLAY_RANGE_DB) -> np.ndarray:
    """Greyscale HH dB with a fixed stretch so dates are visually comparable (not a photo)."""
    lo, hi = display_range
    ok = np.isfinite(db)
    grey = np.zeros(db.shape, dtype=np.uint8)
    grey[ok] = np.clip((db[ok] - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
    rgba = np.stack([grey, grey, grey, np.where(ok, 255, 0).astype(np.uint8)])
    return rgba


def legend() -> list[dict]:
    return [{"class": name, "code": code, "color": CLASS_COLORS[name]} for name, code in CLASS_CODES.items()] + [{"class": "nodata", "code": NODATA, "color": None}]
