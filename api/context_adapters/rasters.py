"""Windowed reads of public global rasters (EPSG:4326) and point sampling.

Sources (no credentials needed):
- Copernicus DEM GLO-30 COGs on AWS Open Data (1x1 degree tiles)
- EC JRC Global Surface Water v1.4 occurrence (10x10 degree tiles, 1984-2021)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

COP_DEM_URL = (
    "https://copernicus-dem-30m.s3.amazonaws.com/"
    "Copernicus_DSM_COG_10_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM/"
    "Copernicus_DSM_COG_10_{ns}{lat:02d}_00_{ew}{lon:03d}_00_DEM.tif"
)
JRC_OCC_URL = (
    "https://storage.googleapis.com/global-surface-water/downloads2021/occurrence/"
    "occurrence_{lon}{ew}_{lat}{ns}v1_4_2021.tif"
)
JRC_NODATA = 255


@dataclass
class GeoArray:
    """A north-up EPSG:4326 array. transform = (west, xres, north, yres>0)."""

    data: np.ndarray
    west: float
    north: float
    xres: float
    yres: float

    def sample(self, lon: float, lat: float):
        col = int(math.floor((lon - self.west) / self.xres))
        row = int(math.floor((self.north - lat) / self.yres))
        if 0 <= row < self.data.shape[0] and 0 <= col < self.data.shape[1]:
            v = self.data[row, col]
            return None if not np.isfinite(v) else float(v)
        return None


def dem_tile_urls(west: float, south: float, east: float, north: float) -> list[str]:
    urls = []
    for lat in range(math.floor(south), math.ceil(north)):
        for lon in range(math.floor(west), math.ceil(east)):
            urls.append(COP_DEM_URL.format(
                ns="N" if lat >= 0 else "S", lat=abs(lat), ew="E" if lon >= 0 else "W", lon=abs(lon)))
    return urls


def jrc_tile_urls(west: float, south: float, east: float, north: float) -> list[str]:
    """JRC tiles are named by their west edge and NORTH edge, both multiples of 10."""
    urls = []
    for top in range(math.floor(south / 10) * 10 + 10, math.ceil(north / 10) * 10 + 1, 10):
        for left in range(math.floor(west / 10) * 10, math.ceil(east / 10) * 10, 10):
            urls.append(JRC_OCC_URL.format(
                lon=abs(left), ew="E" if left >= 0 else "W", lat=abs(top), ns="N" if top >= 0 else "S"))
    return urls


def read_mosaic(urls: list[str], bounds: tuple[float, float, float, float], nodata=None) -> GeoArray:
    """Read and mosaic only the bounds window from remote/local rasters (float32, NaN = nodata)."""
    import rasterio
    from rasterio.merge import merge

    srcs = [rasterio.open(u if "://" not in u else "/vsicurl/" + u) for u in urls]
    try:
        arr, tr = merge(srcs, bounds=bounds, nodata=nodata if nodata is not None else np.nan,
                        dtype="float32")
    finally:
        for s in srcs:
            s.close()
    data = arr[0].astype("float32")
    if nodata is not None:
        data[data == nodata] = np.nan
    return GeoArray(data=data, west=tr.c, north=tr.f, xres=tr.a, yres=-tr.e)


def slope_degrees(dem: GeoArray) -> GeoArray:
    """Slope from a geographic DEM, using metric pixel sizes at each row's latitude."""
    lats = dem.north - (np.arange(dem.data.shape[0]) + 0.5) * dem.yres
    dx = (dem.xres * 111_320.0 * np.cos(np.radians(lats)))[:, None]
    dy = dem.yres * 110_574.0
    gy, gx = np.gradient(dem.data)
    slope = np.degrees(np.arctan(np.hypot(gx / dx, gy / dy)))
    return GeoArray(slope.astype("float32"), dem.west, dem.north, dem.xres, dem.yres)


def load_slope(bbox: tuple[float, float, float, float], margin_deg: float = 0.002) -> GeoArray:
    w, s, e, n = bbox
    b = (w - margin_deg, s - margin_deg, e + margin_deg, n + margin_deg)
    return slope_degrees(read_mosaic(dem_tile_urls(*b), b))


def load_jrc_occurrence(bbox: tuple[float, float, float, float]) -> GeoArray:
    return read_mosaic(jrc_tile_urls(*bbox), bbox, nodata=JRC_NODATA)
