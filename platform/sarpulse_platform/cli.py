"""Shared runner: ingest -> analyse -> inspect -> export -> serve."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .artifacts import export_bundle, inspect_site, utc_now, write_json


def run(args) -> dict:
    from sarpulse_analysis.change import Params
    from sarpulse_analysis.pipeline import run_analysis
    from sarpulse_ingest.__main__ import _load_stack
    from sarpulse_ingest.access import earthdata_opener, local_opener
    from sarpulse_ingest.aoi import load_aoi
    from sarpulse_ingest.ard import build_ard_stack

    out = args.out.resolve()
    if out.exists():
        raise FileExistsError("Run output exists; choose a new run ID to preserve previous results")
    if args.stack:
        stack_path = args.stack.resolve()
        if not stack_path.is_file():
            raise FileNotFoundError(stack_path)
    else:
        if not args.aoi or not args.stack_id or not args.manifest_dir:
            raise ValueError("Provide --stack, or --aoi, --stack-id and --manifest-dir")
        if args.offline and not args.local_dir:
            raise ValueError("--offline requires --local-dir")
    out.mkdir(parents=True)
    state = {"schema_version": "sarpulse.run.v0", "started_utc": utc_now(), "status": "running", "phases": []}
    write_json(out / "run.json", state)
    try:
        if not args.stack:
            aoi = load_aoi(args.aoi)
            stack = _load_stack(args.manifest_dir, args.stack_id)
            wanted = {args.before, args.after}
            stack.scenes = [c for c in stack.scenes if c.scene_id in wanted or c.start_utc[:10] in wanted]
            if len(stack.scenes) != 2:
                raise ValueError("Before/after must select exactly two catalog acquisitions")
            from sarpulse_ingest.comparability import build_stacks
            stack = build_stacks(stack.scenes)[0]
            write_json(out / "input_manifest.json", {"aoi": json.loads(args.aoi.read_text(encoding="utf-8")),
                       "stack": stack.to_dict(), "scenes": [c.to_dict() for c in stack.scenes]})
            opener = local_opener(args.local_dir) if args.offline else earthdata_opener(args.local_dir)
            build_ard_stack(stack, aoi, out / "ard", opener, args.multilook)
            stack_path = out / "ard" / "stack.json"
            state["phases"].append("ingestion")
            write_json(out / "run.json", state)
        else:
            write_json(out / "input_manifest.json", json.loads(stack_path.read_text(encoding="utf-8")))
        stack_doc = json.loads(stack_path.read_text(encoding="utf-8"))
        site_id = stack_doc["aoi"]["id"]
        # Defend the shared output root from a malformed AOI identifier.
        import re
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", site_id):
            raise ValueError("Unsafe AOI identifier")
        site_dir = out / "sites" / site_id
        run_analysis(stack_path, args.before, args.after, site_dir,
                     Params(gmm_check=not args.no_gmm, n_boot=args.bootstrap))
        state["phases"].append("analysis")
        if args.context or args.imerg:
            from context_adapters.__main__ import enrich
            enrich(site_dir, dem=args.context, jrc=args.context, rain=args.imerg)
            state["phases"].append("context")
        state["inspection"] = inspect_site(site_dir, allow_synthetic=args.allow_synthetic)
        state["phases"].append("contract_check")
        if args.export:
            export_bundle(site_dir, args.export, args.allow_synthetic, vectors=args.vectors)
            state["phases"].append("export")
        state.update(status="complete", completed_utc=utc_now(), site_dir=str(site_dir))
    except Exception as err:
        state.update(status="failed", failed_utc=utc_now(), error_type=type(err).__name__)
        write_json(out / "run.json", state)
        raise
    write_json(out / "run.json", state)
    return state


def doctor() -> dict:
    import importlib.util
    import platform
    import netrc

    credential_file = False
    paths = [Path(os.environ["NETRC"])] if os.environ.get("NETRC") else [Path.home()/".netrc", Path.home()/"_netrc"]
    for credential_path in paths:
        try:
            credential_file |= bool(netrc.netrc(str(credential_path)).authenticators("urs.earthdata.nasa.gov"))
        except (OSError, netrc.NetrcParseError):
            pass
    return {"python": platform.python_version(), "modules": {
        m: importlib.util.find_spec(m) is not None for m in ("numpy", "rasterio", "h5py", "scipy", "sklearn", "earthaccess", "fastapi")},
        "earthdata_credentials_available": bool(credential_file or os.environ.get("EARTHDATA_TOKEN") or
                                                 (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"))),
        "note": "Credential presence only; this does not verify authentication. Offline local GCOV files need no login."}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    # Keep the science teams' existing CLIs intact behind one shared entry point.
    if argv and argv[0] in ("search", "validate", "context"):
        if argv[0] == "search":
            from sarpulse_ingest.__main__ import main as delegate
            return delegate(argv)
        if argv[0] == "validate":
            from sarpulse_analysis.__main__ import main as delegate
            return delegate(argv)
        from context_adapters.__main__ import main as delegate
        delegate(argv[1:])
        return 0
    p = argparse.ArgumentParser(prog="sarpulse", description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="check dependencies and credential presence without printing secrets")
    sub.add_parser("contracts", help="write OpenAPI and JSON Schema definitions into contracts/")
    r = sub.add_parser("run", help="run a versioned investigation from a stack or catalog pair")
    r.add_argument("--stack", type=Path)
    r.add_argument("--aoi", type=Path)
    r.add_argument("--stack-id")
    r.add_argument("--manifest-dir", type=Path)
    r.add_argument("--before", required=True)
    r.add_argument("--after", required=True)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--local-dir", type=Path)
    r.add_argument("--offline", action="store_true")
    r.add_argument("--multilook", type=int, default=2)
    r.add_argument("--context", action="store_true", help="fetch DEM and historical-water context")
    r.add_argument("--imerg", action="store_true", help="fetch rainfall context; requires Earthdata access")
    r.add_argument("--no-gmm", action="store_true")
    r.add_argument("--bootstrap", type=int, default=200)
    r.add_argument("--allow-synthetic", action="store_true")
    r.add_argument("--export", type=Path)
    r.add_argument("--vectors", action="store_true")
    for name in ("inspect", "export"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--site", type=Path, required=True)
        cmd.add_argument("--allow-synthetic", action="store_true")
        cmd.add_argument("--require-validation", action="store_true")
        if name == "export":
            cmd.add_argument("--out", type=Path, required=True)
            cmd.add_argument("--vectors", action="store_true")
    s = sub.add_parser("serve", help="serve precomputed evidence and layers")
    s.add_argument("--data-dir", type=Path, required=True)
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    args = p.parse_args(argv)
    try:
        if args.command == "doctor":
            result = doctor()
        elif args.command == "run":
            result = run(args)
        elif args.command == "inspect":
            result = inspect_site(args.site, args.allow_synthetic, args.require_validation)
        elif args.command == "export":
            result = export_bundle(args.site, args.out, args.allow_synthetic, args.require_validation, args.vectors)
        elif args.command == "contracts":
            from app.main import app
            from app import schemas
            out = Path("contracts")
            write_json(out / "openapi.json", app.openapi())
            for name in ("Site", "Scene", "Analysis", "TimeSeries", "SamplePoint", "LayersManifest", "ChangePassport", "ContextRecord"):
                write_json(out / f"{name}.schema.json", getattr(schemas, name).model_json_schema())
            result = {"contracts": str(out.resolve())}
        else:
            import uvicorn
            from app.config import settings
            from app.store import get_store
            if not args.data_dir.is_dir():
                raise FileNotFoundError(args.data_dir)
            settings.data_dir = args.data_dir.resolve()
            get_store.cache_clear()
            from app.main import app
            uvicorn.run(app, host=args.host, port=args.port)
            return 0
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ValueError, KeyError, FileNotFoundError, FileExistsError, PermissionError, RuntimeError) as err:
        print(f"{type(err).__name__}: {err}", file=sys.stderr)
        return 1
