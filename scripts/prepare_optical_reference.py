"""Prepare a cloud-masked Sentinel-2 SCL water reference without treating it as field truth."""
import argparse
import json
from pathlib import Path

import numpy as np
import rasterio


def prepare(source: Path, out: Path):
    with rasterio.open(source) as src:
        scl = src.read(1, masked=True)
        valid = ~np.ma.getmaskarray(scl) & np.isin(scl.data, [4, 5, 6])
        ref = np.where(valid, (scl.data == 6).astype("uint8"), 255).astype("uint8")
        profile = src.profile | {"dtype": "uint8", "count": 1, "nodata": 255, "compress": "deflate"}
        out.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(out, "w", **profile) as dst:
            dst.write(ref, 1)
            dst.update_tags(source="Sentinel-2 L2A Scene Classification", water="SCL 6", land="SCL 4 or 5",
                            caveat="Automated optical reference; not field truth. Cloud/invalid classes excluded.")
    return {"valid_fraction": float(valid.mean()), "water_pixels": int((ref == 1).sum()), "path": str(out)}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scl", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prepare(a.scl, a.out), indent=2))
