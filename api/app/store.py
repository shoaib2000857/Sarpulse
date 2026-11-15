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


@lru_cache
def get_store() -> Store:
    return Store(settings.resolved_data_dir())
