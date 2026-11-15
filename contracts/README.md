# SARPulse v0 integration contracts

Confirmed for integration by Shoaib's platform work on November 15, 2026. Existing teammate field names are preserved.

## Scientific handoff

Ingestion writes `sarpulse.ard_stack.v0` (`stack.json`) with a shared projected, metre-based north-up grid. `grid.transform` is **Affine constructor order** `[a,b,c,d,e,f]`, with `x=a*col+b*row+c`, `y=d*col+e*row+f`. This is **not** GDAL's `GetGeoTransform()` order. HH/HV covariance diagonals remain positive gamma-0 linear power; valid masks are explicit. Analysis converts to dB with `10*log10(power)`.

Analysis writes `<data_root>/<site_id>/` containing:

- `site.json`, `scenes.json`, `analysis.json`, `time_series.json`, `samples.json`, `layers.json`.
- Optional `context.json`; its absence yields an empty evidence list.
- `change_class.tif`, `delta_hh_db.tif`, `water/*.tif`, `evidence/*.tif`, `web/*.png`.
- Optional validation records. Independent reference comparison is separate from internal method agreement.

The JSON Schemas in this directory describe each API record. `openapi.json` is generated from the actual FastAPI application. Regenerate with `python scripts/sarpulse.py contracts`; CI detects drift.

## Frontend consumption

API base: `/api`. Fetch `/api/sites`, then `/api/sites/<id>/{scenes,summary,timeseries,layers,evidence}`. `GET /api/sites/<id>/passport?lon=...&lat=...` returns point evidence. Coordinates are longitude/latitude WGS84. Use `/docs` for the complete interface.

Static delivery: fetch `<base>/sites.json`, then `<base>/sites/<id>/site.json`, `scenes.json`, `analysis.json`, `time_series.json`, `layers.json`, `samples.json`, and `context.json`. Resolve each layer's `png`/`geotiff` relative to the site directory. Static delivery does not implement the dynamic passport route: display the selected sparse sample's coordinates and distance, or use the API for actual-pixel sampling.

MapLibre image sources use `image_coordinates` in **top-left, top-right, bottom-right, bottom-left** order. PNGs are overlays with georeferencing in `layers.json`, not independent georeferenced imagery. Class codes: 0 stable land, 1 gained water, 2 lost water, 3 stable water, 4 ambiguous, 255 no data. HH visual stretch is fixed at -25…0 dB; HV is -35…-5 dB; HH difference is -10…10 dB. These display limits do not change physical measurements.

The shipped pipeline produces one selected before/after change pair per run. Other acquisition dates can be browsed as single-date layers; selecting a different change pair requires another precomputed run. The API does not run a new analysis on request or implement the old plan's optional `summary?before=&after=` interface.

## Scientific display requirements

Always display `data_status`. Synthetic results must be conspicuously marked `SYNTHETIC/DEMO — NOT NASA OBSERVATIONS`. `verified` means real source inputs, not independently validated classifier accuracy. Display `validation_status` separately.

Areas are km², backscatter is gamma-0 dB, observation timestamps are UTC, and source CRS/release/polarization remain available in scene records and provenance. Time-series points use the intersection of valid areas across all selected dates. Preserve their `quality_flags`, threshold and sensitivity ranges. Do not interpolate missing acquisitions.

Threshold sensitivity ranges are not calibrated probabilities. Method agreement is not accuracy. Do not infer flood causation, casualties, displacement or vegetated inundation from the open-water classes. Sparse sample passports disclose coordinates/distance; newer runs export filtered evidence rasters for exact pixel lookup. Invalid locations abstain from environmental interpretation.

