import json

import numpy as np
import pytest
import rasterio

from sarpulse_analysis.change import CLASS_CODES, NODATA, DateResult, Params, change_map
from sarpulse_analysis.features import estimate_enl, lee_filter, to_db
from sarpulse_analysis.pipeline import run_analysis
from sarpulse_analysis.stack import SYNTHETIC, load_stack
from sarpulse_analysis.validate import binary_metrics, validate_water_map, wilson_interval
from sarpulse_analysis.water import agreement, otsu_threshold, split_based_threshold
from sarpulse_analysis.water import ThresholdResult

from tests.synthetic_stack import EPSG, SPACING, X0, Y0, river_masks, speckled, write_stack

API_ANALYSIS_FIELDS = {
    "aoi_id", "source_scene_ids", "before_scene_id", "after_scene_id", "processing_version", "valid_area_km2",
    "gained_water_km2", "lost_water_km2", "ambiguous_km2", "class_definitions", "threshold_method", "provenance",
    "limitations", "validation_status", "data_status",
}
API_SAMPLE_FIELDS = {"lon", "lat", "before_hh_db", "after_hh_db", "before_hv_db", "after_hv_db", "change_class", "valid", "slope_deg", "jrc_occurrence_pct"}


def test_otsu_separates_two_modes():
    rng = np.random.default_rng(1)
    v = np.concatenate([rng.normal(-22, 1.5, 20000), rng.normal(-8, 1.5, 60000)])
    assert -18 < otsu_threshold(v) < -12


def test_lee_filter_reduces_speckle_and_keeps_mean():
    rng = np.random.default_rng(2)
    img = speckled(np.full((200, 200), -10.0), looks=4, rng=rng)
    img[0:5, 0:5] = np.nan
    assert 3.4 < estimate_enl(img) < 4.6
    out, enl = lee_filter(img, 5)
    assert np.isnan(out[0:5, 0:5]).all()
    core = (slice(20, 180), slice(20, 180))
    assert np.nanstd(out[core]) < 0.6 * np.nanstd(img[core])
    assert abs(np.nanmean(out[core]) / np.nanmean(img[core]) - 1) < 0.02


def test_split_based_threshold_on_bimodal_scene():
    rng = np.random.default_rng(3)
    _, after = river_masks()
    db = to_db(lee_filter(speckled(np.where(after, -22.0, -8.0), 8, rng), 5)[0])
    t = split_based_threshold(db, tile_px=32, n_boot=50)
    assert -19 < t.threshold_db < -11
    assert t.n_tiles_selected >= 5 and "global_otsu_fallback" not in t.flags
    assert t.uncertainty_db >= 0.5


def test_split_based_threshold_flags_unimodal_scene():
    rng = np.random.default_rng(4)
    db = to_db(speckled(np.full((128, 128), -8.0), 8, rng))
    t = split_based_threshold(db, tile_px=32, n_boot=20)
    assert "global_otsu_fallback" in t.flags and "weak_bimodality" in t.flags


def _date(hh_db: np.ndarray, threshold=-15.0, unc=0.5) -> DateResult:
    valid = np.isfinite(hh_db)
    thr = ThresholdResult(threshold, unc, 0.1, "fixed", 0, 0, 3.0, 0.3)
    return DateResult("x", "2026-01-01", hh_db, hh_db - 7, valid, thr, valid & (hh_db < threshold), valid & (np.abs(hh_db - threshold) < unc), None)


def test_change_map_rules():
    before = np.array([[-22, -8, -22, -8, -8, -15.2, np.nan]], dtype=np.float32)
    after = np.array([[-22, -22, -8, -8, -16, -22, -22]], dtype=np.float32)
    cls, diag = change_map(_date(before), _date(after), Params())
    expected = [
        CLASS_CODES["stable_water"],
        CLASS_CODES["water_gained"],
        CLASS_CODES["water_lost"],
        CLASS_CODES["stable_land"],
        CLASS_CODES["water_gained"],  # -8 -> -16: label flips and HH dropped 8 dB
        CLASS_CODES["ambiguous"],  # before label inside the uncertainty band
        NODATA,
    ]
    assert cls[0].tolist() == expected
    weak = change_map(_date(np.array([[-14.0]], dtype=np.float32)), _date(np.array([[-16.0]], dtype=np.float32), unc=0.1), Params())[0]
    assert weak[0, 0] == CLASS_CODES["ambiguous"]  # label flips but only 2 dB change
    assert diag["valid_pixels"] == 6


def test_binary_metrics_and_wilson():
    pred = np.array([1, 1, 0, 0, 1, 0, 0, 0], dtype=bool)
    ref = np.array([1, 0, 0, 0, 1, 1, 0, 0], dtype=bool)
    m = binary_metrics(pred, ref)
    assert m["confusion_matrix"] == {"tp": 2, "fp": 1, "fn": 1, "tn": 4}
    assert m["overall_accuracy"] == 0.75 and m["precision_water"] == round(2 / 3, 4) and m["iou_water"] == 0.5
    lo, hi = wilson_interval(6, 8)
    assert lo < 0.75 < hi
    assert agreement(pred, ref, np.ones(8, bool))["percent_agreement"] == 75.0


def test_pipeline_end_to_end(tmp_path):
    before_mask, after_mask = river_masks()
    invalid = np.zeros_like(before_mask)
    invalid[:, :8] = True  # e.g. outside the acquisition
    stack_path = write_stack(tmp_path / "stack", [before_mask, after_mask], ["2026-07-10", "2026-07-22"], invalid=invalid)
    out = tmp_path / "out"
    a = run_analysis(stack_path, "2026-07-10", "2026-07-22", out, Params(n_boot=50))

    assert a["data_status"] == SYNTHETIC and a["limitations"][0].startswith("All values are derived from SYNTHETIC")
    assert API_ANALYSIS_FIELDS <= set(a)
    px_km2 = SPACING * SPACING / 1e6
    true_gain = after_mask.sum() - before_mask.sum()
    assert a["valid_area_km2"] == pytest.approx((~invalid).sum() * px_km2)
    # Confident gain is within 15 % of truth and the threshold range brackets it loosely.
    assert a["gained_water_km2"] == pytest.approx(true_gain * px_km2, rel=0.15)
    lo, hi = a["area_ranges_km2"]["water_gained"]
    assert lo <= a["gained_water_km2"] * 1.2 and hi >= a["gained_water_km2"] * 0.8
    assert a["lost_water_km2"] < 0.05 * a["gained_water_km2"]
    assert a["method_agreement"]["2026-07-22"]["cohens_kappa"] > 0.8

    with rasterio.open(out / "change_class.tif") as r:
        cls = r.read(1)
        assert r.crs.to_epsg() == EPSG and tuple(r.transform)[:6] == (SPACING, 0, X0, 0, -SPACING, Y0)
    assert (cls[invalid] == NODATA).all()
    flood = after_mask & ~before_mask
    assert np.mean(cls[flood] == CLASS_CODES["water_gained"]) > 0.85

    ts = json.loads((out / "time_series.json").read_text())
    assert [p["date"] for p in ts["points"]] == ["2026-07-10", "2026-07-22"]
    assert ts["points"][1]["water_area_km2"] > ts["points"][0]["water_area_km2"]
    samples = json.loads((out / "samples.json").read_text())
    assert samples and all(set(s) == API_SAMPLE_FIELDS for s in samples)
    assert any(s["change_class"] == "water_gained" for s in samples) and any(not s["valid"] for s in samples)
    site = json.loads((out / "site.json").read_text())
    assert site["verified"] is False and site["data_status"] == SYNTHETIC
    layers = json.loads((out / "layers.json").read_text())
    for layer in layers["layers"]:
        assert (out / layer["png"]).is_file()
    w, s, e, n = layers["bounds_wgs84"]
    assert 93.9 < w < e < 94.2 and 26.8 < s < n < 27.0


def test_validate_against_reference_points(tmp_path):
    before_mask, after_mask = river_masks()
    stack_path = write_stack(tmp_path / "stack", [before_mask, after_mask], ["2026-07-10", "2026-07-22"])
    out = tmp_path / "out"
    run_analysis(stack_path, "2026-07-10", "2026-07-22", out, Params(n_boot=20, gmm_check=False))
    stack = load_stack(stack_path)

    # Reference labels taken from the known synthetic truth (a stand-in for independent labels).
    from pyproj import Transformer

    tr = Transformer.from_crs(f"EPSG:{EPSG}", "EPSG:4326", always_xy=True)
    feats = []
    for r in range(5, 256, 25):
        for c in range(5, 256, 25):
            lon, lat = tr.transform(X0 + (c + 0.5) * SPACING, Y0 - (r + 0.5) * SPACING)
            feats.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": {"water": bool(after_mask[r, c])}})
    ref = tmp_path / "ref.geojson"
    ref.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))

    with rasterio.open(out / "water" / "2026-07-22.tif") as r:
        wm = r.read(1)
    m = validate_water_map(wm == 1, wm != 255, stack.grid, ref, "points")
    assert m["n"] == len(feats) and m["overall_accuracy"] > 0.9
