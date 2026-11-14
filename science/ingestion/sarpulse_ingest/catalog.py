"""Discover NISAR L2 GCOV products over an AOI with the public ASF Search API.

Searching is unauthenticated; reading the HDF5 products needs an Earthdata Login
(see access.py). Only catalogue metadata is recorded here; nothing is invented.
"""

from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone

import requests

from .aoi import AOI
from .granule import parse_granule_name

ASF_SEARCH_URL = "https://api.daac.asf.alaska.edu/services/search/param"


@dataclass
class CandidateScene:
    scene_id: str
    url: str
    collection: str
    maturity: str
    processing_type: str
    crid: str
    track: int
    frame: int
    direction: str
    mode: str
    polarization: str
    orbit_accuracy: str
    coverage: str
    counter: int
    start_utc: str
    stop_utc: str
    main_band_polarizations: list[str]
    footprint_wkt: str
    footprint_bbox: dict
    processing_date_utc: str | None
    pge_version: str | None
    browse_url: str | None

    def to_dict(self) -> dict:
        return asdict(self)


def maturity_from_collection(collection: str) -> str:
    """Data-release maturity as published by ASF (BETA < PROVISIONAL < VALIDATED)."""
    c = collection.upper()
    if c.startswith("NISAR_UR") or "UR_L2" in c:
        return "URGENT_RESPONSE"
    if "BETA" in c:
        return "BETA"
    if "PROVISIONAL" in c:
        return "PROVISIONAL"
    if c.endswith("_V1") or c.endswith("_V2"):
        return "VALIDATED"
    return "UNKNOWN"


def _bbox_of(coords: list) -> dict:
    ring = coords[0]
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    return {"west": min(lons), "south": min(lats), "east": max(lons), "north": max(lats)}


def _wkt(ring: list) -> str:
    return "POLYGON((" + ",".join(f"{x} {y}" for x, y in ring) + "))"


def candidate_from_feature(feature: dict) -> CandidateScene:
    p = feature["properties"]
    g = parse_granule_name(p["sceneName"])
    collection = p.get("collectionName") or ""
    coords = feature["geometry"]["coordinates"]
    browse = [b for b in (p.get("browse") or []) if b.endswith("_LATLON.png")]
    return CandidateScene(
        scene_id=g.name,
        url=p["url"],
        collection=collection,
        maturity=maturity_from_collection(collection),
        processing_type=g.processing_type,
        crid=g.crid,
        track=g.track,
        frame=g.frame,
        direction=g.direction,
        mode=g.mode,
        polarization=g.polarization,
        orbit_accuracy=g.orbit_accuracy,
        coverage=g.coverage,
        counter=g.counter,
        start_utc=p["startTime"],
        stop_utc=p["stopTime"],
        main_band_polarizations=list(p.get("mainBandPolarization") or []),
        footprint_wkt=_wkt(coords[0]),
        footprint_bbox=_bbox_of(coords),
        processing_date_utc=p.get("processingDate"),
        pge_version=p.get("pgeVersion"),
        browse_url=browse[0] if browse else None,
    )


def search_gcov(
    aoi: AOI,
    start: date | None = None,
    end: date | None = None,
    max_results: int = 500,
    session: requests.Session | None = None,
) -> tuple[list[CandidateScene], dict]:
    """Return GCOV candidates intersecting the AOI plus a record of the query itself."""
    params = {
        "dataset": "NISAR",
        "processingLevel": "GCOV",
        "intersectsWith": aoi.wkt(),
        "output": "geojson",
        "maxResults": str(max_results),
    }
    if start:
        params["start"] = f"{start.isoformat()}T00:00:00Z"
    if end:
        params["end"] = f"{end.isoformat()}T23:59:59Z"
    http = session or requests.Session()
    resp = http.get(ASF_SEARCH_URL, params=params, timeout=120)
    resp.raise_for_status()
    features = resp.json().get("features", [])
    scenes = sorted((candidate_from_feature(f) for f in features), key=lambda s: (s.start_utc, s.scene_id))
    query = {
        "endpoint": ASF_SEARCH_URL,
        "params": params,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "result_count": len(scenes),
    }
    return scenes, query
