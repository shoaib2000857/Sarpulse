# StarFire — SARPulse
## NASA Space Apps Challenge 2026: Dancing with the SARs
### Research-backed master plan · Version 1.0 · November 7, 2026

**Working product name:** SARPulse  
**Tagline:** Earth's changes. Revealed by radar.  
**Team:** StarFire  
**Challenge:** https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/  
**Build event:** November 14–15, 2026; official submission opens Nov 14 at 09:00 and closes Nov 15 at 23:59 *local time*.  
**Note:** This document specifies a proposed project, not a completed implementation. No actual L-band acquisition pairs or scientific performance metrics have been confirmed here. Dataset feasibility must be independently checked in the ASF catalog. 2026 submission instructions are expected November 13 and supersede historical guidance.

---

## 1. Executive decision

Build a scientifically credible, visually striking, open-source platform for **multi-temporal NISAR-based floodplain and wetland change intelligence**. Prioritize **changes in open water extent**, and, where polarizations and labels allow, **inundation beneath vegetation**. Provide time-aware comparisons, quantitative area changes, physical radar explanations, context from other datasets, clear provenance, and transparent uncertainty. The proposed first flagship region is the **Brahmaputra floodplain of Assam, India**. Exact region boundaries and date pairs are conditional on finding comparable L-band observations. Reserve **Nagapattinam coastal wetlands** and another demonstrably covered region as fallbacks. ISRO has published a real July 9, 2026 S-band Brahmaputra scene and a July 2, 2026 coastal Tamil Nadu S-band scene, but **these alone do not demonstrate multi-date L-band coverage**.

A successful hackathon deliverable is **one fully functioning, scientifically tested AOI and a repeatable pipeline**, not an unverified world-wide system. An extensible map and dataset registry can support later regions, but the demo must distinguish active datasets, prototypes, unavailable data, and future features.

### Product thesis

> SARPulse turns complex NISAR radar products into understandable, inspectable evidence of how water and wetland landscapes change through time, even where optical satellite observations are cloud-obscured.

### Priority order

1. **Scientific validity and reproducibility.**
2. **One real, compelling change story with NISAR source evidence.**
3. **Complete, fast and accessible user experience.**
4. **Measured comparison to reference labels / baseline methods.**
5. **Advanced interpretation and multi-sensor features only if validated.**

### Non-goals for hackathon

- Do not claim real-time emergency alerts or operational flood forecasting.
- Do not promise centimeter-scale ground motion from amplitude-only GCOV images; displacement requires interferometric or offset products and separate analysis.
- Do not call cloud absence, open water, or radar brightness alone proof of a flood.
- Do not claim SAR objectively “sees through all vegetation” or every weather condition without limits.
- Do not present modeled population proximity as confirmed casualties/impact.
- Do not build general-purpose global LLM chat, custom pre-trained foundation models, or an entire Earth data infrastructure during the sprint.

---

## 2. Official challenge interpretation

NASA seeks an **interactive application leveraging NISAR SAR data to visualize one or more kinds of surface change**. Recommended challenge opportunities include multi-date observations, multiple polarizations, supplemental optical/GIS information, human versus natural physical drivers, intuitive maps, timelines, storytelling, and open-source accessibility. There is no requirement to solve every surface process. Our deep focus on floodplain/wetland dynamics fulfills the challenge more robustly than shallow demos spanning a dozen phenomena.

**Evaluator-visible mapping:**

| Challenge expectation | SARPulse evidence |
|---|---|
| NISAR is central | NISAR-derived backscatter change layers and scene metadata |
| Change over time | Confirmed co-comparable scenes, timestamps, temporal differences and change maps |
| Scientific investigation | Polarization-dependent scattering hypotheses, baseline, QA, validation |
| Map / public accessibility | Interactive geospatial viewer with accessible legend and explanations |
| Local/global relevance | Flagship floodplain with reusable workflow, clear ecological/social story |
| Visual storytelling | Guided 90-second investigation showing before, after, change, and evidence |
| Openness | Reproducible scripts, processing manifest, source citations and licensing |

The currently indexed challenge description does not substitute for materials that may appear in the official Resources tab near the event.

---

## 3. Research findings & critical constraints

### NISAR mission

NASA–ISRO NISAR launched July 30, 2025. The mission includes NASA L-band radar (~24 cm wavelength) and ISRO S-band radar (~9.4 cm wavelength, per NASA mission page), with an orbital repeat cycle of about 12 days. **Repeat cycle is not a guarantee of usable acquisitions over every site on every date.** The instruments can image in darkness and through clouds, but geometry, noise, water roughness and acquisition modes remain consequential.

### Available L-band data on Nov 7, 2026

- **PROVISIONAL:** released July 20, calibrated, partially validated, acquisitions beginning June 17 and continuing until partway through Oct 23, 2026. Collection `NISAR_L2_GCOV_PROVISIONAL_V1`; processing release ID `P05023` as documented in ASF's release notes.
- **VALIDATED:** released Nov 6; Level 0–2 products for acquisitions from Oct 21 onward. Collection `NISAR_L2_GCOV_V1`; initial composite release ID `P05036`.
- **BETA:** earlier limited, not fully calibrated; avoid for main inter-date change analysis if possible.
- **Important:** maturation/version effects can masquerade as change. Compare same maturity/processing lineage, prioritize matching orbit track and geometry, and explain any exceptions.
- **Instrument data gap:** July 27, 2026 at 22:03:25 UTC to August 10 at 00:55:27 UTC, permanent.
- **Product availability:** The mission will undertake older-data validated reprocessing in 2027; don't assume validated products cover earlier months as of Nov 7.
- **S-band:** distributed by ISRO Bhoonidhi, available for operational releases starting July 8, 2026, but registration/authorization and processing compatibility have to be verified independently.

### Why GCOV is core

Level-2 `GCOV` (Geocoded Polarimetric Covariance) is radiometrically terrain-corrected and geocoded to appropriate UTM grids. Diagonal covariance terms such as `HHHH`, `HVHV`, `VVVV` are real-valued radar gamma-zero **power** (linear units); convert valid positive values to decibels using `10*log10(power)`. Dataset paths typically look like:

`/science/LSAR/GCOV/grids/frequencyA/HHHH`
`/science/LSAR/GCOV/grids/frequencyA/HVHV`

Do not assume all polarizations are present. Some are compact/hybrid; inspect channels per product. Frequency A typically has 10m or 20m posted pixel spacing depending on mode; Frequency B can be 80m. **Posted pixel spacing is not automatically independent effective spatial resolution.** Check valid masks, number of looks, georeferencing, CRID, acquisition direction, track, geometry and overlapping extent. Off-diagonal covariance elements are complex and have different interpretation.

GCOV is appropriate for amplitude/backscatter changes and basic polarimetric analysis. It is **not** a ready-made interferometric coherence or displacement measurement. Save `GSLC`/`GUNW`/`GOFF` for future deformation modules.

### Auth & compute

- Create a free **NASA Earthdata Login** and search via ASF Vertex/`asf_search`/`earthaccess`.
- NISAR HDF5 source files can be large. Subset a **10–30 km region** and retain 2–6 comparable dates if available; where possible stream remote windows via NASA/ASF tools rather than download entire global products.
- For ISRO S-band create a separate Bhoonidhi account and verify permitted download/API access.
- Never commit credentials, Earthdata tokens, cookies or private `.netrc` files to Git.

---

## 4. Study area selection and go/no-go gates

### Preferred: Brahmaputra floodplain, Assam

**Why:** Complex braided channels, seasonal inundation, water-vegetation mixtures, major ecological and human relevance, and ISRO's published July 9 S-band radar decomposition image. A specific candidate subsection might be near an active floodplain/wetland reach, but **do not lock exact polygon until ASF L-band scene availability is proven**. Exclude excessive high-relief terrain and focus on broad floodplain when possible. A local geographic expert or dependable public reference will improve interpretation.

### Backup A: Nagapattinam / coastal Tamil Nadu wetlands

ISRO documented an S-band July 2, 2026 acquisition showing wetland/coastal land-cover contrast. Verify L-band date pairs, tide and surge confounding, and sufficient change. This is a fallback, not an already validated two-date solution.

### Backup B: Global known-data floodplain or wetland

Search for locations with readily available comparable **PROVISIONAL L-band GCOV** observations and obvious independent reference data. Prefer data over prestige of region. The documented Mozambique flood visualization from early 2026 is narratively powerful but may involve **BETA** maturity; if used, label as a demonstration/reference and never silently mix with Provisional time series.

### Mandatory catalog checklist

1. AOI polygon; time range; at least **two different acquisition times**.
2. Both scenes **NISAR L-band GCOV** for the core MVP.
3. Same polarization(s), frequency, processing maturity, preferably CRID; same relative orbit/flight direction where possible.
4. Real scene footprints overlap the exact AOI; no huge no-data masks.
5. Useful water/vegetation variation visible in backscatter; enough signal beyond noise/speckle.
6. Independent optical/cloud-free, Sentinel-1 or authoritative high-resolution/event evidence for checks.
7. Source and processing metadata can be shown publicly.
8. Data size manageable and access reproducible.

**Decision rule:** If no compatible pair is verified for Assam, immediately choose an alternative. If no pair can be processed for any candidate within the first part of the hackathon, use a preprocessed openly licensed NISAR sample pair with honest scope and provenance, rather than fabricating change.

---

## 5. Scientific methodology

### Research questions

- RQ1: Can repeat-pass NISAR L-band backscatter discriminate **open-water expansion/contraction** over a chosen floodplain with a demonstrably stronger signal than simple image differencing?
- RQ2: Where available, do multiple polarizations help distinguish **open water**, **non-inundated vegetation**, and **possibly inundated vegetation**?
- RQ3: Does contextual information, such as rainfall and historical water occurrence, improve interpretation while preserving clear separation between observational evidence and causal hypotheses?

### Stage A: Scene search & provenance

Query `asf_search`/`earthaccess` with AOI, date bounds, dataset `NISAR`, processing level `GCOV`, maturity and orbit filtering. Save scene IDs, acquisition UTC, footprint, coordinate reference system, processing CRID, polarization list, URLs, product size, license, and data origin. Preserve immutable `input_manifest.json`.

### Stage B: Geospatial preparation

Open HDF5 lazily (`h5py`, `xarray`, `rioxarray`, `h5netcdf` as appropriate). Read geocoding coordinates and EPSG. Extract available diagonal intensity terms from identical frequency and comparable acquisition modes. Verify physically valid positive power, masks, noise and no-data. Resample/mosaic to a **defined analysis grid and common area**, retaining pixel validity; do not blindly use cubic interpolation of binary masks. Check subpixel co-registration against stable terrain. Normalize/rescale only by a documented method; avoid automatically subtracting all real environmental differences away. Calculate dB for visualization/derived features and preserve linear power for relevant physical operations.

### Stage C: Interpretable baselines

1. Single-scene open-water classification using low-backscatter candidate thresholds on physically suitable polarization(s), with land/slope masking, optional Otsu or mixture-model thresholding, and connected-component cleanup.
2. Two-date `ΔdB` map and temporally paired water masks to identify gained/lost water.
3. Optional robust temporal median or persistence analysis where ≥3 comparable dates exist.
4. Differences on bare urban/shadowed areas flagged as possible geometry or scattering artifacts.

**Radar physics:** Calm open water often gives low backscatter due to specular reflection. Vegetated inundation can increase HH via trunk/water or stem/water double-bounce. Wind, incidence angle, biomass, soil moisture, crop cycles, roughness, urban structures, and rain can create lookalike signals. HH/HV or HH–HV differences are exploratory scattering indicators, **not automatic proof of inundation**.

### Stage D: More ambitious method (if time permits)

Candidate multi-feature classifier or uncertainty-aware segmentation using HH, HV, cross-channel ratios, `ΔdB`, local texture, historical water context and slope, trained on carefully selected independent or manual annotations. Gradient-boosted trees/random forests are often easier to train, inspect and validate in a hackathon than a large custom segmentation network. Potential stronger model: lightweight patch-based U-Net fine-tuned on representative, properly licensed labeled data, but only after the baseline works and test split is spatially independent. Avoid inventing pretrained NISAR-specific capabilities.

### Stage E: Changes & quantitative results

Compute valid-area changes using **physical pixel area in the projected grid**, with masks and no-data accounted for. Summarize water gained, water lost, unchanged and ambiguous class area. Show time intervals precisely; do not label observed satellite acquisition intervals “real-time.” Document selected thresholds and any class filtering. Calculate change by place and by subregion only when spatial support is adequate.

### Stage F: Context and hypothesis

- NASA GPM **IMERG** precipitation accumulation for preceding intervals, bearing in mind ~0.1° (~10 km) resolution, different time scale, and biases.
- Sentinel-2 L2A optical imagery, with cloud/shadow mask and matching-date tolerance, for visual interpretation and partial validation; water indices such as MNDWI if relevant.
- ESA Sentinel-1 SAR as secondary comparison where feasible, not a substitute for mandatory NISAR.
- EC JRC Global Surface Water historical occurrence/seasonality (latest available version may now extend through 2024). Use as **historical context**, never as 2026 event ground truth.
- SRTM / compatible DEM and slope mask for limiting terrain false positives.
- Boundaries, land cover, protected-area outlines from openly licensed reliable providers. Any affected-area overlay must be labeled a *geographic intersection*, not confirmed impact or attribution.

The narrative should say “increased observed radar evidence consistent with inundation; rainfall occurred before acquisition” rather than “NASA proves this rainfall caused the flood.”

---

## 6. Evaluation and scientific defensibility

### Evaluation dataset

Build a small but transparent labeled test set of polygons or pixels across the AOI: persistent water, temporary water, stable dry land, vegetated area, urban/ambiguous. A team member not developing the model should verify labels using independent high-resolution images, Sentinel-2 with clear skies, trustworthy flood maps, or domain references as close to the acquisition time as possible. Report cloud-limited / missing / uncertain cases as excluded or ambiguous.

### Baselines and tests

- **Baseline 0:** simple two-image absolute difference (demonstrates why raw change is insufficient).
- **Baseline 1:** HH-only/appropriate single-polarization water threshold + spatial filtering.
- **Proposed core:** multi-temporal water classification with geometry masks, available polarization features and contextual checks.
- **Optional advanced:** trained multi-feature classifier.

For independent validation, report confusion matrix, per-class precision and recall, F1/IoU for water class, area error, stable-land false-positive rate, and known error modes. Use **spatially separated** validation samples to reduce leakage. Compare with a weaker baseline, not simply self-assessed visual quality. If probability scores are shown, calibrate them or use non-numeric qualitative “needs review” indicators.

### Quality-control failure tests

- Shift one image artificially by 1–2 pixels to test registration robustness.
- Compare permanent water and stable built-up regions for false positives.
- Test threshold sensitivity; quantify changed-area sensitivity under plausible choices.
- Remove one channel to demonstrate value/limits of multi-polarization.
- Flag mixed maturities or missing corresponding channels rather than producing misleading maps.
- Check spatial dimensions, nodata propagation, units, projection, dates and zero/negative power values.
- Verify the exact source data and code behind every demo frame.

**No scores should be claimed before running experiments.** A clearly documented limitation is preferable to a fabricated 95% accuracy claim.

---

## 7. Product design and user journeys

### Audience

**Primary:** conservation/floodplain analyst investigating water changes.  
**Secondary:** educator or curious member of public.  
**Judges:** technically literate viewers needing transparent, quick scientific proof.

### User journey 1 — Explore the change

1. Home opens with a map and a single featured real study area.
2. Press **Explore the Change**, loading a reliable precomputed data package.
3. Toggle **Before / After / Difference / Water gained / Water lost**.
4. Drag swipe comparison, scrub observation dates, and click a pixel to inspect intensity and data provenance.
5. View measured area changes with units, caveats and the exact analyzed footprint.
6. Read an evidence-first narrative of plausible hydrological mechanisms.

### User journey 2 — Inspect the science

1. Enter **Science Lab**.
2. Toggle available HH, HV (or other actual available) intensity channels; see units and legend.
3. Inspect a chart of radar backscatter by date for an annotated sample region.
4. View processing lineage, masks, scene IDs, input-data quality, thresholds and limitations.
5. Download actual CSV summary/GeoJSON geometry/PNG report where practical.

### User journey 3 — Tell the story

1. Click **Guided Story**.
2. Five steps: location → cloud/optical challenge → radar data → observed change → evidence & limits.
3. Each step is navigable, subtitled, responsive and keyboard accessible.

### UI components

- Interactive map (MapLibre GL JS) with synchronized comparison views.
- Collapsible time bar with **actual available dates**, not fabricated smooth daily points.
- Four numerical summary cards: analyzed area, water gained, water lost, changed-area share (only if valid calculations exist).
- Clear data labels: **Observed**, **Derived**, **Hypothesis**, **Unverified**.
- Side panel with data provenance, timestamp, polarization and limitations.
- Mini radar-scattering explainer: what dark/bright can and cannot mean.
- Accessible color scales, high contrast, keyboard accessible controls, plain-language mode, mobile fallback.
- Good empty states and predefined demo mode when network/auth is unavailable.

### Design aesthetic

**Scientific mission control, not decorative space fantasy.** Near-black navy background, restrained cyan for radar, magenta for gain/novel change, amber for uncertainty, neutral grays for context. Maps must have an accessible alternative palette; no color-only encoding. Sparse controls, strong typographic hierarchy and annotated visual evidence. Do not create misleading synthetic satellite images or imply NASA endorsement/official status.

---

## 8. Architecture and data model

### Scientific batch pipeline

`ASF / Earthdata query → input manifest → HDF5 read/subset → QA and grid alignment → intensity channels/dB → feature derivation → change classification → validation → exported COG/PMTiles/GeoJSON/summary JSON → frontend`

### Frontend

- React + TypeScript + Vite or Next.js (pick one, not both; default Vite for deploy simplicity)
- MapLibre GL JS; `deck.gl` only if advanced overlays need it
- Tailwind CSS for styling; accessible components
- Recharts or lightweight charting for time series
- Static precomputed GeoJSON, image tiles and JSON so demo works without GPU or model inference

### Backend/processing

- Python 3.11+, `asf_search`/`earthaccess`, `h5py`, `xarray`, `rioxarray`, `rasterio`, `pyproj`, `numpy`, `scipy`, `scikit-image`, `scikit-learn` or `lightgbm`, GeoPandas; optional FastAPI for custom AOI/search API.
- Avoid dependency bloat; pin reproducible versions.
- GDAL/rasterio for Cloud Optimized GeoTIFF production, optional `rio-cogeo`, `tippecanoe`/`PMTiles` for lightweight distribution.
- No database in MVP if 1–2 case studies are static and predefined; add PostGIS only for genuine dynamic AOI querying.
- Storage: object storage or public static hosting for processed tiles; store scientific source IDs not private credential-bearing URLs.

### Proposed repository structure

```text
sarpulse/
  README.md
  LICENSE
  CITATION.cff
  ATTRIBUTION.md
  DATA_SOURCES.md
  AI_DISCLOSURE.md
  .env.example
  docs/
    methods.md
    study-area.md
    limitations.md
    validation.md
    demo-script.md
    submission.md
  science/
    requirements.txt
    notebooks/
    src/
      discover.py
      inspect_products.py
      coregister.py
      radar_features.py
      detect_change.py
      contextualize.py
      validate.py
      export_layers.py
    tests/
  data/
    README.md
    manifests/
    aoi/
    annotations/
    processed/       # small representative artifacts only
  web/
    package.json
    src/
      components/
      pages/
      lib/
      data/
  assets/
  scripts/
```

### Recommended exported schema

`scenes.json`: `scene_id`, `source`, `acquired_at_utc`, `maturity`, `crid`, `orbit_direction`, `relative_orbit`, `polarizations`, `grid_epsg`, `pixel_spacing_m`, `footprint`, `license`, `data_url`.

`analysis.json`: `aoi_id`, `source_scene_ids`, `processing_version`, `valid_area_km2`, `gained_water_km2`, `lost_water_km2`, `class_definitions`, `threshold_method`, `provenance`, `limitations`, `validation_status`.

`time_series.json`: observation dates, area metrics, data-quality flags. Do **not** fill missing dates by interpolation without visibly labeling it.

### API (optional)

- `GET /api/sites` list verified demonstrations
- `GET /api/sites/{id}/scenes` available observations and metadata
- `GET /api/sites/{id}/summary?before=...&after=...` calculations
- `GET /api/sites/{id}/layers` URLs of processed imagery/geometries
- `GET /api/sites/{id}/evidence` reference data and metadata
- `GET /api/health` health status

A static-first site is encouraged for reliability. On-demand processing is optional and should never jeopardize demo performance.

---

## 9. Feature scope and priority

### P0 — Must ship, no exceptions

- [ ] At least two **verified, comparable NISAR L-band** scenes for one AOI.
- [ ] Correct scene/geographic registration, units, masks and metadata.
- [ ] Real before/after SAR visualizations, selectable date pair.
- [ ] Meaningful difference/water-change map and numeric quantified result.
- [ ] Documented baseline and at least one validation check.
- [ ] Beautiful, functional public URL with downloadable source/code links.
- [ ] Science Lab / evidence panel with citations and limitations.
- [ ] Robust guided demo, README, license, AI disclosure and attribution.

### P1 — High-impact stretch

- [ ] Additional NISAR date for time-series demonstration.
- [ ] Multi-polarization feature analysis, justified by available channels.
- [ ] NASA GPM rainfall context aligned to actual observation dates.
- [ ] Sentinel-2 optical panel with acquisition date and cloud flag.
- [ ] Clear open-water versus inundated vegetation distinction if supported by validation.
- [ ] Comparative confusion matrix / baseline ablation.
- [ ] Export GeoJSON / area report, site-specific story steps.

### P2 — Vision, not commitments

- [ ] NISAR L + S band comparative experiment with matched locations and conditions.
- [ ] Additional study region or application class (e.g., agricultural moisture or forests).
- [ ] Multi-scene anomaly/change persistence system.
- [ ] Calibrated probabilistic uncertainty and spatially independent model benchmarking.
- [ ] Automatically selected AOI analysis and a downloadable scientific report.
- [ ] Ground station / water gauge or disaster agency cross-validation.
- [ ] Terrain-aware interferometric displacement subsystem using **different products**.
- [ ] An evidence-grounded conversational explainer with no unsupported causal claims.
- [ ] Progressive web app, low-bandwidth tiles, teacher mode or multilingual explanation.

### Explicit cut list

If time is short, cut machine learning before cutting data correctness; cut custom site search before cutting an excellent featured site; cut account/login functionality before cutting accessibility; cut animation effects before cutting reproducibility; cut AI chat before cutting baseline validation.

---

## 10. Team operating plan

Assume **four functional lanes**; adjust assignments to the real headcount (Space Apps allows up to six).

| Lane | Principal responsibility | Required demo contribution |
|---|---|---|
| Science/data lead | NISAR acquisition, QA, radar features, change algorithm | Reproducible scene pair and scientifically defensible map |
| Geospatial/validation lead | GIS layers, AOI, ground truth, baselines, uncertainty | Independent validation + limitations |
| Frontend/UX lead | Interactive maps, timeline, comparison, responsive design | Polished deployable user experience |
| Integration/story lead | Dataset manifests, backend/static exports, demo, README, submission | Single coherent build and compelling narrative |

If there are five or six, assign a dedicated geospatial processing role and a dedicated presentation/quality role. Every workstream should have one owner, one backup, one deliverable and a go/no-go deadline. Pair science and frontend early to agree on output format; otherwise the scientists may generate rasters the map cannot display.

### Integration contracts

- Scientific pipeline owns GeoTIFF/COG + GeoJSON + JSON output schemas.
- Frontend consumes those schemas via fixtures before real data exports are ready.
- Documentation records acquisition IDs and processing code version.
- Demo only presents verified results with correct dates.

---

## 11. Schedule and decision gates

### November 7–13: Allowed preparation / research

1. Review official challenge; understand NISAR SAR physics and data products.
2. Explore publicly documented data collection and map potential scenes; do not imply download/preprocessing equals original hackathon deliverable unless permitted.
3. Set up NASA Earthdata and ISRO Bhoonidhi accounts and local compute environments.
4. Agree on roles, scientific evaluation plan, UI references, Git workflow, data-size constraints.
5. Check local-event format, connectivity, available compute, registration and team page.
6. **Check latest official rules** about when actual challenge work may start; historical NASA guidance asks teams not to start actual project work before the hackathon. Planning and learning are distinct from building a submitted project.
7. November 13: review published 2026 Project Submission, Judging & Awards, and challenge Resources materials, updating all deliverable and AI disclosure requirements.

### Saturday, November 14

| Local milestone | Outcome |
|---|---|
| 09:00–11:00 | Kickoff, inspect live guidelines, select AOI/date pair, create repo and issue board |
| 11:00–15:00 | NISAR data retrieved; inspect polarizations/CRS; first usable aligned rasters; UI skeleton |
| 15:00–19:00 | Baseline change map + first area figures; frontend renders real layers |
| 19:00–23:00 | Improve classification, validation samples; comparison tool and data-source panel |
| Late Day 1 checkpoint | End-to-end demo from real observations. If not achieved, cut all stretch features |

### Sunday, November 15

| Local milestone | Outcome |
|---|---|
| Early session | Validate core method, handle QA/uncertainty and useful contextual layers |
| Midday | Finalize polished Science Lab and guided story; testing and accessibility |
| Afternoon | Record demo; add citations, datasets, assumptions, screenshots and open-source license |
| 18:00–20:00 | Submission draft, peer review, link-access test on another machine/network |
| Before 21:00 target | Submit a complete working entry early; reserve buffer until official 23:59 cutoff |

Remember that a **09:00 Saturday to 23:59 Sunday submission window is about 39 hours**, not two entire 24-hour days. Local venue operations may be shorter; obey local instructions.

### Hard stop gates

- If no verified NISAR pair after first dedicated data-access block → switch AOI.
- If classification not robust → use narrower, evidence-backed change narrative, not exaggerated labels.
- If model not validated by midday Sunday → ship transparent statistical baseline.
- If new features threaten deployability → freeze features and focus on demo, attribution, accessibility and testing.

---

## 12. Evaluation against judging criteria

2026 local event pages describe five common dimensions: **Impact, Creativity, Validity, Relevance, Presentation**. Official 2026 global rubric details are expected close to the event and must be consulted directly.

- **Impact:** choose a meaningful floodplain and show what insights a user gains beyond raw satellite images. Avoid inflated life-saving claims.
- **Creativity:** visual science storytelling, radar-specific interpretability, observability/uncertainty and a delightful time-comparison experience.
- **Validity:** true NASA/ISRO observations; documented calibration, co-registration, expected geometry, matched products, actual metrics, known limitations, reproducibility.
- **Relevance:** NISAR must be central; do not sideline it with Sentinel-2 or generic climate dashboards.
- **Presentation:** working public URL, accessible onboarding, simple explanation, exceptional 60–90 second judge walkthrough, clear attribution and link to repo.

**Differentiator:** Source-backed “Why did this pixel change?” evidence viewer: scene backscatter/channel plot + change magnitude + data-quality indicators + explanatory limits. This is more credible than an unsupported LLM explanation.

---

## 13. Demo plan and pitch

### Guided demo (roughly 90 seconds, not necessarily the official upload length)

0–10s: “Clouds hide much of what optical satellites see during floods. Radar lets us investigate the surface anyway.”  
10–25s: Globe/map flies to verified floodplain with region/time labels.  
25–40s: Time-synchronized before/after NISAR imagery and difference overlay.  
40–55s: Water gain/loss and site summary from real calculations.  
55–70s: Science Lab opens HH/HV channels, scatter/temporal plot, exact scene IDs, independent validation.  
70–90s: Explain plausible hydrological context, uncertainty, implications and what users can explore. Close with “SARPulse: Earth's changes. Revealed by radar.”

**Important:** The 2025 official judges' document mentioned special demo length/slide limits and AI disclosure requirements. **Do not assume those specific 2025 limits are the 2026 rules.** On Nov 13, inspect the 2026 submission guide and create precisely the required demo duration and format.

### Pitch outline

1. Opening human hook (why this site matters).
2. Data problem (complex radar + cloudy conditions + interpretation difficulty).
3. Demonstration (specific observation and measured result).
4. Scientific approach (two or three key methods and actual data sources).
5. Validation and limitations (where it succeeds; where it doesn't).
6. Impact and extendability (what the system would enable next).

### Judges' hard questions and answers we must prepare

1. **What exactly is NISAR contributing?** Show derived NISAR layers and actual scene IDs.
2. **What makes this different from Worldview or a generic GIS app?** Provenance-rich comparative radar inference, area quantification, validation and understandable radar scattering explanations.
3. **How do you know change isn't processing noise?** Same maturity/CRID where possible; geometry matching; masks; stable-land controls; ablation/QA.
4. **How do you prove it is water?** Independent observations/annotations, polarization physics, slope and land-cover context, confusion matrix.
5. **Can SAR see floods beneath trees?** It can sometimes detect characteristic double-bounce; not universal; dependent on vegetation, frequency and geometry.
6. **Why not train a giant model?** Strong reproducible baseline suits limited labels and scientific interpretability; ML only if it improves held-out evidence.
7. **Is it live monitoring?** No: observation-based historical/near-recent analysis with documented acquisition cadence and latency, not continuous operational alerts.
8. **Where's the uncertainty?** Data-quality masks, ambiguous classes, threshold sensitivity, validation metrics and metadata.
9. **Is the rainfall the cause?** It is contextual evidence, not definitive attribution; tides, flows, engineered releases and antecedent conditions may also matter.
10. **What would the next iteration do?** More AOIs, validated L/S integration, stronger labels, time-series baselines and partnerships with domain specialists.

---

## 14. Submission package & compliance

- Public GitHub repository with source code, LICENSE, README, architecture diagram, setup steps.
- Public hosted working demo; no passwords required to inspect the featured study area.
- Project page with challenge selected, team membership and requested submission text.
- Reproducible analysis scripts, example configuration, input scene IDs and output manifests.
- Clear NASA and ISRO data attribution, and licenses for ancillary imagery/layers.
- SCIENCE.md or docs/methods.md, independent validation evidence, exact known limits.
- Screenshots, short compliant demo video/slides according to **2026** guidelines.
- AI usage disclosure and proper identification of any AI-generated imagery, scripts, code or text if required.
- Do **not** alter NASA logos or place unlicensed NASA marks on AI-generated promotional art; product should not appear NASA-endorsed.
- Final regression tests: landing link, mobile, map tiles, dataset citations, sample download, zero secrets committed.

---

## 15. Reproducibility, governance, and risk register

| Risk | Severity | Mitigation |
|---|---|---|
| No matched NISAR dates in first AOI | Critical | Catalog go/no-go; two backup regions; use real accessible sample pair |
| Maturity/CRID confusion | Critical | Strict metadata matching and warning/abstention |
| Unavailable Earthdata credentials / massive downloads | High | Test logins; use subsets/streaming, precompute outputs; static public demo |
| Wrong radar physics / flooded vegetation mislabeled | High | Conservative water focus; validation; show ambiguities |
| Poor optical validation due to clouds | High | Sentinel-1/reference polygons; label missing validation transparently |
| Registration or coordinate mismatch | High | Stable control areas, grid checks, masks and reprojection tests |
| ML effort displaces core product | High | P0 baseline first; optional model only if superior |
| Demo website requires live processing | High | Precompute and publish stable tiles/JSON |
| Fake or uncalibrated confidence values | High | Use measured uncertainty or qualitative indicators |
| Submission rules change on Nov 13 | High | Dedicated official guide review and compliance checklist |
| User confusion | Medium | Explain observed/derived/hypothesized, accessible legends, simple mode |
| Team integration friction | High | Explicit schemas and feature freeze |

### Reproducibility guarantee

Every derived map is associated with a manifest containing source product IDs and timestamps, polarization, processing mode, software version/hash, AOI bounding polygon, resampling method, masking, threshold/model version and data licensing. Any delivered number must be recomputable from those inputs. Generate `DATA_SOURCES.md` from the manifest where possible.

---

## 16. Resource directory and research citations

**Official hackathon and challenge**

- 2026 challenge: https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/
- 2026 event timeline & submission: https://www.spaceappschallenge.org/2026/
- 2026 participation terms: https://www.spaceappschallenge.org/legal/

**NASA and ISRO mission & data**

- NASA NISAR mission: https://science.nasa.gov/mission/nisar/
- NISAR availability and processing maturity: https://nisar-docs.asf.alaska.edu/availability-overview/
- NISAR product types: https://nisar-docs.asf.alaska.edu/products-overview/
- NISAR GCOV documentation: https://nisar-docs.asf.alaska.edu/gcov/
- NISAR known issues: https://nisar-docs.asf.alaska.edu/nisar-known-issues/
- Data access and Earthdata authorization: https://nisar-docs.asf.alaska.edu/access-overview/
- ASF Vertex: https://search.asf.alaska.edu/
- ASF `asf_search` documentation: https://nisar-docs.asf.alaska.edu/asf-search/
- ASF NISAR Cookbook, search & stream: https://asfopensarlab.github.io/NISAR_Cookbook/search-stream-nisar-asf-search/
- ASF NISAR Cookbook, data access: https://asfopensarlab.github.io/NISAR_Cookbook/nisar-data-access/
- ISRO S-band product release (Brahmaputra, Nagapattinam scene examples): https://www.isro.gov.in/NISARS_Band_SAR_Data_Products_Release.html
- ISRO Bhoonidhi: https://bhoonidhi.nrsc.gov.in/NISAR/
- NASA visualization of Mozambique flooding: https://svs.gsfc.nasa.gov/5661
- IIRS scientific example of L/S wetland penetration: https://science.iirs.gov.in/seeing-through-forests-how-nisar-reveals-what-lies-beneath/

**Environmental context and evaluation**

- NASA GPM IMERG: https://gpm.nasa.gov/data/imerg
- NASA GPM data directory: https://gpm.nasa.gov/data/directory
- NASA rainfall caveats: https://science.data.nasa.gov/disasters/data-gallery/gpm-imerg-precipitation
- Sentinel-2 L2A/SCL documentation: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html
- JRC Global Surface Water downloads: https://global-surface-water.appspot.com/download
- JRC GSW v1.4 on Earth Engine (check newer v1.5 access): https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater

**Research caution:** Document accessible published sample imagery is not equivalent to verified matched NISAR L-band temporal granules for the proposed AOI. No real ground-truth validation or performance figure has been generated for SARPulse as of this planning document. Results must come from actual implementation and tests during the event, subject to its rules.

---

## 17. Definition of done

The project is **submission ready** when:

- [ ] A stranger can access a working demo without an account.
- [ ] The demo loads a real, attributed multi-date NISAR-backed analysis.
- [ ] The before/after/change visualizations reflect the same overlapping AOI and correct acquisition dates.
- [ ] One defensible quantitative change result is accompanied by an explicit method and data quality statement.
- [ ] The science panel answers the most important skeptical questions.
- [ ] At least a minimal reference check and error/limitation analysis is included.
- [ ] README, attribution, code licensing, AI disclosure, reproducibility, submission text and demo video all comply with current rules.
- [ ] All links work and no credentials or private information were committed.
- [ ] The final submission is completed before **November 15, 2026, 23:59 local time**.

**Guiding principle:** One extraordinary, reproducible scientific story beats a hundred unfinished features.
