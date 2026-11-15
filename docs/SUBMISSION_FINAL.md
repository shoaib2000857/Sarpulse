# SARPulse — final project fields

Prepared November 16, 2026 from the delivered build. This replaces the earlier completion-assumption draft. It documents the current project, not an assertion that a NASA submission was made before the supplied deadline.

## Project name

SARPulse — Earth's changes. Revealed by radar.

## Summary

SARPulse turns NASA–ISRO NISAR radar measurements into an interactive investigation of changing water landscapes. Team StarFire built a reproducible workflow and public application for Dancing with the SARs, featuring genuine observations of the Brahmaputra–Majuli floodplain in Assam and Biesbosch wetlands in the Netherlands.

Users compare dated HH/HV radar layers, explore candidate water gain and loss, inspect scientific metadata and download a Change Passport linking an interpretation to its measurements, method and limitations. A Science Lab exposes thresholds, sensitivity and reference comparisons instead of hiding uncertainty behind a coloured map.

Radar change does not automatically prove flooding. Our Biesbosch optical-reference comparison reveals substantial false positives; Assam has no independent reference comparison. SARPulse makes those limits visible while helping educators, researchers and floodplain managers investigate where change occurred, what the evidence supports and what still requires verification.

## Project demonstration

https://sarpulse.adoredrose256.chatgpt.site/demo/sarpulse-demo.pdf

Seven slides including title and introduction. Browser presentation: https://sarpulse.adoredrose256.chatgpt.site/demo/

## Project link

https://sarpulse.adoredrose256.chatgpt.site

Requested domain: https://sarpulse.shoaibssm.me — use only after the DNS/HTTPS verification described in [PUBLIC_DEPLOYMENT.md](PUBLIC_DEPLOYMENT.md). Source: https://github.com/shoaib2000857/Sarpulse

## Project details

### What it does

SARPulse connects satellite-data processing to an interactive Earth-observation workspace. Its Earth Time Machine compares dated radar layers; its Change Intelligence Map highlights candidate water gain, loss and ambiguous areas; its Science Lab exposes channels, processing parameters, reference results and downloadable scientific outputs. A Change Passport records source acquisition identifiers, timestamps, coordinates, radar values, method and limitations. Public static passports disclose the distance to the nearest precomputed sample; the full API samples the actual analysed raster pixel.

### How it works

The Python pipeline discovers compatible NISAR L2 GCOV observations, inspects available HH/HV covariance diagonals, retains quality masks, and prepares a common projected grid. Positive radar power is converted with 10 log10(power) into decibels. An interpretable water-classification baseline, temporal backscatter checks and threshold sensitivity produce candidate gain/loss and ambiguous classes. Physical pixel area determines square-kilometre summaries. A secondary statistical method provides internal comparison, not proof of accuracy.

The Assam investigation compares July 22 and October 14, 2026; Biesbosch compares July 19 and October 11, 2026. Both use genuine provisional NISAR GCOV data with processing CRID P05023. Acquisition identities, UTC, units, CRS and lineage remain inspectable. Assam data were retrieved through ASF/Earthdata; Biesbosch native subsets came through a documented public mirror with NASA identifiers corroborated against ASF metadata. Derived images, GeoTIFFs, CSV and provenance are published; raw source HDF5 and credentials are excluded.

### Scientific evaluation and limitations

Copernicus DEM and JRC historical-water data provide separately identified geographic context. Biesbosch is compared with Sentinel-2C L2A scene-classification water labels acquired 4.34 days before its first radar observation. Water precision is 0.2605, recall 0.8906 and F1 0.403. These results expose considerable false positives and describe agreement with an automatic, time-offset reference, not field accuracy. Assam lacks an independent reference comparison. Tides, vegetation, moisture, roughness, speckle and threshold choices can affect interpretation. Candidate changes are not confirmed floods or estimates of people affected. Rainfall integration, supervised ML, dual-frequency analysis and global on-demand processing are not claimed as delivered features.

### Creativity, benefits and impact

Our contribution is a traceable investigation from radar measurement to map interpretation. Users can inspect why a location was highlighted, see uncertainty and download the underlying evidence. Precomputed layers make the public experience responsive without requiring Earthdata credentials or a large live processing job. The reusable workflow helps people investigate water landscapes while making its own failure cases visible.

### Technology and team

Python, NumPy, SciPy, h5py, Rasterio/GDAL, pyproj, scikit-learn, FastAPI and Pydantic support processing and evidence delivery. React, TypeScript, Vite and MapLibre GL JS power the interface. Docker runs the complete application; GitHub Actions checks Python on Windows/Linux and the frontend build/tests. A seven-slide web/PDF demo accompanies the project.

Team StarFire: Shoaib — platform and integration; Veer — data and preprocessing; Naveen — change detection and evaluation; Nidhi — mapping and frontend; Shridhar — backend and scientific evidence; Hansika — UI/UX, story and presentation.

## Use of Super Intelligence

Select the actual form options for code assistance and writing/documentation assistance. OpenAI Codex assisted implementation, review, debugging, testing, integration and documentation under the team's supplied direction. Central disclosure: [AI_DISCLOSURE.md](../AI_DISCLOSURE.md). SI did not generate the satellite observations or reported reference measurements. Synthetic software-test fixtures are explicitly separated from genuine observations. Include any additional tools actually used by teammates; do not select “I did not use SI.”

## NASA Data — Link Text / Link URL

| Link Text | Link URL |
| --- | --- |
| NASA–ISRO NISAR L2 GCOV — product and processing documentation | https://nisar-docs.asf.alaska.edu/gcov/ |
| NASA ASF DAAC — NISAR archive and discovery | https://search.asf.alaska.edu/ |
| NASA Earthdata — data access | https://search.earthdata.nasa.gov/search |
| NASA earthaccess — authenticated retrieval library | https://github.com/nsidc/earthaccess |
| Exact NISAR scenes, output provenance and reference evidence | https://github.com/shoaib2000857/Sarpulse/tree/main/web/public/data/sites |
| NASA SMAP — credited introductory 3D model source, not NISAR imagery | https://science.nasa.gov/resource/smap-3d-model/ |

## Space Agency Partner & Other Data — Link Text / Link URL

| Link Text | Link URL |
| --- | --- |
| SARPulse source, full dependency and asset attribution | https://github.com/shoaib2000857/Sarpulse/blob/main/ATTRIBUTION.md |
| Copernicus DEM GLO-30 — terrain context | https://registry.opendata.aws/copernicus-dem/ |
| EC JRC Global Surface Water v1.4 — historical context | https://global-surface-water.appspot.com/ |
| ESA Copernicus Sentinel-2 — optical reference and processing | https://sentiwiki.copernicus.eu/web/s2-processing |
| Earth Search — Sentinel-2 STAC discovery | https://earth-search.aws.element84.com/v1 |
| Biesbosch NISAR transport mirror — original identities retained | https://huggingface.co/datasets/EscRq1/netherlands-nisar-pair/tree/main |
| Python | https://www.python.org/ |
| NumPy | https://numpy.org/ |
| SciPy | https://scipy.org/ |
| h5py | https://www.h5py.org/ |
| Rasterio / GDAL | https://rasterio.readthedocs.io/ |
| pyproj / PROJ | https://pyproj4.github.io/pyproj/stable/ |
| scikit-learn | https://scikit-learn.org/ |
| FastAPI | https://fastapi.tiangolo.com/ |
| Pydantic | https://docs.pydantic.dev/ |
| Uvicorn | https://www.uvicorn.org/ |
| Requests | https://requests.readthedocs.io/ |
| React | https://react.dev/ |
| TypeScript | https://www.typescriptlang.org/ |
| Vite | https://vite.dev/ |
| MapLibre GL JS | https://maplibre.org/maplibre-gl-js/docs/ |
| Three.js and supporting frontend libraries — complete list | https://github.com/shoaib2000857/Sarpulse/blob/main/web/package.json |
| OpenStreetMap — map attribution where displayed | https://www.openstreetmap.org/copyright |
| GitHub Actions — source and CI | https://github.com/features/actions |
| Docker — reproducible application | https://www.docker.com/ |
| OpenAI Codex — development and documentation assistance | https://openai.com/codex/ |

The complete asset/license and tool inventory in ATTRIBUTION.md is part of this resource list. Do not claim NASA website submission or acceptance from this document. Agreement to terms and originality remains the submitting participant's attestation.
