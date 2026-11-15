# Complete project release — November 16, 2026

The runnable project now includes scientific ingestion/analysis, a connected frontend, static and API evidence delivery, genuine precomputed observations, comparative reference evidence, exports and a seven-slide demo.

## Delivered

- **Veer:** authentic GCOV pixel retrieval, HH/HV inspection, masking, aligned projected grids and source metadata. Assam retrieved through Earthdata; an independently documented Netherlands pair provides a second case.
- **Naveen:** interpretable open-water baseline, change classes, parameter sensitivity, ambiguous area, multi-polarization consistency check, reference metrics and explicit errors/limits.
- **Shridhar:** evidence/scenes/summary/layers/samples APIs, exact analysed-pixel passports, terrain and historical-water adapters; optical reference evidence is included with its time offset and limitations.
- **Nidhi:** shared map with georeferenced PNG/image support, HH/HV selection, before/after comparison, site selection, fixed-pair change overlays and connected point inspection.
- **Hansika:** responsive application, Science Lab, guided story, original credited 3D presentation and completed seven-slide web/PDF demonstration at `/demo/` and `/demo/sarpulse-demo.pdf`.
- **Shoaib:** source/contract integration, reproducible commands, inspected static deliveries, complete Docker application, CI and release-artifact workflow, publication and documentation.

The frontend supports both `VITE_SARPULSE_API_URL` (the Docker build uses `/api`) and a static `VITE_SARPULSE_DATA_URL` (default `/data/`). The static version discloses nearest-sample coordinates and distance; the API reads actual analysed raster pixels. Changing arbitrary observation dates does not recompute the preselected change pair.

## Scientific findings and limits

All four NISAR inputs are genuine provisional GCOV products with CRID P05023. Physical values, dates, CRS, masks and releases are retained. The reference comparison is intentionally not described as validated flood detection: the Biesbosch baseline has many false positives (water F1 0.403 against an automatic Sentinel-2 SCL reference acquired 4.34 days earlier). Its temporal gap, tidal/land-cover changes and automatic reference errors are explicit. Assam has no independent reference comparison. No field accuracy, confirmed flood impact, displacement or vegetated-inundation claim is made.

Heavy on-demand global computation, a supervised model without representative labels, L/S fusion, displacement and operational flood alerts remain outside this release. They were conditional/deferred items in the accepted plan, not missing dependencies for running the project.

## Reproduce and run

`docker compose up --build` serves the complete app/API at http://127.0.0.1:8000 . `npm --prefix web ci` and `npm --prefix web run dev` run the static viewer. Python setup/runner commands remain in `platform/README.md`; AOIs/manifests for both cases are under `data/`. Raw source products remain local and ignored. Do not commit Earthdata files.

The public deployment and any required custom-domain DNS records are recorded in `docs/PUBLIC_DEPLOYMENT.md`. The submission package is a project delivery, not proof of a NASA website submission. The supplied deadline was November 15 at 23:59 in the applicable event time zone; development continuing on November 16 must not be represented as completed within an earlier submission window.
