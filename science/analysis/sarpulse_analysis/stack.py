"""Load an analysis-ready stack (`sarpulse.ard_stack.v0`, produced by science/ingestion)."""

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from pyproj import CRS

SUPPORTED_SCHEMAS = {"sarpulse.ard_stack.v0"}
SYNTHETIC = "SYNTHETIC/DEMO — NOT NASA OBSERVATIONS"
OBSERVED = "observed"


@dataclass(frozen=True)
class Grid:
    epsg: int
    transform: tuple[float, float, float, float, float, float]
    width: int
    height: int
    pixel_spacing_m: float

    @property
    def pixel_area_km2(self) -> float:
        return abs(self.transform[0] * self.transform[4]) / 1e6

    @property
    def affine(self) -> Affine:
        return Affine(*self.transform)


@dataclass
class SceneInfo:
    scene_id: str
    acquired_at_utc: str
    files: dict[str, str]
    data_status: str
    maturity: str | None
    record: dict = field(repr=False)

    @property
    def date(self) -> str:
        return self.acquired_at_utc[:10]


@dataclass
class Stack:
    root: Path
    doc: dict
    grid: Grid
    scenes: list[SceneInfo]

    @property
    def aoi_id(self) -> str:
        return self.doc["aoi"]["id"]

    @property
    def data_status(self) -> str:
        return self.doc.get("data_status", SYNTHETIC)

    def scene(self, ref: str) -> SceneInfo:
        """Find a scene by exact id or by acquisition date (YYYY-MM-DD)."""
        hits = [s for s in self.scenes if ref in (s.scene_id, s.date)]
        if len(hits) != 1:
            raise KeyError(f"{ref!r} matches {len(hits)} scenes in stack {self.doc.get('stack_id')}")
        return hits[0]

    def read(self, scene: SceneInfo, layer: str) -> np.ndarray:
        path = self.root / scene.files[layer]
        with rasterio.open(path) as r:
            if r.crs.to_epsg() != self.grid.epsg or (r.width, r.height) != (self.grid.width, self.grid.height):
                raise ValueError(f"{path} is not on the stack grid")
            if not np.allclose(tuple(r.transform)[:6], self.grid.transform, rtol=0, atol=1e-7):
                raise ValueError(f"{path} transform differs from the stack grid")
            arr = r.read(1)
        return arr

    def read_scene(self, scene: SceneInfo) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """(HH linear, HV linear, valid bool) with NaN outside valid pixels."""
        hh = self.read(scene, "HHHH").astype(np.float32)
        hv = self.read(scene, "HVHV").astype(np.float32)
        valid = self.read(scene, "valid").astype(bool) & np.isfinite(hh) & np.isfinite(hv) & (hh > 0) & (hv > 0)
        hh[~valid] = np.nan
        hv[~valid] = np.nan
        return hh, hv, valid


def load_stack(path: str | Path) -> Stack:
    path = Path(path)
    doc = json.loads(path.read_text(encoding="utf-8"))
    if doc.get("schema_version") not in SUPPORTED_SCHEMAS:
        raise ValueError(f"Unsupported stack schema {doc.get('schema_version')!r}")
    g = doc["grid"]
    grid = Grid(epsg=int(g["epsg"]), transform=tuple(g["transform"]), width=int(g["width"]), height=int(g["height"]), pixel_spacing_m=float(g["pixel_spacing_m"]))
    crs = CRS.from_epsg(grid.epsg)
    if not crs.is_projected or any(a.unit_conversion_factor != 1 for a in crs.axis_info):
        raise ValueError("Analysis requires a projected grid in metres for physical area calculations")
    if (grid.width < 1 or grid.height < 1 or grid.transform[0] <= 0 or grid.transform[4] >= 0
            or grid.transform[1] != 0 or grid.transform[3] != 0):
        raise ValueError("Analysis requires a nonempty north-up raster grid")
    scenes = [
        SceneInfo(
            scene_id=s["scene_id"],
            acquired_at_utc=s["acquired_at_utc"],
            files=s["files"],
            data_status=s.get("data_status", SYNTHETIC),
            maturity=(s.get("scene") or {}).get("maturity"),
            record=s,
        )
        for s in doc["scenes"]
    ]
    scenes.sort(key=lambda s: s.acquired_at_utc)
    if len(scenes) < 2 or len({s.acquired_at_utc for s in scenes}) != len(scenes):
        raise ValueError("At least two unique acquisition times are required")
    # Synthetic test stacks can omit observational metadata; real stacks cannot.
    if doc.get("data_status") == OBSERVED:
        for name in ("maturity", "crid", "orbit_direction", "relative_orbit", "polarizations"):
            values = [s.record.get("scene", {}).get(name) for s in scenes]
            if any(v is None or v == [] or v == "UNKNOWN" for v in values) or any(v != values[0] for v in values):
                raise ValueError(f"Missing or incompatible scene {name}: {values}")
    return Stack(root=path.parent, doc=doc, grid=grid, scenes=scenes)
