# SARPulse — NASA Space Apps 2026 submission

**Superseded:** use [SUBMISSION_FINAL.md](SUBMISSION_FINAL.md), which describes the delivered real-data application and working public demo. The completion-assumption text below is historical and must not be pasted as the current project status.

Team StarFire · Dancing with the SARs · Prepared November 15, 2026

**Team editing note — do not paste this note into the form:** This is a completion-assumption draft, as requested by Shoaib. The product descriptions below assume the planned experience has shipped. Check them against the final build before publishing. Catalog metadata is present, but this session has not yet processed real NISAR pixels or validated environmental results. No accuracy, flood-area or population-impact figures are invented here. The project URL is supplied by Shoaib; it did not resolve in the local check and needs DNS/hosting verification. Replace the demo-link placeholder and remove any capability or resource that is absent from the final delivery.

## 1. Project Name

SARPulse — Earth's changes. Revealed by radar.

## 2. Summary

Paste the following into **Summary** (within the 1,500-character limit):

SARPulse turns complex NASA–ISRO NISAR radar observations into an interactive investigation of Earth's changing water landscapes. Built by Team StarFire for Dancing with the SARs, it brings together dated radar imagery, before-and-after comparisons, open-water change maps and a Science Lab for inspecting the evidence.

Our flagship investigation focuses on the Brahmaputra floodplain in Assam, where shifting channels and seasonal water make surface change both important and difficult to interpret. Users can explore water expansion and contraction, inspect HH/HV radar measurements, and open a Change Passport linking each interpretation to source acquisitions, processing methods and limitations.

SARPulse separates measured signals, derived classifications, contextual evidence and hypotheses. It helps researchers, educators and floodplain managers understand what radar measurements support, where uncertainty remains, and why a change deserves further investigation. A reproducible, precomputed workflow keeps the experience fast while preserving scientific traceability.

## 3. Project Demonstration

**Public demo URL:** `[REPLACE WITH PUBLIC LINK TO THE FINAL SLIDES OR VIDEO]`

This field must link directly to an accessible demonstration: **no more than seven slides, including the title and introduction, OR a video of 30 seconds or less**. The website URL alone does not establish compliance with the demonstration format. No login, password or permission request may be required.

## 4. Project

https://sarpulse.shoaibssm.me

Source repository, if useful as an additional link in Project Details:

https://github.com/shoaib2000857/Sarpulse

## 5. Project Details

Paste from **Earth's changes, made inspectable** through **Built by Team StarFire** below. These are completion-assumption descriptions; remove unshipped features before submitting.

### Earth's changes, made inspectable

Satellite radar can reveal surface information through clouds and in darkness, but interpreting that information takes more than comparing two pictures. Radar backscatter responds to surface roughness, moisture, vegetation and acquisition geometry. A darker or brighter pixel can have several explanations.

SARPulse makes that investigation accessible. Our central question is: **How can comparable NISAR observations help people identify and understand changes in open water across a floodplain?**

We focus on the Brahmaputra floodplain around Majuli, Assam, rather than claiming to solve every kind of Earth-surface change. The region's braided channels, water bodies and surrounding vegetation provide a meaningful setting for exploring water expansion and contraction. Our approach is reusable for other locations once compatible observations and suitable validation evidence are available.

### What users can do

**Earth Time Machine:** Compare dated radar acquisitions, move between observations and reveal changes using before-and-after views. Radar layers are presented as scientific backscatter measurements, with acquisition dates and units, rather than as ordinary optical photographs.

**Change Intelligence Map:** Inspect classified open-water gain, loss, stable water, land and ambiguous areas. Area summaries use physical pixel area over the valid comparison footprint. Water-class changes are presented as evidence consistent with changing open-water extent; they are not automatically labeled confirmed flooding.

**Science Lab:** Examine the available HH and HV channels, temporal backscatter differences, selected thresholds, sensitivity ranges, scene metadata and processing lineage. Missing channels and unsupported analyses remain explicit.

**Change Passport:** Investigate a location through four distinct layers of explanation: radar measurements, derived classifications, contextual information and physical hypotheses. The passport retains source identifiers, observation times, processing information and limitations so users can inspect the basis of an interpretation.

**Context and reproducibility:** Precomputed geographic outputs make the featured investigation available without launching a large processing job during a demonstration. Documented scripts and manifests allow the analysis to be reproduced. Any rainfall, terrain, optical or historical-water context shown in the final investigation is identified separately from the NISAR measurements and from independent validation.

### How the scientific workflow works

1. **Discover comparable observations.** Search NASA's ASF catalog for NISAR L2 GCOV products intersecting the study area. Preserve acquisition UTC, source product identifiers, polarization, track, orbit direction, processing release and data maturity.
2. **Prepare a common analysis grid.** Read the required HDF5 windows, check available covariance terms, retain valid-data masks and align the observations on a shared projected grid. Average radar power in linear units before converting positive valid values to decibels with `10 × log10(power)`.
3. **Establish an interpretable water baseline.** Reduce speckle and use HH backscatter thresholds to identify open-water candidates on each date. The current statistical approach uses split-based Otsu thresholding with a flagged global fallback when suitable bimodal tiles are unavailable.
4. **Quantify changes conservatively.** Compare water classifications across time, require a sufficient directional backscatter change for confident gain or loss, and retain an ambiguous class near uncertain thresholds. Report gained and lost area in square kilometres over valid pixels.
5. **Inspect uncertainty and alternative explanations.** Explore sensitivity to threshold choices and compare with a secondary HH/HV Gaussian-mixture method. Agreement between two methods measures internal consistency; it is not a substitute for accuracy against independent labels.
6. **Deliver traceable outputs.** Export geospatial layers and metadata for the interactive application and expose evidence through a small FastAPI service. Processing is performed ahead of viewing, preserving a reliable demonstration path.

### Why this approach is creative

The contribution is the connection between a visual change map and the evidence needed to interpret it. SARPulse lets a curious viewer follow a change back to its measurements, metadata, methods and limitations. The same experience supports a quick public exploration and a more detailed scientific inspection.

Our Change Passport turns “this pixel changed” into a better question: **What does the measurement support, and what else could explain it?** That makes interpretation and uncertainty part of the product experience.

### Benefits and intended impact

For researchers and floodplain managers, SARPulse offers an accessible starting point for identifying changes that merit further investigation. For educators and the public, it explains why radar is useful where clouds limit optical observations and why radar interpretation requires care. For future projects, its precomputed outputs and source manifests provide a reusable foundation for additional areas and environmental questions.

SARPulse is a research and communication prototype. It is not an operational warning system, flood forecast or emergency-response authority.

### Scientific limitations and design choices

- Smooth sand, bare soil and radar shadow can resemble dark open water. Roughened water can be brighter and may be missed.
- Flooded vegetation can brighten through double-bounce scattering. The open-water baseline does not establish inundation beneath vegetation.
- Matching processing maturity, release, polarization and geometry is essential; processing differences can resemble environmental change.
- Provisional products retain their provisional status in the interpretation. Mission calibration maturity and validation of our classifier are separate questions.
- Terrain effects, noise, speckle, residual registration error and acquisition spacing limit what can be concluded.
- Historical water occurrence and rainfall are context, not proof of a particular flood or its cause.
- Threshold sensitivity ranges describe parameter sensitivity; they are not calibrated probabilities or full confidence intervals for environmental truth.
- Quantitative accuracy requires an independent, suitably dated reference. We make no unsupported accuracy claim.
- GCOV backscatter alone does not measure ground displacement. Additional change domains require their own products, methods and evaluation.

### Technology

Scientific processing uses Python, NumPy, SciPy, h5py, rasterio, pyproj and scikit-learn. NASA archive discovery and access use ASF services and earthaccess. A FastAPI backend serves scene metadata, analysis summaries, map-layer manifests, contextual evidence and Change Passports. The planned browser application uses React, TypeScript, Vite and MapLibre GL JS. Precomputed rasters, web overlays and JSON metadata keep heavy scientific processing outside the viewing experience.

### Built by Team StarFire

Shoaib — core platform, shared contracts, orchestration and integration; Veer — satellite data and preprocessing; Naveen — change detection, evaluation and uncertainty; Nidhi — frontend and geographic visualization; Shridhar — backend, evidence and contextual data; Hansika — UI/UX, storytelling and presentation.

Project: https://sarpulse.shoaibssm.me
Source: https://github.com/shoaib2000857/Sarpulse

## 6. Use of Super Intelligence (SI)

The actual dropdown options were not included in the supplied form text. Select the options corresponding to **SI-assisted code development** and **SI-assisted writing/documentation**, plus any other uses that actually occurred. **Do not select “I did not use SI.”**

Suggested disclosure text for the project documentation or any available explanation field:

> We used OpenAI Codex to assist with code review, integration, implementation, debugging, tests and documentation, including drafting submission text. The project direction and team requirements were supplied by Team StarFire. SI assistance is disclosed in the repository and processing metadata. SI was not used to fabricate NASA acquisitions, environmental observations, reference labels, flood areas, population impacts or accuracy figures. Synthetic integration fixtures are explicitly marked “SYNTHETIC/DEMO — NOT NASA OBSERVATIONS” and are separate from observational results. Any SI-generated media included in the final delivery will be identified according to the 2026 submission guide. SI assistance does not constitute scientific validation or NASA endorsement.

**Before publishing:** Confirm the final SI-use selections with the team, including any use of Claude Code or other assistants by contributors. The supplied guide permits SI to accelerate development and requires disclosure of how it was used.

Required indicators in the delivery:

- Code and any SI-generated data: descriptive acknowledgement and metadata.
- SI-generated images/video, if used: visible SI-generation watermark.
- SI-generated audio, if used: acknowledgement in descriptive text and metadata.
- Do not generate, alter or incorporate NASA branding into SI-generated content contrary to the supplied rules.

## 7. NASA Data — form link entries

Use **Add New Link** for each resource actually used. These resources support the current workflow and research; record final observational products separately. A resource link is not evidence that the associated scientific analysis has run.

| Link Text | Link URL |
| --- | --- |
| NASA–ISRO NISAR L2 GCOV — product documentation | https://nisar-docs.asf.alaska.edu/gcov/ |
| NASA ASF DAAC — NISAR data discovery through Vertex | https://search.asf.alaska.edu/ |
| NISAR Data User Guide — access, products and processing maturity | https://nisar-docs.asf.alaska.edu/ |
| NASA Earthdata — archive access and discovery | https://search.earthdata.nasa.gov/search |
| NASA earthaccess — authenticated scientific data access library | https://github.com/nsidc/earthaccess |

The following entries are **conditional**. Add them only if they were actually used in the final build or cited research; do not imply data integration from a link alone.

| Link Text | Link URL | When to include |
| --- | --- | --- |
| NASA GPM IMERG — precipitation context | https://gpm.nasa.gov/data/imerg | If rainfall data or this resource is used; identify actual product/version and date interval |
| NASA Earthdata — introduction to SAR | https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar | If used for scientific explanation |
| NASA NISAR — polarimetry | https://science.nasa.gov/mission/nisar/polarimetry/ | If used for scattering/polarization explanation |
| NASA ASF NISAR Cookbook | https://asfopensarlab.github.io/NISAR_Cookbook/search-stream-nisar-asf-search/ | If code/methods or tutorial content are used |
| NASA JPL — NISAR Mississippi River Delta example | https://www.jpl.nasa.gov/news/nasa-isro-radar-mission-peers-through-clouds-to-see-mississippi-river-delta/ | If cited in research or if its material is used, with applicable attribution |

### Candidate acquisition record — internal verification aid

The repository catalog identifies the following **production, provisional** pair in the same stack. These are catalog records, **not a claim of processed or independently validated results**:

- Collection: `NISAR_L2_GCOV_PROVISIONAL_V1`.
- Stack: `T040A_F015_4005_DHDH_PR_P05023`.
- Before UTC: `2026-07-22T23:05:28Z`.
- Before ID: `NISAR_L2_PR_GCOV_026_040_A_015_4005_DHDH_A_20260722T230528_20260722T230602_P05023_N_F_J_001`.
- After UTC: `2026-10-14T23:05:26Z`.
- After ID: `NISAR_L2_PR_GCOV_033_040_A_015_4005_DHDH_A_20261014T230526_20261014T230601_P05023_N_F_J_001`.
- Processing CRID: `P05023`; track 40, ascending, frame 15; required frequency-A channels HH/HV.
- Source manifests: `data/manifests/brahmaputra-majuli/`.

Once processed, add the actual source manifest and output-provenance link to the submission. If a different pair is used, replace this record and any dates shown in the product or demonstration.

## 8. Space Agency Partner & Other Data — form link entries

List tools as well as data. Include each dependency actually used in the delivery and retain its applicable license; installation of a package alone does not establish scientific use of its datasets.

| Link Text | Link URL |
| --- | --- |
| SARPulse — Team StarFire source code | https://github.com/shoaib2000857/Sarpulse |
| Python | https://www.python.org/ |
| NumPy | https://numpy.org/ |
| SciPy | https://scipy.org/ |
| h5py | https://www.h5py.org/ |
| Rasterio | https://rasterio.readthedocs.io/ |
| GDAL — geospatial raster operations through Rasterio | https://gdal.org/ |
| pyproj and PROJ — coordinate transformations | https://pyproj4.github.io/pyproj/stable/ |
| scikit-learn — statistical mixture-method comparison | https://scikit-learn.org/ |
| FastAPI | https://fastapi.tiangolo.com/ |
| Pydantic — data-contract validation | https://docs.pydantic.dev/ |
| Uvicorn — ASGI server | https://www.uvicorn.org/ |
| Requests — ASF HTTP catalog queries | https://requests.readthedocs.io/ |
| pytest — software verification | https://docs.pytest.org/ |
| HTTPX — API testing | https://www.python-httpx.org/ |
| GitHub — source hosting and integration | https://github.com/ |
| uv — Python environment and dependency management | https://docs.astral.sh/uv/ |
| OpenAI Codex — SI-assisted development and documentation | https://openai.com/codex/ |

Add the following **only when used**:

| Link Text | Link URL | Scope |
| --- | --- | --- |
| Copernicus DEM GLO-30 — ESA/Copernicus terrain context | https://registry.opendata.aws/copernicus-dem/ | DEM/slope context; retain required notices |
| EC JRC Global Surface Water | https://global-surface-water.appspot.com/ | Historical occurrence; the implemented adapter uses v1.4, 1984–2021 |
| ESA Copernicus Sentinel-2 | https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-2 | Optical context or independent reference, if actually acquired |
| ISRO NISAR S-band product examples | https://www.isro.gov.in/NISARS_Band_SAR_Data_Products_Release.html | Published examples/research; do not claim paired S-band analysis unless performed |
| React | https://react.dev/ | Final frontend |
| TypeScript | https://www.typescriptlang.org/ | Final frontend |
| Vite | https://vite.dev/ | Final frontend |
| MapLibre GL JS | https://maplibre.org/maplibre-gl-js/docs/ | Final interactive map |
| Tailwind CSS | https://tailwindcss.com/ | If used by the final frontend |
| OpenStreetMap | https://www.openstreetmap.org/copyright | If its map data or tiles are displayed; also cite the actual tile provider |
| Claude Code | https://claude.com/product/claude-code | If a teammate used it |

Also credit any actual fonts, icons, basemap providers, hosting platform, media, tutorial code, copied snippets and other libraries used by the final frontend. This list cannot be finalized until Nidhi/Hansika's delivery is inspected.

## 9. Demonstration content — choose one format

### Option A: at most seven English slides

This is a **content outline**, not an exported presentation. Hansika can use it to create the final deck.

1. **SARPulse — Earth's changes. Revealed by radar.** Team StarFire; Shoaib, Veer, Naveen, Nidhi, Shridhar and Hansika; Dancing with the SARs. Use a screenshot of the actual application.
2. **The problem.** Clouds limit optical observation; radar is powerful but difficult to interpret. Show the study-area map and explain why water changes matter.
3. **NASA data → evidence.** Show actual NISAR source dates, HH/HV availability and the shared-grid workflow. Identify the product maturity.
4. **Explore the change.** Show the real before/after comparison and classified map with a legible legend. Include only measurements exported from the processed data.
5. **Open the Change Passport.** Show measurements, source IDs, derived interpretation and limitations from one real location.
6. **Check the science.** State the method, threshold sensitivity and independent-reference status. Show an ambiguous case. Internal method agreement must not be labeled accuracy.
7. **Why it matters and what comes next.** Explain research/education value, current limits and expansion to further verified regions. Include project and source URLs plus concise credits.

### Option B: video of 30 seconds or less

Target **27–29 seconds**, including any title and ending frames. Rehearse and measure the actual export.

Suggested narration:

> I'm Shoaib from Team StarFire. For Dancing with the SARs, we built SARPulse: Earth's changes, revealed by radar. Explore NISAR observations of the Brahmaputra floodplain, compare water changes, and inspect the evidence behind each interpretation. Change Passports connect radar measurements, source dates and limitations. Our goal: help people understand changing landscapes while making uncertainty visible.

Suggested shots:

- 0–4 seconds: team/project title and actual study-area map.
- 4–12 seconds: dated before/after radar comparison.
- 12–20 seconds: water-change layer and measured summary, if available.
- 20–26 seconds: Change Passport and Science Lab with legible evidence.
- 26–29 seconds: project URL and tagline.

Do not fill the clip with invented satellite imagery or result numbers. Any SI-generated media must carry the required indicators. Do not include likenesses or voices of people under 18 in the final project or demo, per the supplied guide; use an adult narrator or screen-only presentation as appropriate.

## 10. Final verification before Submit for Judging

- [ ] Confirm the description matches the final build; remove absent features and datasets.
- [ ] Replace the demo placeholder with the real public video/deck link.
- [ ] Confirm video is <=30 seconds OR deck is <=7 slides including title and intro.
- [ ] Confirm https://sarpulse.shoaibssm.me loads publicly without authentication.
- [ ] Confirm the repository and any linked materials are publicly accessible.
- [ ] Test links in a private browser; inspect the actual final demo export.
- [ ] Check the final input manifest and provenance; distinguish real outputs from synthetic fixtures.
- [ ] State independent-validation status accurately; include no invented accuracy or impact figures.
- [ ] Ensure English submission/deck text; any non-English video speech needs English subtitles.
- [ ] Include all actual NASA, partner and third-party resources, code, tools and assets.
- [ ] Add SI descriptive indicators/metadata and media watermarks where applicable.
- [ ] Confirm rights/attribution, original-work attestation and absence of prohibited under-18 likenesses.
- [ ] Confirm all six team members are accepted participants at the same Local Event.
- [ ] Shoaib reviews the Terms and Conditions and originality confirmations personally.
- [ ] Save Progress, then click **Submit for Judging** before November 15, 2026, 23:59 in the applicable event time zone. Universal Event uses the Team Owner's residence time zone.
- [ ] Verify the success banner and the final submission timestamp. Saving alone is not submission.

## 11. Sources and precedence

The team supplied the November 13, 2026 Project Submission Guide, the live Project form, the challenge statement and the Resources tab in conversation and `infodump.md`. These supplied requirements supersede the older master-plan proposal for a 90-second submission demo. The long walkthrough may be used internally; the submitted video must obey the 30-second limit.

- Official guide: https://www.spaceappschallenge.org/resources/project-submission-guide/
- Challenge: https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/
- Terms: https://www.spaceappschallenge.org/legal/
- Team source context: `StarFire_SARPulse_2026_Master_Plan (1).md`, `infodump.md`.

This draft does not submit the project, certify team eligibility, verify hosting or establish completed scientific results.
