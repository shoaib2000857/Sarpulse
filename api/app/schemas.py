"""DRAFT API schemas — proposal for Shoaib to confirm in contracts/.

Field names follow the master plan (scenes.json / analysis.json / time_series.json)
plus the evidence "Change Passport". Every record carries a data_status so the UI
can never present synthetic fixtures as NASA observations.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DataStatus(str, Enum):
    synthetic = "SYNTHETIC/DEMO — NOT NASA OBSERVATIONS"
    observed = "observed"


class EvidenceLabel(str, Enum):
    observed = "Observed"
    derived = "Derived"
    context = "Context"
    hypothesis = "Hypothesis"
    unverified = "Unverified"


class BBox(BaseModel):
    west: float = Field(ge=-180, le=180)
    south: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)

    def contains(self, lon: float, lat: float) -> bool:
        return self.west <= lon <= self.east and self.south <= lat <= self.north


class Site(BaseModel):
    id: str
    name: str
    description: str
    bbox: BBox
    data_status: DataStatus
    verified: bool = Field(description="True only when comparable real NISAR scenes are confirmed")


class Scene(BaseModel):
    scene_id: str
    source: str
    acquired_at_utc: datetime
    maturity: str
    crid: str | None = None
    orbit_direction: str | None = None
    relative_orbit: int | None = None
    polarizations: list[str]
    grid_epsg: int
    pixel_spacing_m: float
    footprint: BBox
    license: str
    data_url: str | None = None
    data_status: DataStatus


class Analysis(BaseModel):
    aoi_id: str
    source_scene_ids: list[str]
    before_scene_id: str
    after_scene_id: str
    processing_version: str
    valid_area_km2: float = Field(ge=0)
    gained_water_km2: float = Field(ge=0)
    lost_water_km2: float = Field(ge=0)
    ambiguous_km2: float = Field(ge=0, default=0)
    class_definitions: dict[str, str]
    threshold_method: str
    provenance: dict[str, Any]
    limitations: list[str]
    validation_status: str
    data_status: DataStatus


class TimeSeriesPoint(BaseModel):
    date: date
    scene_id: str
    water_area_km2: float | None = None
    quality_flags: list[str] = []


class TimeSeries(BaseModel):
    aoi_id: str
    interpolated: bool = False
    points: list[TimeSeriesPoint]
    data_status: DataStatus


class ContextRecord(BaseModel):
    """Ancillary evidence (rainfall, optical, historical water, terrain). Never ground truth."""

    kind: str  # e.g. rainfall_imerg, optical_sentinel2, jrc_gsw, dem_slope
    source: str
    period_start: date | None = None
    period_end: date | None = None
    value: float | None = None
    units: str | None = None
    resolution: str | None = None
    caveat: str
    data_status: DataStatus


class SamplePoint(BaseModel):
    """Per-location values from the analysis pipeline (Naveen/Veer outputs)."""

    lon: float
    lat: float
    before_hh_db: float | None = None
    after_hh_db: float | None = None
    before_hv_db: float | None = None
    after_hv_db: float | None = None
    change_class: str
    valid: bool = True
    slope_deg: float | None = None
    jrc_occurrence_pct: float | None = None


class EvidenceItem(BaseModel):
    label: EvidenceLabel
    statement: str
    values: dict[str, Any] = {}
    source: str | None = None


class ChangePassport(BaseModel):
    site_id: str
    lon: float
    lat: float
    before_scene_id: str
    after_scene_id: str
    change_class: str
    evidence: list[EvidenceItem]
    limitations: list[str]
    provenance: dict[str, Any]
    data_status: DataStatus
