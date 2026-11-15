# science/analysis — change detection, validation and uncertainty

Owner: **Naveen** (issue #3), working with Veer. Turns an analysis-ready NISAR GCOV stack (`sarpulse.ard_stack.v0` from `science/ingestion/`, PR for issue #2) into open-water maps, before/after change classes, a water-area time series, uncertainty ranges and accuracy checks. All outputs match the draft API schemas (PR #7).

## Method (baseline)

1. **Speckle**: Lee filter (5×5) on linear power. ENL is estimated from the data as 1 / mode of the local CV² distribution (11×11 windows).
2. **Open water per date**: split-based Otsu threshold on HH dB. The image is tiled (64 px), and only tiles whose histogram is clearly bimodal are pooled to choose the threshold. Bimodal means Ashman's D > 2 on a fitted two-Gaussian mixture, with the smaller component ≥ 10 %. If fewer than 5 tiles qualify, a global Otsu fallback is used and flagged.
3. **Threshold uncertainty**: bootstrap over the selected tiles (200 resamples). The uncertainty half-width u = max(1.96·σ_boot, 0.5 dB).
4. **Change classes** (`change_class.tif`, uint8):

   | Code | Class | Rule |
   | --- | --- | --- |
   | 0 | `stable_land` | not water on either date |
   | 1 | `water_gained` | land → water, and HH fell by ≥ 3 dB |
   | 2 | `water_lost` | water → land, and HH rose by ≥ 3 dB |
   | 3 | `stable_water` | water on both dates |
   | 4 | `ambiguous` | HH within ±u of the threshold on either date, or label flipped with < 3 dB change |
   | 255 | nodata | invalid on either date |

5. **Area ranges**: gained/lost areas are recomputed with each date's threshold shifted by −u, 0 and +u, and the min/max is reported as `area_ranges_km2`.
6. **Independent-method check (unsupervised ML)**: a 2-component Gaussian mixture on (HH, HV) dB per date. Agreement with the Otsu map is reported as percent agreement and Cohen's κ. This is **internal consistency, not accuracy**.
7. **Time series**: water area per date over the area valid on **every** date, so the areas are comparable.

L-band HH is used for the water decision because calm open water is a specular, very dark target. HV over water is often near the noise floor, so it is used only as a GMM feature and reported in samples.

## Usage

```bash
cd science/analysis
pip install -r requirements.txt          # Python 3.12

# after science/ingestion has built data/processed/<aoi>/stack.json
python -m sarpulse_analysis run --stack ../../data/processed/brahmaputra-majuli/stack.json \
    --before 2026-07-22 --after 2026-10-14
```

`--before` and `--after` accept a scene id or `YYYY-MM-DD`, and the before scene must be earlier. The output goes to `data/processed/<aoi>/analysis/` (git-ignored):

| File | Purpose |
| --- | --- |
| `site.json`, `scenes.json`, `analysis.json`, `time_series.json`, `samples.json` | API store layout (`<data_dir>/<site_id>/`). Add Shridhar's `context.json` and the folder can be served directly |
| `change_class.tif`, `delta_hh_db.tif`, `water/<date>.tif` | GeoTIFFs on the stack's UTM grid |
| `web/*.png`, `layers.json` | EPSG:4326 overlays (change classes, per-date water, per-date HH backscatter with a fixed −25…0 dB stretch) with `bounds_wgs84` / `image_coordinates` for a MapLibre image source |
| `validation/<date>.json` | written by `validate` (below) |

`analysis.json` keeps every API field and adds `stable_water_km2`, `stable_land_km2`, `area_ranges_km2`, `hh_brightening_non_water_km2`, `thresholds` and `method_agreement`. Pydantic ignores these extra fields.

### Validation against an independent reference

No accuracy figure exists until a real, independent reference is compared. For example, use points labelled on a near-same-day cloud-free Sentinel-2 image, or a reference water raster:

```bash
python -m sarpulse_analysis validate --stack ../../data/processed/brahmaputra-majuli/stack.json \
    --analysis-dir ../../data/processed/brahmaputra-majuli/analysis --date 2026-10-14 \
    --reference labels_2026-10-14.geojson --kind points --reference-name "Sentinel-2 L2A 2026-10-15, manual labels"
```

This reports a confusion matrix, overall accuracy with a Wilson 95 % CI, precision/recall/F1/IoU for water and Cohen's κ, and writes the summary into `analysis.json:validation_status`. Points need a boolean `water` property. For a raster, use `--kind raster --water-values 1`. Remember that a reference from a different date measures change as well as error.

## Tests

```bash
python -m pytest -q
```

Tests use simulated gamma-speckle stacks from `tests/synthetic_stack.py` (**SYNTHETIC/DEMO — NOT NASA OBSERVATIONS**). They check threshold behaviour on bimodal and unimodal scenes, ENL recovery, the class rules, metrics, recovery of a known flooded area, and the API field sets.

## Limitations (also written into every `analysis.json`)

- Low HH also comes from smooth non-water surfaces (dry sand bars, bare flat soil, radar shadow). Wind- or rain-roughened water can be missed.
- Flooded vegetation (double-bounce brightening) is **not** mapped as water. Strong HH increases on non-water land are reported only as `hh_brightening_non_water_km2`.
- Backscatter change is evidence of surface change, not proof of flooding or its cause.
- Layover/shadow (NISAR static-layers product) is not applied.
- Provisional GCOV maturity is carried as a limitation and a time-series quality flag.
- Parameters (3 dB minimum change, 0.5 dB minimum uncertainty, 64 px tiles) are documented choices, not tuned on reference data.
