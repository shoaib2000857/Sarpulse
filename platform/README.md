# Core platform and integration

Owner: Shoaib.

## Setup (repository root, PowerShell)

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.lock.txt
uv pip install --python .venv/Scripts/python.exe --no-deps -e .
.venv/Scripts/python scripts/sarpulse.py doctor
```

Standard Python alternative: create a Python 3.12 virtual environment, then `python -m pip install -r requirements.lock.txt` and `python -m pip install --no-deps -e .`. After activating it, `sarpulse` is the same entry point as `python scripts/sarpulse.py`. No app is launched by setup or discovery.

## One real investigation

Search is public. Pixel access requires local downloaded files or a free Earthdata account, configured outside Git through `.netrc` or environment variables. Do not paste credentials into documentation or chat.

```powershell
.venv/Scripts/python scripts/sarpulse.py search --aoi data/aoi/brahmaputra-majuli.geojson --end 2026-11-15 --out-dir data/manifests/brahmaputra-majuli

.venv/Scripts/python scripts/sarpulse.py run --aoi data/aoi/brahmaputra-majuli.geojson --manifest-dir data/manifests/brahmaputra-majuli --stack-id T040A_F015_4005_DHDH_PR_P05023 --before 2026-07-22 --after 2026-10-14 --out data/processed/majuli-run-001
```

For downloaded GCOV files, add `--local-dir <folder> --offline`. Files must be named `<scene_id>.h5`. A local-only run does not require Earthdata Login. For an existing ARD stack:

```powershell
.venv/Scripts/python scripts/sarpulse.py run --stack data/processed/majuli-run-001/ard/stack.json --before 2026-07-22 --after 2026-10-14 --out data/processed/majuli-run-002
```

Output is `<run>/sites/brahmaputra-majuli/`, directly readable by the API. `<run>/input_manifest.json` snapshots selected metadata and `<run>/run.json` records phase completion/failure. Existing runs/deliveries are not overwritten. `--context` adds DEM/JRC context, `--imerg` adds rainfall; both require remote access and are opt-in. Missing optional context never prevents the core API from serving results.

## Independent validation and quality gate

```powershell
.venv/Scripts/python scripts/sarpulse.py validate --stack data/processed/majuli-run-001/ard/stack.json --analysis-dir data/processed/majuli-run-001/sites/brahmaputra-majuli --date 2026-10-14 --reference <reference.geojson> --kind points --reference-name "Actual sensor/date, labeling method and limitations"

.venv/Scripts/python scripts/sarpulse.py inspect --site data/processed/majuli-run-001/sites/brahmaputra-majuli --require-validation
```

Reference points require boolean or numeric 0/1 `water` labels in WGS84. Raster validation supports explicit water values and honors nodata. A reference comparison only establishes validity to the extent that its provenance, temporal agreement and sampling design are trustworthy. No reference is downloaded or invented automatically.

## Export and serve

```powershell
.venv/Scripts/python scripts/sarpulse.py export --site data/processed/majuli-run-001/sites/brahmaputra-majuli --out dist/majuli-v001 --require-validation --vectors
.venv/Scripts/python scripts/sarpulse.py serve --data-dir dist/majuli-v001/sites --port 8000
```

The delivery has `sites.json`, per-site science JSON, PNG/GeoTIFF assets, CSV time series, provenance, optional GeoJSON change polygons and SHA-256 checksums in `artifact.json`. GeoJSON means derived classifications, not confirmed flood outlines. Vector export stops at 25,000 features; use rasters or a smaller AOI if exceeded. The export includes no raw HDF5 products or credentials.

Export/inspect reject synthetic outputs by default. `--allow-synthetic` is an explicit integration-test mode; labels remain visible in every record. Without `--require-validation`, observed results may be exported with an explicit not-validated status. Do not present that as measured accuracy.

`sarpulse serve --data-dir api/fixtures` serves the existing **synthetic** API fixture for frontend development. It does not establish a real scientific demonstration.

## Verification

```powershell
New-Item -ItemType Directory -Path build -Force | Out-Null
.venv/Scripts/python -m pytest -q --basetemp=build/pytest-run-unique
.venv/Scripts/python scripts/sarpulse.py contracts
git diff -- contracts
```

Use a fresh local basetemp name if the system pytest temp directory is inaccessible. CI runs the full suite on Ubuntu and Windows with Python 3.12, validates fixture contracts and detects schema drift. Integration tests cover **synthetic HDF5 -> ingestion -> analysis -> API -> export**, preservation of uncertainty, real-pixel lookup, nodata references, grid shifts and incompatible releases. These are engineering checks, not validation of real-world water classification.
