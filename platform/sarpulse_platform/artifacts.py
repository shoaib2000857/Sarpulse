"""Contract checks and versioned static delivery."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.schemas import DataStatus
from app.store import Store

CORE_JSON = ("site.json", "scenes.json", "analysis.json", "time_series.json", "samples.json", "layers.json")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def inspect_site(site_dir: Path, allow_synthetic: bool = False, require_validation: bool = False) -> dict:
    """Validate a science output folder through the exact API models used in production."""
    site_dir = Path(site_dir).resolve()
    store = Store(site_dir.parent)
    sid = site_dir.name
    site, analysis = store.site(sid), store.analysis(sid)
    scenes, timeseries, layers = store.scenes(sid), store.time_series(sid), store.layers(sid)
    samples, context = store.samples(sid), store.context(sid)
    if site.id != sid or any(a != sid for a in (analysis.aoi_id, timeseries.aoi_id, layers.aoi_id)):
        raise ValueError("Site folder and aoi_id/site.id must agree")
    statuses = {x.data_status for x in (site, analysis, timeseries, layers, *scenes)}
    if len(statuses) != 1:
        raise ValueError("Radar records have inconsistent data_status")
    if not allow_synthetic and statuses != {DataStatus.observed}:
        raise ValueError("Synthetic bundle rejected; --allow-synthetic is for integration testing only")
    if site.verified and site.data_status != DataStatus.observed:
        raise ValueError("Synthetic sites cannot be marked verified")
    by_id = {s.scene_id: s for s in scenes}
    if len(by_id) != len(scenes) or len(scenes) < 2:
        raise ValueError("At least two distinct scene records are required")
    required_ids = {analysis.before_scene_id, analysis.after_scene_id, *analysis.source_scene_ids}
    if not required_ids <= by_id.keys():
        raise ValueError("Analysis references unknown scene IDs")
    before, after = by_id[analysis.before_scene_id], by_id[analysis.after_scene_id]
    if before.acquired_at_utc >= after.acquired_at_utc:
        raise ValueError("Before acquisition must precede after acquisition")
    for field in ("maturity", "crid", "orbit_direction", "relative_orbit", "polarizations", "grid_epsg", "pixel_spacing_m"):
        if getattr(before, field) != getattr(after, field):
            raise ValueError(f"Incompatible pair metadata: {field}")
    if any(p.scene_id not in by_id or p.date != by_id[p.scene_id].acquired_at_utc.date() for p in timeseries.points):
        raise ValueError("Time series references unknown scenes or mismatched dates")
    if timeseries.interpolated:
        raise ValueError("v0 delivery supports actual observations only")
    if analysis.valid_area_km2 <= 0:
        raise ValueError("No valid area available for the investigation")
    if analysis.gained_water_km2 + analysis.lost_water_km2 + analysis.ambiguous_km2 > analysis.valid_area_km2 + 0.001:
        raise ValueError("Reported change areas exceed the valid footprint")
    assets = set()
    for layer in layers.layers:
        for rel in (layer.png, layer.geotiff):
            if rel:
                if "://" in rel:
                    raise ValueError("Delivery requires local precomputed assets, not remote processing dependencies")
                assets.add(str(store.asset(sid, rel).relative_to(site_dir).as_posix()))
    for rel in (getattr(analysis, "passport_rasters", None) or {}).values():
        assets.add(str(store.asset(sid, rel).relative_to(site_dir).as_posix()))
    validation = getattr(analysis, "validation", []) or []
    validated = bool(validation) and all(v.get("metrics", {}).get("n", 0) > 0 for v in validation)
    if require_validation and not validated:
        raise ValueError("No independent reference comparison with usable samples")
    return {"site_id": sid, "data_status": site.data_status.value, "scene_count": len(scenes),
            "sample_count": len(samples), "context_count": len(context), "assets": sorted(assets),
            "independent_reference_compared": validated, "validation_status": analysis.validation_status,
            "limitations": analysis.limitations}


def _revision() -> dict:
    try:
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True))
        return {"git_commit": sha, "working_tree_dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"git_commit": None, "working_tree_dirty": None}


def export_vectors(site_dir: Path, target: Path, max_features: int = 25000) -> int:
    import numpy as np
    import rasterio
    from rasterio.features import shapes
    from rasterio.warp import transform_geom

    analysis = json.loads((site_dir / "analysis.json").read_text(encoding="utf-8"))
    features = []
    names = {1: "water_gained", 2: "water_lost", 4: "ambiguous"}
    with rasterio.open(site_dir / "change_class.tif") as src:
        data = src.read(1)
        for geom, code in shapes(data, mask=np.isin(data, list(names)), transform=src.transform):
            if len(features) >= max_features:
                raise ValueError("Vector export exceeds 25,000 features; use the raster or a smaller AOI")
            features.append({"type": "Feature", "geometry": transform_geom(src.crs, "EPSG:4326", geom),
                             "properties": {"change_class": names[int(code)], "data_status": analysis["data_status"],
                                            "before_scene_id": analysis["before_scene_id"], "after_scene_id": analysis["after_scene_id"]}})
    write_json(target, {"type": "FeatureCollection", "features": features,
                        "description": "Derived water-change classes, not confirmed flood boundaries.",
                        "data_status": analysis["data_status"]})
    return len(features)


def export_bundle(site_dir: Path, out: Path, allow_synthetic=False, require_validation=False, vectors=False) -> dict:
    """Create a new deployment directory; existing deliveries are never overwritten."""
    site_dir, out = Path(site_dir).resolve(), Path(out).resolve()
    report = inspect_site(site_dir, allow_synthetic, require_validation)
    if out == site_dir or out.is_relative_to(site_dir) or site_dir.is_relative_to(out):
        raise ValueError("Export destination must be separate from the source site")
    if out.exists():
        raise FileExistsError(f"Choose a new versioned delivery path: {out}")
    sid = report["site_id"]
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", sid):
        raise ValueError("Site IDs must contain only letters, numbers, hyphens and underscores")
    target = out / "sites" / sid
    target.mkdir(parents=True)
    # Copy a deliberate allowlist, never credentials or unrelated source-directory files.
    for rel in (*CORE_JSON, *report["assets"]):
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(site_dir / rel, dst)
    context = json.loads((site_dir / "context.json").read_text(encoding="utf-8")) if (site_dir / "context.json").is_file() else []
    write_json(target / "context.json", context)
    validation = getattr(Store(site_dir.parent).analysis(sid), "validation", [])
    if validation:
        write_json(target / "validation.json", validation)
    scene_doc = json.loads((target / "scenes.json").read_text(encoding="utf-8"))
    analysis_doc = json.loads((target / "analysis.json").read_text(encoding="utf-8"))
    write_json(target / "provenance.json", {"data_status": report["data_status"], "scenes": scene_doc,
                                          "processing": analysis_doc["provenance"], "limitations": report["limitations"]})
    points = json.loads((target / "time_series.json").read_text(encoding="utf-8"))["points"]
    with (target / "time_series.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "scene_id", "water_area_km2", "data_status", "quality_flags"])
        writer.writeheader()
        for p in points:
            writer.writerow({k: p.get(k) for k in ("date", "scene_id", "water_area_km2")} |
                            {"data_status": report["data_status"], "quality_flags": "; ".join(p.get("quality_flags", []))})
    if vectors:
        report["vector_features"] = export_vectors(site_dir, target / "changes.geojson")
    site = json.loads((target / "site.json").read_text(encoding="utf-8"))
    write_json(out / "sites.json", [site | {"path": f"sites/{sid}/"}])
    metadata = {"schema_version": "sarpulse.delivery.v0", "created_utc": utc_now(), "site": report,
                "source": _revision(), "si_assistance": "Code and documentation assisted by Codex; see AI_DISCLOSURE.md.",
                "files": {}}
    for path in sorted(out.rglob("*")):
        if path.is_file():
            metadata["files"][path.relative_to(out).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    write_json(out / "artifact.json", metadata)
    (out / "README.txt").write_text(
        f"SARPulse precomputed delivery\nData status: {report['data_status']}\n"
        f"Validation: {report['validation_status']}\n"
        "Static consumer: sites.json -> sites/<id>/layers.json. Resolve layer paths relative to the site folder.\n"
        "API consumer: sarpulse serve --data-dir <this-folder>/sites\n"
        "Threshold ranges are sensitivity estimates, not calibrated probabilities.\n"
        "Observational inputs and synthetic test fixtures are identified separately.\n", encoding="utf-8")
    return metadata
