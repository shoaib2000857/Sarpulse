# SARPulse API (`api/`)

Owner: Shridhar. FastAPI service for scientific evidence, contextual datasets and the **Change Passport**.

The API is a thin read-only layer over precomputed JSON (static-first), so the demo never depends on live processing. Schemas in `app/schemas.py` are a **draft proposal** pending Shoaib's sign-off in `contracts/`.

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
| GET | `/api/sites/{id}/evidence` | Context records (rainfall, JRC, optical, DEM) |
| GET | `/api/sites/{id}/passport?lon=&lat=` | Change Passport for a point |

## Data

`SARPULSE_DATA_DIR` (default `fixtures/`) holds `<site_id>/{site,scenes,analysis,time_series,context,samples}.json`.

**The bundled `fixtures/demo-brahmaputra` is SYNTHETIC/DEMO — NOT NASA OBSERVATIONS.** Every record carries `data_status` so the UI can show this.

## Change Passport

Evidence for a point is split into labelled items: **Observed** (radar dB values, acquisition times), **Derived** (change class, method, validation status), **Context** (ancillary data with caveats), **Hypothesis** (physical interpretation). Automatic warnings are added for mixed maturity, invalid masks, steep slope and distant samples.

## Next

- Context adapters: GPM IMERG, Sentinel-2 L2A, JRC GSW, DEM slope (write cached JSON, never called live in the demo).
- Swap fixtures for real exports from `science/analysis`.
