"""Integration tests. All radar inputs are SYNTHETIC, not NASA observations."""

import json
from dataclasses import replace

import h5py
import numpy as np
import pytest
import rasterio
from fastapi.testclient import TestClient
from pyproj import Transformer
from rasterio.transform import Affine

from app.main import app
from app.store import Store, get_store
from sarpulse_analysis.change import Params
from sarpulse_analysis.pipeline import run_analysis
from sarpulse_analysis.stack import load_stack
from sarpulse_analysis.validate import binary_metrics, reference_from_points, reference_from_raster
from sarpulse_ingest.access import earthdata_opener
from sarpulse_ingest.ard import SYNTHETIC, build_ard_stack
from sarpulse_ingest.comparability import build_stacks
from sarpulse_platform.artifacts import export_bundle, inspect_site
from sarpulse_platform.cli import main
from science.ingestion.tests.test_ingestion import AOI_SMALL, _make_scene


@pytest.fixture(scope="module")
def investigation(tmp_path_factory):
    root = tmp_path_factory.mktemp("synthetic-integration")
    candidates = [_make_scene(root, "20260722", -8), _make_scene(root, "20261014", -8)]
    for i, c in enumerate(candidates):
        with h5py.File(root / f"{c.scene_id}.h5", "r+") as f:
            for term, db in (("HHHH", -22), ("HVHV", -29)):
                ds = f[f"/science/LSAR/GCOV/grids/frequencyA/{term}"]
                ds[:, 25:50 + i * 25] = 10 ** (db / 10)
    # The default opener must use local files without requiring Earthdata credentials.
    stack = build_stacks(candidates)[0]
    ard = root / "ard"
    build_ard_stack(stack, AOI_SMALL, ard, earthdata_opener(root))
    site = root / "sites" / AOI_SMALL.id
    run_analysis(ard / "stack.json", "2026-07-22", "2026-10-14", site,
                 Params(n_boot=10, tile_px=32, gmm_check=False))
    return root, ard / "stack.json", site


def test_real_handoffs_and_pixel_passport(investigation):
    _, _, site = investigation
    report = inspect_site(site, allow_synthetic=True)
    assert report["data_status"] == SYNTHETIC
    assert not report["independent_reference_compared"]
    manifest = json.loads((site / "layers.json").read_text())
    assert any(l["id"].startswith("hv_db_") for l in manifest["layers"])
    assert any(l["id"] == "delta_hh_db" for l in manifest["layers"])
    with rasterio.open(site / "change_class.tif") as src:
        x, y = src.xy(30, 30)
        lon, lat = Transformer.from_crs(src.crs, "EPSG:4326", always_xy=True).transform(x, y)
        expected_class = {0: "stable_land", 1: "water_gained", 2: "water_lost", 3: "stable_water", 4: "ambiguous"}[src.read(1)[30, 30]]
    store = Store(site.parent)
    app.dependency_overrides[get_store] = lambda: store
    try:
        client = TestClient(app)
        url = f"/api/sites/{site.name}"
        p = client.get(url + "/passport", params={"lon": lon, "lat": lat})
        assert p.status_code == 200, p.text
        p = p.json()
        assert p["change_class"] == expected_class
        assert p["evidence"][0]["label"] == "Unverified"
        assert p["evidence"][0]["values"]["sample_distance_km"] < 0.001
        ts = client.get(url + "/timeseries").json()
        assert "water_area_km2_range" in ts["points"][0]
        assert "threshold_db" in ts["points"][0]
        layers = client.get(url + "/layers").json()
        for layer in layers["layers"]:
            assert client.get(layer["png"]).content.startswith(b"\x89PNG")
        assert client.get(url + "/files/..%2F..%2Fard%2Fstack.json").status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_versioned_delivery_and_synthetic_gate(investigation, tmp_path):
    _, _, site = investigation
    with pytest.raises(ValueError, match="Synthetic"):
        export_bundle(site, tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()
    delivery = tmp_path / "v1"
    metadata = export_bundle(site, delivery, allow_synthetic=True, vectors=True)
    assert metadata["site"]["data_status"] == SYNTHETIC
    assert (delivery / "sites" / site.name / "time_series.csv").is_file()
    assert (delivery / "sites" / site.name / "changes.geojson").is_file()
    assert "README.txt" in metadata["files"]
    import hashlib
    for rel, digest in metadata["files"].items():
        assert hashlib.sha256((delivery / rel).read_bytes()).hexdigest() == digest
    inspect_site(delivery / "sites" / site.name, allow_synthetic=True)
    with pytest.raises(FileExistsError):
        export_bundle(site, delivery, allow_synthetic=True)
    with pytest.raises(ValueError, match="independent reference"):
        inspect_site(site, allow_synthetic=True, require_validation=True)


def test_orchestrator_preserves_runs_and_marks_failed_status(investigation, tmp_path):
    _, stack, _ = investigation
    args = ["run", "--stack", str(stack), "--before", "2026-07-22", "--after", "2026-10-14",
            "--out", str(tmp_path / "run"), "--allow-synthetic", "--no-gmm", "--bootstrap", "10"]
    assert main(args) == 0
    assert json.loads((tmp_path / "run" / "run.json").read_text())["status"] == "complete"
    assert main(args) == 1
    args[args.index("--out") + 1] = str(tmp_path / "failed")
    args.remove("--allow-synthetic")
    assert main(args) == 1
    assert json.loads((tmp_path / "failed" / "run.json").read_text())["status"] == "failed"


def test_mixed_maturity_rejected_before_io(tmp_path):
    a = _make_scene(tmp_path, "20260722", -8)
    b = replace(a, start_utc="2026-10-14T23:05:28Z", maturity="VALIDATED")
    with pytest.raises(ValueError, match="incompatible"):
        build_ard_stack(build_stacks([a, b])[0], AOI_SMALL, tmp_path / "out", lambda c: None)


def test_observed_stack_release_mismatch_rejected(investigation, tmp_path):
    _, path, _ = investigation
    doc = json.loads(path.read_text())
    doc["data_status"] = "observed"
    doc["scenes"][1]["scene"]["crid"] = "INCOMPATIBLE"
    bad = tmp_path / "stack.json"
    bad.write_text(json.dumps(doc))
    with pytest.raises(ValueError, match="crid"):
        load_stack(bad)


def test_one_metre_grid_shift_is_not_silently_accepted(investigation, tmp_path):
    _, path, _ = investigation
    stack = load_stack(path)
    scene = stack.scenes[0]
    source = stack.root / scene.files["HHHH"]
    shifted = tmp_path / "shifted.tif"
    with rasterio.open(source) as src:
        profile, data = src.profile, src.read(1)
    profile["transform"] = Affine.translation(1, 0) * profile["transform"]
    with rasterio.open(shifted, "w", **profile) as dst:
        dst.write(data, 1)
    fake = replace(scene, files=scene.files | {"HHHH": str(shifted)})
    with pytest.raises(ValueError, match="transform differs"):
        stack.read(fake, "HHHH")


def test_zero_f1_and_invalid_reference_labels(investigation, tmp_path):
    assert binary_metrics(np.array([1, 0]), np.array([0, 1]))["f1_water"] == 0
    _, path, _ = investigation
    stack = load_stack(path)
    x, y = stack.grid.affine * (30.5, 30.5)
    lon, lat = Transformer.from_crs(stack.grid.epsg, 4326, always_xy=True).transform(x, y)
    bad = tmp_path / "labels.geojson"
    bad.write_text(json.dumps({"features": [{"geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": {"water": "false"}}]}))
    with pytest.raises(ValueError, match="boolean"):
        reference_from_points(bad, stack.grid)


def test_reference_nan_is_not_nonwater(investigation, tmp_path):
    _, path, _ = investigation
    stack = load_stack(path)
    ref = tmp_path / "reference.tif"
    arr = np.ones((stack.grid.height, stack.grid.width), "float32")
    arr[2, 3] = np.nan
    with rasterio.open(ref, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1,
                       crs=stack.grid.epsg, transform=stack.grid.affine, dtype="float32", nodata=np.nan) as dst:
        dst.write(arr, 1)
    result = reference_from_raster(ref, stack.grid, {1})
    assert result[2, 3] == -1
    assert result[20, 20] == 1
