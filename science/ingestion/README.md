# science/ingestion — NISAR GCOV acquisition and processing

Owner: **Veer** (issue #2). Turns real NISAR L2 GCOV products into an analysis-ready stack for `science/analysis/`.

What it does:

1. **Discover**: query the public ASF Search API for NISAR L2 GCOV products intersecting an AOI (`data/aoi/*.geojson`).
2. **Check comparability**: group products that share track, direction, frame, bandwidth mode, polarization, processing type and CRID (software release). Reprocessed duplicates keep only the latest counter. Mixed maturity, mixed orbit accuracy and partial frames are reported as warnings.
3. **Build an analysis-ready stack**: stream only the AOI window of each product (Earthdata Login required), apply the GCOV validity mask, multilook in linear power and write every scene onto one shared, snapped UTM grid.

## Setup

```bash
cd science/ingestion
python -m venv .venv && source .venv/bin/activate   # Python 3.12
pip install -r requirements.txt
```

Reading products needs a free [Earthdata Login](https://urs.earthdata.nasa.gov/) in `~/.netrc`:

```text
machine urs.earthdata.nasa.gov login <username> password <password>
```

Or set `EARTHDATA_USERNAME` / `EARTHDATA_PASSWORD`. Never commit credentials.

## Usage

```bash
# 1. Catalogue search -> data/manifests/<aoi>/{gcov_candidates,comparable_stacks}.json
python -m sarpulse_ingest search --aoi ../../data/aoi/brahmaputra-majuli.geojson --end 2026-11-14

# 2. Analysis-ready stack -> data/processed/<aoi>/ (git-ignored)
python -m sarpulse_ingest ard --aoi ../../data/aoi/brahmaputra-majuli.geojson \
    --stack-id T040A_F015_4005_DHDH_PR_P05023 --dates 2026-07-22,2026-10-14
```

`--dates` selects a subset of the stack (omit it to process every date). `--local-dir` uses already-downloaded `<scene_id>.h5` files first, and `--offline` never streams.

## Verified catalogue result (Brahmaputra / Majuli AOI)

The ASF search on 2026-11-14 (`data/manifests/brahmaputra-majuli/`) returned 32 GCOV products and 6 comparable stacks. The largest stack:

| Stack | Dates | Range | Maturity |
| --- | --- | --- | --- |
| `T040A_F015_4005_DHDH_PR_P05023`: track 40 ascending, frame 15, 40+5 MHz, dual-pol HH/HV, production, CRID P05023 | 10 | 2026-06-16 to 2026-10-14 (12-day repeat, with gaps) | PROVISIONAL |

So the **catalogue metadata** confirms comparable multi-date coverage across the 2026 monsoon and post-monsoon period. Pixel data has not been inspected yet: run `ard` with Earthdata credentials to confirm AOI validity per scene. The 2026-06-16 product uses forecast-orbit accuracy (`F`) while the others use `N`, so the stack warns about it.

## Output contract: analysis-ready stack v0

The integrated interface is documented in `contracts/README.md`.

`data/processed/<aoi>/stack.json` (`schema_version: sarpulse.ard_stack.v0`):

| Field | Meaning |
| --- | --- |
| `aoi` | id, name and WGS84 bbox |
| `stack_id`, `comparability_key`, `comparability_warnings` | why the scenes are comparable |
| `grid` | `crs`, `epsg`, `transform` (Affine constructor order a,b,c,d,e,f, not GDAL GetGeoTransform order), `width`, `height`, `pixel_spacing_m`; shared by every raster |
| `grid_bbox_wgs84` | grid bounds in lon/lat |
| `units` | physical meaning of each raster |
| `data_status` | `observed` only when every scene came from a real product; otherwise `SYNTHETIC/DEMO — NOT NASA OBSERVATIONS` |
| `processing` | software version, multilook factor, validity rule, creation time |
| `scenes[]` | per scene: `scene_id`, `acquired_at_utc` (zero-Doppler start), `files` (relative GeoTIFF paths), `valid_fraction`, `resampling`, `noise_equivalent_backscatter_db_median`, `warnings`, full `identification` group, `catalogue` record, and an API `scene` record |
| `excluded_scenes[]` | scenes that were dropped and why |

Rasters per scene (`ard/<scene_id>/`), all float32 GeoTIFF on the stack grid with NaN nodata:

- `HHHH.tif`, `HVHV.tif`: gamma-0 RTC backscatter in **linear power** (convert with `10*log10` for dB)
- `valid.tif` (uint8): 1 where the GCOV mask is a valid sub-swath (1–5), there is no input-data exception, and both terms are finite and positive
- `number_of_looks.tif`: looks per output pixel

`scenes.json` matches the draft API `Scene` schema in `api/app/schemas.py` (PR #7).

## Tests

```bash
python -m pytest -q
```

Tests use tiny HDF5 files in the GCOV layout from `tests/synthetic_gcov.py`. They are **SYNTHETIC/DEMO — NOT NASA OBSERVATIONS**, and a root attribute makes the pipeline label all derived outputs as synthetic.

## Limitations

- Uses frequency A (main band) HH and HV only. Frequency B (5 MHz, 80 m) and quad-pol cross terms are ignored.
- The GCOV `mask` does not encode layover/shadow. Those live in the separate static-layers product (`identification/staticLayersDataAccess`) and are not applied yet. The Brahmaputra floodplain is flat, but check terrain before using hilly AOIs.
- Noise-equivalent backscatter is a product-wide median in DN² (linear) converted to dB, and it is **informational only**. Low HV over calm water can sit near the noise floor.
- The stack is PROVISIONAL maturity (calibrated but not fully validated). Carry that caveat into every result.
- Multilooking requires every input pixel in a block to be valid, so edges shrink by up to one output pixel.

Sources: [NISAR GCOV product guide](https://nisar-docs.asf.alaska.edu/gcov/), [JPL D-102274 GCOV product specification Rev F](https://cumulus.asf.earthdatacloud.nasa.gov/PUBLIC/DATA/NISAR/NISAR_D-102274_RevF_NASA_SDS_Product_Specification_L2_GCOV_w-esigs.pdf), [earthaccess streaming](https://nisar-docs.asf.alaska.edu/earthaccess).
