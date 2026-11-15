import json
import shutil
from datetime import date
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("rasterio")

from app.schemas import ContextRecord, SamplePoint  # noqa: E402
from context_adapters import imerg, rasters  # noqa: E402
from context_adapters.__main__ import enrich  # noqa: E402

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "demo-brahmaputra"


def test_tile_urls():
    assert rasters.dem_tile_urls(93.9, 26.8, 94.3, 27.1) == [
        rasters.COP_DEM_URL.format(ns="N", lat=26, ew="E", lon=93),
        rasters.COP_DEM_URL.format(ns="N", lat=26, ew="E", lon=94),
        rasters.COP_DEM_URL.format(ns="N", lat=27, ew="E", lon=93),
        rasters.COP_DEM_URL.format(ns="N", lat=27, ew="E", lon=94),
    ]
    assert rasters.jrc_tile_urls(93.9, 26.8, 94.3, 27.1) == [
        rasters.JRC_OCC_URL.format(lon=90, ew="E", lat=30, ns="N")
    ]


def test_slope_of_known_ramp():
    # Elevation rising 1 m per metre northward-ish -> 45 deg. Build along x at the equator.
    xres = 1 / 3600
    metres_per_px = xres * 111_320.0
    x = np.arange(50) * metres_per_px
    dem = rasters.GeoArray(np.tile(x, (50, 1)).astype("float32"), 0.0, 0.0 + 25 * xres, xres, xres)
    s = rasters.slope_degrees(dem)
    assert abs(float(np.median(s.data)) - 45.0) < 0.5


def test_geoarray_sample_bounds():
    g = rasters.GeoArray(np.array([[1.0, 2.0], [3.0, np.nan]], dtype="float32"), 10.0, 20.0, 1.0, 1.0)
    assert g.sample(10.5, 19.5) == 1.0
    assert g.sample(11.5, 18.5) is None  # nan
    assert g.sample(50, 50) is None  # outside


def _fake_h5(path: Path, value: float):
    import h5py

    with h5py.File(path, "w") as f:
        g = f.create_group("Grid")
        g["lon"] = np.arange(93.05, 95.0, 0.1)
        g["lat"] = np.arange(26.05, 28.0, 0.1)
        p = np.full((1, g["lon"].shape[0], g["lat"].shape[0]), value, dtype="float32")
        p[0, 0, 0] = -9999.9  # fill outside AOI must not matter
        g["precipitation"] = p


def test_imerg_file_mean_and_accumulate(tmp_path):
    f = tmp_path / "d.h5"
    _fake_h5(f, 4.0)
    assert imerg.aoi_mean_mm(f, (93.9, 26.8, 94.3, 27.1)) == pytest.approx(4.0)
    daily = {date(2026, 7, 1): 4.0, date(2026, 7, 2): None, date(2026, 7, 3): 6.0}
    assert imerg.accumulate(daily, date(2026, 7, 1), date(2026, 7, 4)) == (10.0, 2, 3)


def test_enrich_site(tmp_path):
    site = tmp_path / "demo-brahmaputra"
    shutil.copytree(FIXTURE, site)
    (site / "context.json").unlink()

    const = lambda v: (lambda bbox: rasters.GeoArray(np.full((40, 40), v, "float32"), 93.8, 27.2, 0.02, 0.02))  # noqa: E731
    records = enrich(
        site, rain=True, slope_loader=const(12.0), jrc_loader=const(80.0),
        rain_fetcher=lambda bbox, s, e: {date(2026, 7, d): 5.0 for d in range(1, 25)},
    )
    kinds = {r["kind"]: r for r in records}
    assert kinds["dem_slope"]["value"] == 100.0
    assert kinds["jrc_gsw_occurrence"]["value"] == 100.0
    assert kinds["rainfall_imerg"]["value"] == 120.0  # 24 days, Jul 1-24 ([before, after))
    for r in records:
        ContextRecord.model_validate(r)
    samples = [SamplePoint.model_validate(s) for s in json.loads((site / "samples.json").read_text("utf-8"))]
    assert all(s.slope_deg == 12.0 and s.jrc_occurrence_pct == 80.0 for s in samples)

    # Re-running replaces rather than duplicates records.
    enrich(site, dem=False, jrc=False, rain=True,
           rain_fetcher=lambda bbox, s, e: {})
    kinds2 = [r["kind"] for r in json.loads((site / "context.json").read_text("utf-8"))]
    assert sorted(kinds2) == ["dem_slope", "jrc_gsw_occurrence", "rainfall_imerg"]
