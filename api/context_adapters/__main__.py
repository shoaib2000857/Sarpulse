"""Enrich a site folder with contextual evidence.

    python -m context_adapters <site_dir> [--no-dem] [--no-jrc] [--imerg]

Reads site.json / analysis.json / scenes.json / samples.json, then:
- fills samples[*].slope_deg (Copernicus DEM GLO-30) and jrc_occurrence_pct (JRC GSW v1.4)
- writes context.json with AOI-level records (+ IMERG rainfall between the two dates if --imerg)

Results are cached in the site folder so the demo never fetches live.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import numpy as np

from . import imerg, rasters

OBSERVED = "observed"
STEEP_DEG = 10.0
JRC_WATER_PCT = 50.0


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _dump(p: Path, doc) -> None:
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def _share(arr: np.ndarray, pred) -> float | None:
    ok = np.isfinite(arr)
    return round(float(pred(arr[ok]).mean() * 100), 1) if ok.any() else None


def scene_dates(site_dir: Path) -> tuple[date, date]:
    a = _load(site_dir / "analysis.json")
    by_id = {s["scene_id"]: s for s in _load(site_dir / "scenes.json")}
    d = [date.fromisoformat(by_id[k]["acquired_at_utc"][:10]) for k in (a["before_scene_id"], a["after_scene_id"])]
    return d[0], d[1]


def enrich(site_dir: Path, dem: bool = True, jrc: bool = True, rain: bool = False,
           slope_loader=rasters.load_slope, jrc_loader=rasters.load_jrc_occurrence,
           rain_fetcher=imerg.fetch_daily) -> list[dict]:
    site = _load(site_dir / "site.json")
    b = site["bbox"]
    bbox = (b["west"], b["south"], b["east"], b["north"])
    samples = _load(site_dir / "samples.json")
    ctx_path = site_dir / "context.json"
    replaced = {k for k, on in (("dem_slope", dem), ("jrc_gsw_occurrence", jrc), ("rainfall_imerg", rain)) if on}
    records = [r for r in (_load(ctx_path) if ctx_path.is_file() else []) if r["kind"] not in replaced]

    if dem:
        slope = slope_loader(bbox)
        for s in samples:
            v = slope.sample(s["lon"], s["lat"])
            s["slope_deg"] = None if v is None else round(v, 1)
        records.append({
            "kind": "dem_slope", "source": "Copernicus DEM GLO-30 (ESA / AWS Open Data)",
            "value": _share(slope.data, lambda x: x > STEEP_DEG), "units": f"% of AOI with slope > {STEEP_DEG:g} deg",
            "resolution": "30 m", "period_start": None, "period_end": None,
            "caveat": "Terrain context. Steep slopes cause radar layover/shadow; changes there are unreliable.",
            "data_status": OBSERVED,
        })
    if jrc:
        occ = jrc_loader(bbox)
        for s in samples:
            s["jrc_occurrence_pct"] = occ.sample(s["lon"], s["lat"])
        records.append({
            "kind": "jrc_gsw_occurrence", "source": "EC JRC Global Surface Water v1.4 (Landsat, 1984-2021)",
            "value": _share(occ.data, lambda x: x >= JRC_WATER_PCT),
            "units": f"% of AOI water in >= {JRC_WATER_PCT:g}% of historical observations",
            "resolution": "30 m", "period_start": "1984-03-16", "period_end": "2021-12-31",
            "caveat": "Historical optical context, not 2026 ground truth. Braided channels migrate.",
            "data_status": OBSERVED,
        })
    if rain:
        start, end = scene_dates(site_dir)
        total, have, expected = imerg.accumulate(rain_fetcher(bbox, start, end), start, end)
        records.append({
            "kind": "rainfall_imerg", "source": f"NASA GPM IMERG V07 daily ({imerg.DEFAULT_SHORT_NAME})",
            "value": total, "units": "mm (AOI mean, accumulated)", "resolution": "0.1 deg (~10 km)",
            "period_start": start.isoformat(), "period_end": end.isoformat(),
            "caveat": f"Context only, not proof of cause. {have}/{expected} days available; "
                      "satellite estimate with known biases; upstream rain and river flow also matter.",
            "data_status": OBSERVED,
        })

    _dump(site_dir / "samples.json", samples)
    _dump(ctx_path, records)
    return records


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="python -m context_adapters", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site_dir", type=Path)
    ap.add_argument("--no-dem", action="store_true")
    ap.add_argument("--no-jrc", action="store_true")
    ap.add_argument("--imerg", action="store_true", help="needs Earthdata Login")
    a = ap.parse_args(argv)
    for r in enrich(a.site_dir, dem=not a.no_dem, jrc=not a.no_jrc, rain=a.imerg):
        print(f"{r['kind']}: {r['value']} {r['units']}")


if __name__ == "__main__":
    main()
