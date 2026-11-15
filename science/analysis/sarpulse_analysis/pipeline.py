"""End-to-end change analysis for one analysis-ready stack.

Output directory layout matches the API store (`<data_dir>/<site_id>/*.json`, see
api/app/store.py in PR #7) plus rasters and web overlays:

    site.json scenes.json analysis.json time_series.json samples.json layers.json
    change_class.tif delta_hh_db.tif water/<date>.tif web/*.png
"""

import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from pyproj import Transformer

from . import __version__
from .change import CLASS_CODES, CLASS_DEFINITIONS, CLASS_NAMES, NODATA, DateResult, Params, change_map, classify_date
from .export import WebProjector, backscatter_rgba, classes_rgba, legend, water_rgba, write_geotiff, write_json, write_png
from .stack import OBSERVED, SYNTHETIC, Stack, load_stack

MAX_SAMPLES = 3000

BASE_LIMITATIONS = [
    "Open water is inferred from low L-band HH backscatter. Smooth non-water surfaces (dry sand bars, bare flat soil, radar shadow) can look like water; wind- or rain-roughened water can look like land.",
    "Flooded vegetation can brighten HH through double-bounce scattering and is NOT mapped as water; strong HH increases on land are reported separately as hh_brightening_non_water_km2.",
    "A change in backscatter is evidence of surface change, not proof of flooding or of its cause. Rainfall or river-gauge data are context, not confirmation.",
    "Layover/shadow from the NISAR static-layers product is not applied; results in steep terrain are unreliable.",
    "Areas use projected (UTM) pixel area; map scale distortion is below ~0.2 % within a UTM zone.",
    "Backscatter values in samples.json are gamma-0 dB on the analysis grid; filter settings are recorded in processing parameters. They are not unprocessed source pixels.",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _km2(pixels: int | float, stack: Stack) -> float:
    return round(float(pixels) * stack.grid.pixel_area_km2, 4)


def _sample_points(stack: Stack, cls: np.ndarray, before: DateResult, after: DateResult) -> list[dict]:
    """Regular grid of sample points with the values the classifier used (API SamplePoint)."""
    g = stack.grid
    step = max(1, math.ceil(math.sqrt(g.width * g.height / MAX_SAMPLES)))
    rows, cols = np.mgrid[step // 2 : g.height : step, step // 2 : g.width : step]
    rows, cols = rows.ravel(), cols.ravel()
    xs = g.transform[2] + (cols + 0.5) * g.transform[0]
    ys = g.transform[5] + (rows + 0.5) * g.transform[4]
    lons, lats = Transformer.from_crs(f"EPSG:{g.epsg}", "EPSG:4326", always_xy=True).transform(xs, ys)

    def val(a: np.ndarray, r: int, c: int):
        v = a[r, c]
        return round(float(v), 2) if np.isfinite(v) else None

    out = []
    for r, c, lon, lat in zip(rows, cols, lons, lats):
        code = int(cls[r, c])
        out.append(
            {
                "lon": round(float(lon), 6),
                "lat": round(float(lat), 6),
                "before_hh_db": val(before.hh_db, r, c),
                "after_hh_db": val(after.hh_db, r, c),
                "before_hv_db": val(before.hv_db, r, c),
                "after_hv_db": val(after.hv_db, r, c),
                "change_class": CLASS_NAMES.get(code, "nodata"),
                "valid": code != NODATA,
                "slope_deg": None,
                "jrc_occurrence_pct": None,
            }
        )
    return out


def run_analysis(stack_path: str | Path, before_ref: str, after_ref: str, out_dir: str | Path, params: Params | None = None) -> dict:
    p = params or Params()
    stack = load_stack(stack_path)
    out = Path(out_dir)
    before_scene, after_scene = stack.scene(before_ref), stack.scene(after_ref)
    if before_scene.acquired_at_utc >= after_scene.acquired_at_utc:
        raise ValueError("before scene must be acquired earlier than after scene")

    statuses = {s.data_status for s in stack.scenes} | {stack.data_status}
    data_status = OBSERVED if statuses == {OBSERVED} else SYNTHETIC

    # Classify every date (time series) with its own threshold.
    results: dict[str, DateResult] = {}
    for s in stack.scenes:
        hh, hv, valid = stack.read_scene(s)
        results[s.scene_id] = classify_date(s.scene_id, s.date, hh, hv, valid, p)
    before, after = results[before_scene.scene_id], results[after_scene.scene_id]

    cls, diag = change_map(before, after, p)
    delta = diag.pop("delta_hh_db")
    cp = diag["class_pixels"]

    # Time series over the area valid on every date, so areas are comparable.
    common = np.logical_and.reduce([r.valid for r in results.values()])
    if not np.any(before.valid & after.valid):
        raise ValueError("Selected scenes have no common valid pixels")
    if not common.any():
        raise ValueError("Time-series scenes have no common valid footprint; use a smaller compatible stack")
    ts_points = []
    for s in stack.scenes:
        r = results[s.scene_id]
        t, u = r.threshold.threshold_db, r.threshold.uncertainty_db
        flags = list(r.flags)
        if (s.maturity or "").upper() in ("PROVISIONAL", "BETA"):
            flags.append(f"maturity_{s.maturity.lower()}")
        ts_points.append(
            {
                "date": s.date,
                "scene_id": s.scene_id,
                "water_area_km2": _km2((r.water & common).sum(), stack),
                "water_area_km2_range": [_km2((common & (r.hh_db < t - u)).sum(), stack), _km2((common & (r.hh_db < t + u)).sum(), stack)],
                "threshold_db": round(t, 3),
                "quality_flags": flags,
            }
        )

    # Rasters.
    g = stack.grid
    tags = {"data_status": data_status, "before_scene_id": before.scene_id, "after_scene_id": after.scene_id}
    write_geotiff(out / "change_class.tif", cls, g, NODATA, {**tags, "classes": CLASS_CODES})
    delta_out = np.where(cls != NODATA, delta, np.nan).astype(np.float32)
    write_geotiff(out / "delta_hh_db.tif", delta_out, g, np.nan, {**tags, "units": "dB (after - before, Lee-filtered gamma-0 HH)"})
    passport_rasters = {"change_class": "change_class.tif"}
    for label, result in (("before", before), ("after", after)):
        for channel in ("hh", "hv"):
            key = f"{label}_{channel}_db"
            rel = f"evidence/{key}.tif"
            write_geotiff(out / rel, getattr(result, f"{channel}_db"), g, np.nan,
                          {**tags, "units": "gamma-0 dB, Lee-filtered" if p.speckle_filter == "lee" else "gamma-0 dB"})
            passport_rasters[key] = rel
    proj = WebProjector(g)
    write_png(out / "web" / "change_class.png", classes_rgba(proj.warp(cls, NODATA)))
    layers = [
        {
            "id": "change_class",
            "kind": "categorical",
            "title": f"Water change {before.date} to {after.date}",
            "png": "web/change_class.png",
            "geotiff": "change_class.tif",
            "legend": legend(),
            "before_scene_id": before.scene_id,
            "after_scene_id": after.scene_id,
        }
    ]
    write_png(out / "web" / "delta_hh_db.png", backscatter_rgba(proj.warp(delta_out, np.float32(np.nan)), (-10, 10)))
    layers.append({"id": "delta_hh_db", "kind": "difference", "title": "HH change (after minus before)",
                   "png": "web/delta_hh_db.png", "geotiff": "delta_hh_db.tif", "display_range_db": [-10, 10]})
    for s in stack.scenes:
        r = results[s.scene_id]
        wmask = np.where(r.valid, r.water.astype(np.uint8), NODATA).astype(np.uint8)
        write_geotiff(out / "water" / f"{r.date}.tif", wmask, g, NODATA, {"data_status": data_status, "scene_id": r.scene_id, "values": "1 water, 0 land, 255 nodata"})
        write_png(out / "web" / f"water_{r.date}.png", water_rgba(proj.warp(wmask, NODATA)))
        write_png(out / "web" / f"hh_db_{r.date}.png", backscatter_rgba(proj.warp(r.hh_db, np.float32(np.nan))))
        write_png(out / "web" / f"hv_db_{r.date}.png", backscatter_rgba(proj.warp(r.hv_db, np.float32(np.nan)), (-35, -5)))
        layers.append({"id": f"water_{r.date}", "kind": "mask", "title": f"Open water {r.date}", "png": f"web/water_{r.date}.png", "geotiff": f"water/{r.date}.tif", "scene_id": r.scene_id, "date": r.date})
        layers.append({"id": f"hh_db_{r.date}", "kind": "backscatter", "title": f"HH backscatter {r.date}", "png": f"web/hh_db_{r.date}.png", "display_range_db": [-25.0, 0.0], "scene_id": r.scene_id, "date": r.date})
        layers.append({"id": f"hv_db_{r.date}", "kind": "backscatter", "title": f"HV backscatter {r.date}", "png": f"web/hv_db_{r.date}.png", "display_range_db": [-35.0, -5.0], "scene_id": r.scene_id, "date": r.date})

    limitations = list(BASE_LIMITATIONS)
    maturities = sorted({(s.maturity or "UNKNOWN") for s in stack.scenes})
    if any(m in ("PROVISIONAL", "BETA", "URGENT_RESPONSE", "UNKNOWN") for m in maturities):
        limitations.insert(0, f"NISAR GCOV inputs have data maturity {', '.join(maturities)}: calibrated but not fully validated by the mission.")
    for r in (before, after):
        for f in r.flags:
            limitations.append(f"{r.date}: threshold quality flag '{f}'.")
    limitations.extend(f"Stack comparability: {w}" for w in stack.doc.get("comparability_warnings", []))
    if data_status != OBSERVED:
        limitations.insert(0, "All values are derived from SYNTHETIC inputs, not NASA observations.")

    analysis = {
        "aoi_id": stack.aoi_id,
        "source_scene_ids": [s.scene_id for s in stack.scenes],
        "before_scene_id": before.scene_id,
        "after_scene_id": after.scene_id,
        "processing_version": f"sarpulse_analysis {__version__}",
        "valid_area_km2": _km2(diag["valid_pixels"], stack),
        "gained_water_km2": _km2(cp["water_gained"], stack),
        "lost_water_km2": _km2(cp["water_lost"], stack),
        "ambiguous_km2": _km2(cp["ambiguous"], stack),
        "stable_water_km2": _km2(cp["stable_water"], stack),
        "stable_land_km2": _km2(cp["stable_land"], stack),
        "area_ranges_km2": {
            "water_gained": [_km2(v, stack) for v in diag["gained_pixels_range"]],
            "water_lost": [_km2(v, stack) for v in diag["lost_pixels_range"]],
            "note": "min/max over thresholds shifted by -u, 0, +u on each date, with the min_change_db rule and no ambiguity masking",
        },
        "hh_brightening_non_water_km2": _km2(diag["hh_brightening_non_water_pixels"], stack),
        "class_definitions": CLASS_DEFINITIONS,
        "threshold_method": f"{before.threshold.method} per date on Lee-filtered HH dB; change requires |delta HH| >= {p.min_change_db} dB",
        "thresholds": {r.date: {**r.threshold.to_dict(), "enl": round(r.enl, 2) if r.enl else None} for r in (before, after)},
        "passport_rasters": passport_rasters,
        "baseline_comparison": {
            "description": "Diagnostic areas on the common pair footprint; not accuracy metrics or flood truth.",
            "absolute_difference_threshold_db": p.min_change_db,
            "absolute_difference_km2": _km2(((cls != NODATA) & (np.abs(delta) >= p.min_change_db)).sum(), stack),
            "difference_without_water_transition_km2": _km2(((cls != NODATA) & (np.abs(delta) >= p.min_change_db) & (before.water == after.water)).sum(), stack),
            "simple_threshold_gain_km2": _km2(((cls != NODATA) & ~before.water & after.water).sum(), stack),
            "simple_threshold_loss_km2": _km2(((cls != NODATA) & before.water & ~after.water).sum(), stack),
        },
        "method_agreement": {
            "description": "Otsu water vs unsupervised 2-component Gaussian mixture on (HH, HV) dB. Internal consistency only, NOT accuracy.",
            **{r.date: r.method_agreement for r in (before, after)},
        },
        "provenance": {
            "si_assistance": "Code and integration assisted by Codex; see AI_DISCLOSURE.md. Observational inputs are not SI-generated.",
            "stack_id": stack.doc.get("stack_id"),
            "stack_schema": stack.doc.get("schema_version"),
            "comparability_key": stack.doc.get("comparability_key"),
            "ingest_processing": stack.doc.get("processing"),
            "grid": stack.doc.get("grid"),
            "scenes": [s.record.get("scene", {"scene_id": s.scene_id, "acquired_at_utc": s.acquired_at_utc, "maturity": s.maturity}) for s in stack.scenes],
            "parameters": p.to_dict(),
            "created_utc": _utc_now(),
        },
        "limitations": limitations,
        "validation_status": "not validated: no independent reference compared yet",
        "data_status": data_status,
    }
    time_series = {
        "aoi_id": stack.aoi_id,
        "interpolated": False,
        "common_valid_area_km2": _km2(common.sum(), stack),
        "points": ts_points,
        "data_status": data_status,
    }
    site = {
        "id": stack.aoi_id,
        "name": stack.doc["aoi"].get("name", stack.aoi_id),
        "description": f"NISAR L2 GCOV open-water change, {before.date} to {after.date} ({stack.doc.get('stack_id')}).",
        "bbox": stack.doc.get("grid_bbox_wgs84") or stack.doc["aoi"]["bbox"],
        "data_status": data_status,
        "verified": data_status == OBSERVED,
    }
    layers_doc = {
        "aoi_id": stack.aoi_id,
        "crs": "EPSG:4326",
        "bounds_wgs84": proj.bounds,
        "image_coordinates": proj.image_coordinates(),
        "dates": [s.date for s in stack.scenes],
        "layers": layers,
        "attribution": "NISAR data: NASA/JPL-Caltech, via ASF DAAC. Derived by SARPulse (Team StarFire).",
        "data_status": data_status,
    }
    write_json(out / "analysis.json", analysis)
    write_json(out / "time_series.json", time_series)
    write_json(out / "samples.json", _sample_points(stack, cls, before, after))
    write_json(out / "site.json", site)
    write_json(out / "scenes.json", [s.record["scene"] for s in stack.scenes if "scene" in s.record])
    write_json(out / "layers.json", layers_doc)
    return analysis
