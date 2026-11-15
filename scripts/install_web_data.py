"""Install an inspected precomputed delivery into the static app without copying credentials or raw products."""
import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/p) for p in ("api", "platform")]
from sarpulse_platform.artifacts import inspect_site


def install(bundle: Path, target: Path, allow_synthetic=False):
    bundle, target = bundle.resolve(), target.resolve()
    sites = json.loads((bundle/"sites.json").read_text(encoding="utf-8"))
    for site in sites:
        inspect_site(bundle/"sites"/site["id"], allow_synthetic=allow_synthetic)
    existing = json.loads((target/"sites.json").read_text(encoding="utf-8")) if (target/"sites.json").is_file() else []
    if any((target/"sites"/s["id"]).exists() for s in sites):
        raise FileExistsError("This site already exists in the target; use a versioned release directory")
    if bundle == target or bundle.is_relative_to(target) or target.is_relative_to(bundle):
        raise ValueError("Source and target must be separate")
    for path in bundle.rglob("*"):
        if path.is_file():
            if path.suffix.lower() not in (".json", ".csv", ".png", ".tif", ".tiff", ".geojson", ".txt"):
                raise ValueError(f"Unexpected delivery asset: {path.name}")
            if path.stat().st_size > 20 * 1024 * 1024:
                raise ValueError(f"Delivery asset exceeds static hosting limit: {path.name}")
    if target.exists():
        for site in sites:
            shutil.copytree(bundle/"sites"/site["id"],target/"sites"/site["id"])
        (target/"sites.json").write_text(json.dumps(existing+sites,indent=2)+"\n",encoding="utf-8")
        shutil.copy2(bundle/"artifact.json",target/f"artifact-{sites[0]['id']}.json")
    else:
        shutil.copytree(bundle,target)
    return {"site_ids":[s["id"] for s in sites],"target":str(target)}


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bundle",type=Path,required=True)
    p.add_argument("--target",type=Path,default=ROOT/"web/public/data")
    p.add_argument("--allow-synthetic",action="store_true")
    a=p.parse_args()
    print(json.dumps(install(a.bundle,a.target,a.allow_synthetic),indent=2))
