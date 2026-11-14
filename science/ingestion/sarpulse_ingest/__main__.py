"""Command line: `python -m sarpulse_ingest {search,ard} ...` (run from science/ingestion/)."""

import argparse
import json
import sys
from dataclasses import fields
from datetime import date
from pathlib import Path

from .aoi import load_aoi
from .catalog import CandidateScene, search_gcov
from .comparability import Stack, build_stacks

REPO = Path(__file__).resolve().parents[3]


def _write(path: Path, doc) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path}")


def cmd_search(args) -> int:
    aoi = load_aoi(args.aoi)
    candidates, query = search_gcov(aoi, args.start, args.end)
    stacks = build_stacks(candidates, min_dates=2)
    out = Path(args.out_dir or REPO / "data" / "manifests" / aoi.id)
    _write(out / "gcov_candidates.json", {"aoi": {"id": aoi.id, "bbox": aoi.bbox()}, "query": query, "candidates": [c.to_dict() for c in candidates]})
    _write(out / "comparable_stacks.json", {"aoi_id": aoi.id, "retrieved_utc": query["retrieved_utc"], "stacks": [s.to_dict() for s in stacks]})
    print(f"\n{len(candidates)} GCOV products; {len(stacks)} comparable stacks (>= 2 dates):")
    for s in stacks:
        print(f"  {s.stack_id:<45} {len(s.scenes):>2} dates  {s.scenes[0].start_utc[:10]} .. {s.scenes[-1].start_utc[:10]}")
        for w in s.warnings:
            print(f"      ! {w}")
    return 0


def _load_stack(manifest_dir: Path, stack_id: str) -> Stack:
    cands = json.loads((manifest_dir / "gcov_candidates.json").read_text())["candidates"]
    by_id = {c["scene_id"]: CandidateScene(**{f.name: c[f.name] for f in fields(CandidateScene)}) for c in cands}
    stacks = json.loads((manifest_dir / "comparable_stacks.json").read_text())["stacks"]
    match = [s for s in stacks if s["stack_id"] == stack_id]
    if not match:
        sys.exit(f"stack {stack_id!r} not in {manifest_dir}/comparable_stacks.json")
    s = match[0]
    return Stack(key=s["key"], scenes=[by_id[i] for i in s["scenes"]], warnings=s["warnings"])


def cmd_ard(args) -> int:
    from .access import earthdata_opener, local_opener
    from .ard import build_ard_stack

    aoi = load_aoi(args.aoi)
    manifest_dir = Path(args.manifest_dir or REPO / "data" / "manifests" / aoi.id)
    stack = _load_stack(manifest_dir, args.stack_id)
    if args.dates:
        wanted = set(args.dates.split(","))
        stack.scenes = [c for c in stack.scenes if c.start_utc[:10] in wanted]
        missing = wanted - {c.start_utc[:10] for c in stack.scenes}
        if missing:
            sys.exit(f"no scene in {stack.stack_id} on {sorted(missing)}")
    try:
        opener = local_opener(Path(args.local_dir)) if args.offline else earthdata_opener(Path(args.local_dir) if args.local_dir else None)
    except PermissionError as err:
        sys.exit(str(err))
    out = Path(args.out or REPO / "data" / "processed" / aoi.id)
    doc = build_ard_stack(stack, aoi, out, opener, multilook=args.multilook)
    print(f"wrote {out / 'stack.json'}: {len(doc['scenes'])} scenes, grid {doc['grid']['width']}x{doc['grid']['height']} @ {doc['grid']['pixel_spacing_m']} m, status={doc['data_status']}")
    for e in doc["excluded_scenes"]:
        print(f"  excluded {e['scene_id']}: {e['reason']}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="sarpulse_ingest", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="find NISAR GCOV products over an AOI and group comparable stacks")
    s.add_argument("--aoi", required=True, help="GeoJSON AOI (data/aoi/*.geojson)")
    s.add_argument("--start", type=date.fromisoformat)
    s.add_argument("--end", type=date.fromisoformat)
    s.add_argument("--out-dir", help="default: data/manifests/<aoi id>/")
    s.set_defaults(func=cmd_search)

    a = sub.add_parser("ard", help="build an analysis-ready stack for one comparable stack")
    a.add_argument("--aoi", required=True)
    a.add_argument("--stack-id", required=True, help="stack_id from comparable_stacks.json")
    a.add_argument("--dates", help="comma-separated YYYY-MM-DD subset of the stack's dates")
    a.add_argument("--manifest-dir", help="default: data/manifests/<aoi id>/")
    a.add_argument("--local-dir", help="directory with downloaded <scene_id>.h5 files (used first)")
    a.add_argument("--offline", action="store_true", help="only use --local-dir, never stream")
    a.add_argument("--multilook", type=int, default=2, help="k x k averaging in linear power (default 2)")
    a.add_argument("--out", help="default: data/processed/<aoi id>/ (git-ignored)")
    a.set_defaults(func=cmd_ard)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
