"""Command line: `python -m sarpulse_analysis {run,validate} ...` (run from science/analysis/)."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import rasterio

from .change import Params
from .pipeline import run_analysis
from .stack import load_stack
from .validate import validate_water_map


def cmd_run(args) -> int:
    stack_path = Path(args.stack)
    out = Path(args.out or stack_path.parent / "analysis")
    params = Params(
        speckle_filter="none" if args.no_speckle_filter else "lee",
        filter_size=args.filter_size,
        tile_px=args.tile_px,
        margin_db=args.margin_db,
        min_change_db=args.min_change_db,
        gmm_check=not args.no_gmm,
    )
    a = run_analysis(stack_path, args.before, args.after, out, params)
    print(f"wrote {out}/ (data_status={a['data_status']})")
    print(f"  valid {a['valid_area_km2']} km2 | gained {a['gained_water_km2']} km2 {a['area_ranges_km2']['water_gained']} | lost {a['lost_water_km2']} km2 {a['area_ranges_km2']['water_lost']} | ambiguous {a['ambiguous_km2']} km2")
    for date, t in a["thresholds"].items():
        print(f"  {date}: threshold {t['threshold_db']} +/- {t['uncertainty_db']} dB, {t['method']}, flags={t['flags']}")
    return 0


def cmd_validate(args) -> int:
    out = Path(args.analysis_dir)
    stack = load_stack(args.stack)
    scene = stack.scene(args.date)
    with rasterio.open(out / "water" / f"{scene.date}.tif") as r:
        wm = r.read(1)
    water, valid = wm == 1, wm != 255
    metrics = validate_water_map(water, valid, stack.grid, Path(args.reference), args.kind, tuple(int(v) for v in args.water_values.split(",")), args.label_field)
    record = {
        "scene_id": scene.scene_id,
        "date": scene.date,
        "reference": {"path": str(args.reference), "kind": args.kind, "description": args.reference_name},
        "reference_caveat": args.reference_caveat,
        "metrics": metrics,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    vpath = out / "validation" / f"{scene.date}.json"
    vpath.parent.mkdir(parents=True, exist_ok=True)
    vpath.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    analysis_path = out / "analysis.json"
    analysis = json.loads(analysis_path.read_text())
    analysis.setdefault("validation", [])
    analysis["validation"] = [v for v in analysis["validation"] if v["date"] != scene.date] + [record]
    analysis["validation_status"] = "; ".join(
        f"{v['date']} vs {v['reference']['description']}: OA {v['metrics']['overall_accuracy']} (95% CI {v['metrics']['overall_accuracy_95ci']}), F1 water {v['metrics']['f1_water']}, n={v['metrics']['n']}"
        for v in analysis["validation"]
    )
    if args.reference_caveat:
        analysis["validation_status"] = "Reference agreement (not field accuracy): " + analysis["validation_status"]
        if args.reference_caveat not in analysis["limitations"]:
            analysis["limitations"].append(args.reference_caveat)
    analysis_path.write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    if metrics["n"] < 100:
        print(f"warning: only {metrics['n']} reference samples; treat metrics as indicative", file=sys.stderr)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sarpulse_analysis", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="water maps, change classes, time series and exports for one stack")
    r.add_argument("--stack", required=True, help="stack.json from science/ingestion")
    r.add_argument("--before", required=True, help="scene id or YYYY-MM-DD")
    r.add_argument("--after", required=True, help="scene id or YYYY-MM-DD")
    r.add_argument("--out", help="default: <stack dir>/analysis/")
    r.add_argument("--no-speckle-filter", action="store_true")
    r.add_argument("--filter-size", type=int, default=5)
    r.add_argument("--tile-px", type=int, default=64)
    r.add_argument("--margin-db", type=float, default=0.5, help="minimum half-width of the threshold uncertainty band")
    r.add_argument("--min-change-db", type=float, default=3.0, help="minimum |delta HH| for a water gain/loss")
    r.add_argument("--no-gmm", action="store_true", help="skip the Gaussian-mixture consistency check")
    r.set_defaults(func=cmd_run)

    v = sub.add_parser("validate", help="accuracy of one date's water map against an independent reference")
    v.add_argument("--stack", required=True)
    v.add_argument("--analysis-dir", required=True)
    v.add_argument("--date", required=True, help="scene id or YYYY-MM-DD")
    v.add_argument("--reference", required=True, help="GeoJSON points or reference raster")
    v.add_argument("--kind", choices=["points", "raster"], required=True)
    v.add_argument("--reference-name", required=True, help="e.g. 'Sentinel-2 NDWI 2026-07-23, manual labels'")
    v.add_argument("--reference-caveat", default="", help="Temporal/reference-method limitations retained with metrics")
    v.add_argument("--water-values", default="1", help="raster values meaning water (comma-separated)")
    v.add_argument("--label-field", default="water", help="boolean property on reference points")
    v.set_defaults(func=cmd_validate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
