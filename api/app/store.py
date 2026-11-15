"""Read-only data store over a static directory of precomputed JSON.

Layout: <data_dir>/<site_id>/{site,scenes,analysis,time_series,samples,layers}.json,
optional context.json, plus raster/PNG assets referenced by layers.json.
This keeps the API a thin layer over the same files the frontend can load
statically, so the demo never depends on live processing.
"""

import json
from functools import lru_cache
from pathlib import Path

from pydantic import TypeAdapter

from .config import settings
from .schemas import Analysis, ContextRecord, LayersManifest, SamplePoint, Scene, Site, TimeSeries

ASSET_SUFFIXES = {".png", ".tif", ".tiff"}


class NotFound(Exception):
    pass


class Store:
    def __init__(self, root: Path):
        self.root = root

    def _safe(self, site_id: str, rel: str) -> Path:
        site_dir = (self.root / site_id).resolve()
        path = (site_dir / rel).resolve()
        if not site_dir.is_relative_to(self.root.resolve()) or not path.is_relative_to(site_dir) or not path.is_file():
            raise NotFound(f"{site_id}/{rel}")
        return path

    def _read(self, site_id: str, name: str):
        return json.loads(self._safe(site_id, f"{name}.json").read_text(encoding="utf-8"))

    def site_ids(self) -> list[str]:
        if not self.root.is_dir():
            return []
        return sorted(p.name for p in self.root.iterdir() if (p / "site.json").is_file())

    def site(self, site_id: str) -> Site:
        return Site.model_validate(self._read(site_id, "site"))

    def scenes(self, site_id: str) -> list[Scene]:
        return TypeAdapter(list[Scene]).validate_python(self._read(site_id, "scenes"))

    def analysis(self, site_id: str) -> Analysis:
        return Analysis.model_validate(self._read(site_id, "analysis"))

    def time_series(self, site_id: str) -> TimeSeries:
        return TimeSeries.model_validate(self._read(site_id, "time_series"))

    def context(self, site_id: str) -> list[ContextRecord]:
        """Optional: the analysis pipeline does not write context.json; context adapters do."""
        self.site(site_id)  # 404 for unknown sites
        try:
            data = self._read(site_id, "context")
        except NotFound:
            return []
        return TypeAdapter(list[ContextRecord]).validate_python(data)

    def layers(self, site_id: str) -> LayersManifest:
        return LayersManifest.model_validate(self._read(site_id, "layers"))

    def asset(self, site_id: str, rel: str) -> Path:
        if Path(rel).suffix.lower() not in ASSET_SUFFIXES:
            raise NotFound(f"{site_id}/{rel}")
        return self._safe(site_id, rel)

    def samples(self, site_id: str) -> list[SamplePoint]:
        return TypeAdapter(list[SamplePoint]).validate_python(self._read(site_id, "samples"))

    def point(self, site_id: str, lon: float, lat: float) -> tuple[SamplePoint, float]:
        """Sample the actual classified pixel where exported rasters are available.

        Older/small fixtures use the sparse sample grid with a disclosed distance.
        """
        from .passport import distance_km, nearest_sample

        analysis = self.analysis(site_id)
        rasters = getattr(analysis, "passport_rasters", None)
        if not rasters:
            samples = self.samples(site_id)
            if not samples:
                raise NotFound("No analysed samples for this site")
            return nearest_sample(samples, lon, lat)

        import math
        import rasterio
        from rasterio.warp import transform

        values = {}
        pixel_lon, pixel_lat = lon, lat
        for key in ("change_class", "before_hh_db", "after_hh_db", "before_hv_db", "after_hv_db"):
            with rasterio.open(self.asset(site_id, rasters[key])) as src:
                xs, ys = transform("EPSG:4326", src.crs, [lon], [lat])
                row, col = src.index(xs[0], ys[0])
                if not (0 <= row < src.height and 0 <= col < src.width):
                    values[key] = None
                    continue
                raw = next(src.sample([(xs[0], ys[0])], masked=True))[0]
                values[key] = float(raw) if not getattr(raw, "mask", False) and math.isfinite(float(raw)) else None
                if key == "change_class":
                    x, y = src.xy(row, col)
                    px, py = transform(src.crs, "EPSG:4326", [x], [y])
                    pixel_lon, pixel_lat = px[0], py[0]
        classes = {0: "stable_land", 1: "water_gained", 2: "water_lost", 3: "stable_water", 4: "ambiguous"}
        change_class = classes.get(values.pop("change_class"), "nodata")
        sample = SamplePoint(lon=pixel_lon, lat=pixel_lat, change_class=change_class,
                             valid=change_class != "nodata", **values)
        return sample, distance_km(lon, lat, pixel_lon, pixel_lat)


@lru_cache
def get_store() -> Store:
    return Store(settings.resolved_data_dir())
