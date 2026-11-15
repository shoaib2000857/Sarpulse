# SARPulse API (`api/`)

Owner: Shridhar. FastAPI service for scientific evidence, contextual datasets and the **Change Passport**.

The API is a thin read-only layer over precomputed JSON (static-first), so the demo never depends on live processing. The integrated v0 interfaces are confirmed in `contracts/README.md`, with generated JSON Schema and OpenAPI definitions.

## Run

```bash
cd api
python -m venv .venv
.venv/Scripts/activate        # Windows; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Test

```bash
python -m pytest
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Status and available sites |
| GET | `/api/sites` | Site list |
| GET | `/api/sites/{id}` | One site |
| GET | `/api/sites/{id}/scenes` | Scene metadata |
| GET | `/api/sites/{id}/summary` | Change analysis (areas, method, limitations) |
| GET | `/api/sites/{id}/timeseries` | Per-date metrics (no interpolation) |
| GET | `/api/sites/{id}/evidence` | Context records (rainfall, JRC, optical, DEM); `[]` if none yet |
| GET | `/api/sites/{id}/layers` | Map overlay manifest (`layers.json`), PNG/GeoTIFF paths rewritten to URLs |
| GET | `/api/sites/{id}/files/{path}` | Serves `.png` / `.tif` assets inside the site folder only |
| GET | `/api/sites/{id}/passport?lon=&lat=` | Change Passport for a point |

## Data

`SARPULSE_DATA_DIR` (default `fixtures/`) holds `<site_id>/{site,scenes,analysis,time_series,samples,layers}.json` plus the `web/*.png` and `*.tif` assets, exactly as written by `python -m sarpulse_analysis` (science/analysis). `context.json` is optional and comes from the context adapters. Point the API at real output with `SARPULSE_DATA_DIR=../data/processed/<run>`.

Extra fields from the pipeline (`area_ranges_km2`, `thresholds`, `method_agreement`, ...) are passed through unchanged.

**The bundled `fixtures/demo-brahmaputra` is SYNTHETIC/DEMO — NOT NASA OBSERVATIONS.** Every record carries `data_status` so the UI can show this.

## Change Passport

Evidence for a point is split into labelled items: **Observed** (real radar dB values, acquisition times), **Derived** (change class, method, validation status), **Context** (ancillary data with caveats), **Hypothesis** (physical interpretation). Synthetic radar values use **Unverified**. New analysis exports include evidence rasters for actual-pixel lookup; older fixtures use sparse samples with disclosed coordinates and distance. Invalid pixels abstain from environmental interpretation. Warnings cover mixed maturity/release, invalid masks, steep slope and distant samples.

## Context adapters (offline)

Fill per-point `slope_deg` / `jrc_occurrence_pct` in `samples.json` and write `context.json` for a site folder (e.g. Naveen's pipeline output):

```bash
pip install -r requirements-context.txt
python -m context_adapters ../data/processed/<run>/<site_id>            # DEM slope + JRC (no login)
python -m context_adapters ../data/processed/<run>/<site_id> --imerg    # + IMERG rainfall (Earthdata Login)
```

| Kind | Source | AOI value | Caveat |
|---|---|---|---|
| `dem_slope` | Copernicus DEM GLO-30 (AWS Open Data COGs) | % of AOI with slope > 10 deg | layover/shadow risk |
| `jrc_gsw_occurrence` | EC JRC Global Surface Water v1.4 (1984-2021) | % of AOI water in >= 50% of observations | historical context, not 2026 truth |
| `rainfall_imerg` | NASA GPM IMERG V07 daily Late Run | AOI-mean accumulated mm between before and after dates `[before, after)` | context, not cause; ~10 km |

Only AOI windows are read remotely (about 30 s for the demo box). Results are cached in the folder, so the API never fetches live. Context records are `data_status: observed` because they are real ancillary data, independent of whether the radar site is synthetic.

## Next

- Run `--imerg` with Earthdata Login on the real Majuli stack dates.
- Optional: Sentinel-2 L2A nearest clear scene + cloud %.
- Swap fixtures for real exports from `science/analysis`.
