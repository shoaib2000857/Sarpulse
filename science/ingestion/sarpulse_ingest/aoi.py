"""Area of interest (AOI) handling and the analysis grid derived from it."""

import json
import math
from dataclasses import dataclass
from pathlib import Path

from pyproj import Transformer


@dataclass(frozen=True)
class AOI:
    """A WGS84 lon/lat bounding box with an id. Polygons are reduced to their bbox."""

    id: str
    name: str
    west: float
    south: float
    east: float
    north: float

    def __post_init__(self):
        if not (-180 <= self.west < self.east <= 180 and -90 <= self.south < self.north <= 90):
            raise ValueError(f"Invalid AOI bounds for {self.id}")

    def wkt(self) -> str:
        w, s, e, n = self.west, self.south, self.east, self.north
        return f"POLYGON(({w} {s},{e} {s},{e} {n},{w} {n},{w} {s}))"

    def bbox(self) -> dict:
        return {"west": self.west, "south": self.south, "east": self.east, "north": self.north}


def load_aoi(path: str | Path) -> AOI:
    """Load a GeoJSON Feature (or FeatureCollection with one feature) as an AOI."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    feature = doc["features"][0] if doc.get("type") == "FeatureCollection" else doc
    props = feature.get("properties") or {}
    ring = feature["geometry"]["coordinates"][0]
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    return AOI(
        id=props.get("id") or Path(path).stem,
        name=props.get("name") or Path(path).stem,
        west=min(lons),
        south=min(lats),
        east=max(lons),
        north=max(lats),
    )


@dataclass(frozen=True)
class Grid:
    """North-up raster grid. transform uses GDAL/affine order (a, b, c, d, e, f)."""

    epsg: int
    x0: float  # west edge
    y0: float  # north edge
    spacing: float
    width: int
    height: int

    @property
    def transform(self) -> tuple[float, float, float, float, float, float]:
        return (self.spacing, 0.0, self.x0, 0.0, -self.spacing, self.y0)

    def to_dict(self) -> dict:
        return {
            "crs": f"EPSG:{self.epsg}",
            "epsg": self.epsg,
            "transform": list(self.transform),
            "width": self.width,
            "height": self.height,
            "pixel_spacing_m": self.spacing,
        }


def aoi_grid(aoi: AOI, epsg: int, spacing: float) -> Grid:
    """Projected grid covering the AOI, with edges snapped to multiples of `spacing`.

    Snapping keeps every scene from the same NISAR track/frame on identical pixels.
    """
    tr = Transformer.from_crs("EPSG:4326", f"EPSG:{epsg}", always_xy=True)
    xmin, ymin, xmax, ymax = tr.transform_bounds(aoi.west, aoi.south, aoi.east, aoi.north, densify_pts=21)
    x0 = math.floor(xmin / spacing) * spacing
    x1 = math.ceil(xmax / spacing) * spacing
    y0 = math.ceil(ymax / spacing) * spacing
    y1 = math.floor(ymin / spacing) * spacing
    return Grid(epsg=epsg, x0=x0, y0=y0, spacing=spacing, width=round((x1 - x0) / spacing), height=round((y0 - y1) / spacing))


def grid_bbox_wgs84(grid: Grid) -> dict:
    tr = Transformer.from_crs(f"EPSG:{grid.epsg}", "EPSG:4326", always_xy=True)
    x1 = grid.x0 + grid.width * grid.spacing
    y1 = grid.y0 - grid.height * grid.spacing
    w, s, e, n = tr.transform_bounds(grid.x0, y1, x1, grid.y0, densify_pts=21)
    return {"west": round(w, 6), "south": round(s, 6), "east": round(e, 6), "north": round(n, 6)}
