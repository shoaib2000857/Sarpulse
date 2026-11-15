import json
from pathlib import Path

import numpy as np
import pytest
import rasterio

from sarpulse_ingest.access import local_opener
from sarpulse_ingest.aoi import AOI, aoi_grid
from sarpulse_ingest.ard import SYNTHETIC, build_ard_stack
from sarpulse_ingest.catalog import CandidateScene, candidate_from_feature, maturity_from_collection
from sarpulse_ingest.comparability import build_stacks
from sarpulse_ingest.granule import parse_granule_name

from science.ingestion.tests.synthetic_gcov import write_synthetic_gcov

# Real product name format as listed by ASF (used only to test parsing).
NAME = "NISAR_L2_PR_GCOV_026_040_A_015_4005_DHDH_A_20260722T230528_20260722T230602_P05023_N_F_J_001"
AOI_SMALL = AOI(id="test-aoi", name="test", west=94.00, south=26.90, east=94.02, north=26.92)
API_SCENE_FIELDS = {
    "scene_id", "source", "acquired_at_utc", "maturity", "crid", "orbit_direction", "relative_orbit",
    "polarizations", "grid_epsg", "pixel_spacing_m", "footprint", "license", "data_url", "data_status",
}


def test_parse_granule_name():
    g = parse_granule_name(NAME + ".h5")
    assert (g.processing_type, g.cycle, g.track, g.direction, g.frame) == ("PR", 26, 40, "ASCENDING", 15)
    assert (g.mode, g.polarization, g.crid, g.orbit_accuracy, g.coverage, g.counter) == ("4005", "DHDH", "P05023", "N", "F", 1)
    assert g.primary_bandwidth_mhz == 40
    assert g.start.isoformat() == "2026-07-22T23:05:28+00:00"
    with pytest.raises(ValueError):
        parse_granule_name("S1A_IW_GRDH_1SDV_20260722")


def test_maturity_from_collection():
    assert maturity_from_collection("NISAR_L2_GCOV_PROVISIONAL_V1") == "PROVISIONAL"
    assert maturity_from_collection("NISAR_L2_GCOV_BETA_V1") == "BETA"
    assert maturity_from_collection("NISAR_L2_GCOV_V1") == "VALIDATED"
    assert maturity_from_collection("NISAR_UR_L2") == "URGENT_RESPONSE"


def _feature(name: str, collection="NISAR_L2_GCOV_PROVISIONAL_V1", pols=("HH", "HV")) -> dict:
    g = parse_granule_name(name)
    return {
        "geometry": {"coordinates": [[[93.0, 25.3], [95.6, 25.9], [94.9, 28.1], [92.4, 27.5], [93.0, 25.3]]]},
        "properties": {
            "sceneName": name,
            "url": f"https://example.invalid/{name}.h5",
            "collectionName": collection,
            "startTime": g.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "stopTime": g.end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "mainBandPolarization": list(pols),
        },
    }


def _name(date: str, crid="P05023", counter=1, ptype="PR", track="040", mode="4005") -> str:
    return f"NISAR_L2_{ptype}_GCOV_026_{track}_A_015_{mode}_DHDH_A_{date}T230528_{date}T230602_{crid}_N_F_J_{counter:03d}"


def test_candidate_from_feature():
    c = candidate_from_feature(_feature(NAME))
    assert c.scene_id == NAME and c.maturity == "PROVISIONAL" and c.track == 40
    assert c.footprint_bbox == {"west": 92.4, "south": 25.3, "east": 95.6, "north": 28.1}


def test_build_stacks_splits_incomparable_and_dedupes():
    cands = [
        candidate_from_feature(_feature(_name("20260710"))),
        candidate_from_feature(_feature(_name("20260722"))),
        candidate_from_feature(_feature(_name("20260722", counter=2))),  # reprocessed duplicate
        candidate_from_feature(_feature(_name("20260803", crid="P05036"))),  # other software release
        candidate_from_feature(_feature(_name("20260815", mode="2005"))),  # other bandwidth
        candidate_from_feature(_feature(_name("20260827"), pols=("HH",))),  # lacks HV
    ]
    stacks = build_stacks(cands, min_dates=2)
    assert len(stacks) == 1
    s = stacks[0]
    assert s.stack_id == "T040A_F015_4005_DHDH_PR_P05023"
    assert [c.counter for c in s.scenes] == [1, 2]
    assert any("Superseded" in w for w in s.warnings)


def _make_scene(tmp_path: Path, date: str, hh_db: float, shift_m: float = 0.0, invalid_block=False) -> CandidateScene:
    grid = aoi_grid(AOI_SMALL, 32646, 20.0)
    margin = 60.0
    x = np.arange(grid.x0 - margin + 5, grid.x0 + grid.width * 20 + margin, 10.0) + shift_m
    y = np.arange(grid.y0 + margin - 5, grid.y0 - grid.height * 20 - margin, -10.0) + shift_m
    hh = np.full((y.size, x.size), 10 ** (hh_db / 10), dtype=np.float32)
    hv = hh / 10
    mask = np.full(hh.shape, 2, dtype=np.uint8)
    mask[:, :3] = 255  # outside acquisition
    if invalid_block:
        mask[20:22, 20:21] = 0  # partially focused samples
    name = _name(date)
    start = f"{date[:4]}-{date[4:6]}-{date[6:]}T23:05:28.000000000"
    write_synthetic_gcov(tmp_path / f"{name}.h5", name, x, y, hh, hv, mask, start=start)
    return candidate_from_feature(_feature(name))


def test_build_ard_stack_aligned(tmp_path):
    cands = [_make_scene(tmp_path, "20260722", -8.0, invalid_block=True), _make_scene(tmp_path, "20261014", -18.0)]
    stack = build_stacks(cands)[0]
    out = tmp_path / "out"
    doc = build_ard_stack(stack, AOI_SMALL, out, local_opener(tmp_path), multilook=2)

    assert doc["data_status"] == SYNTHETIC
    assert doc["grid"]["pixel_spacing_m"] == 20.0 and doc["grid"]["epsg"] == 32646
    assert [s["acquired_at_utc"] for s in doc["scenes"]] == ["2026-07-22T23:05:28Z", "2026-10-14T23:05:28Z"]
    first = doc["scenes"][0]
    assert "exact 2x2" in first["resampling"] and first["warnings"] == []

    with rasterio.open(out / first["files"]["HHHH"]) as r:
        hh = r.read(1)
        assert r.crs.to_epsg() == 32646 and r.res == (20.0, 20.0)
    with rasterio.open(out / first["files"]["valid"]) as r:
        valid = r.read(1).astype(bool)
    # Values are preserved in linear power and invalid native pixels invalidate their block.
    np.testing.assert_allclose(hh[valid], 10 ** (-8.0 / 10), rtol=1e-6)
    assert 0 < (~valid).sum() < 10 and np.isnan(hh[~valid]).all()
    with rasterio.open(out / first["files"]["number_of_looks"]) as r:
        assert np.nanmax(r.read(1)) == 16.0  # 4 looks x 4 native pixels

    scenes = json.loads((out / "scenes.json").read_text())
    assert all(set(s) == API_SCENE_FIELDS and s["data_status"] == SYNTHETIC for s in scenes)


def test_build_ard_stack_reprojects_unaligned_grid(tmp_path):
    cands = [_make_scene(tmp_path, "20260722", -8.0, shift_m=3.0), _make_scene(tmp_path, "20261014", -18.0, shift_m=3.0)]
    doc = build_ard_stack(build_stacks(cands)[0], AOI_SMALL, tmp_path / "out", local_opener(tmp_path))
    assert "reprojection" in doc["scenes"][0]["resampling"]
    with rasterio.open(tmp_path / "out" / doc["scenes"][1]["files"]["HHHH"]) as r:
        hh = r.read(1)
    np.testing.assert_allclose(np.nanmedian(hh), 10 ** (-18.0 / 10), rtol=1e-5)


def test_scene_outside_aoi_is_excluded(tmp_path):
    a = _make_scene(tmp_path, "20260722", -8.0)
    b = _make_scene(tmp_path, "20261014", -18.0)
    far = AOI(id="far", name="far", west=95.5, south=26.9, east=95.52, north=26.92)
    with pytest.raises(RuntimeError, match="Fewer than two usable scenes"):
        build_ard_stack(build_stacks([a, b])[0], far, tmp_path / "out", local_opener(tmp_path))
