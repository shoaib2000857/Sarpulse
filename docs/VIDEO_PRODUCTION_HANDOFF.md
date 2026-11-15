# SARPulse — complete context and cinematic video production brief

Prepared for Shoaib's separate video-editing Codex session on November 16, 2026. This is a production instruction file, not a finished video or an assertion that new renders exist. Project baseline: main commit `bc9c037` (real-data release, merged PR #12). Recheck current files and studio capabilities when beginning.

## Start here: the assignment

Produce a polished cinematic film introducing **SARPulse**, Team **StarFire**'s Earth-observation investigation platform. Shoaib explicitly wants a beautifully made film using a code motion framework such as **HyperFrames**, with convincing 3D animation, realistic lighting/materials, strong composition, purposeful camera work and cinematic sound. Build and inspect an actual edited film, retaining its editable sources. A timed sequence of static slides is insufficient for this brief.

Use **HyperFrames for authored typography, interface/evidence animation and motion graphics**, **Blender for genuine 3D shots**, and **DaVinci Resolve as the main editor, colour and audio finishing environment**. Fusion or After Effects can support suitable compositing. Choose techniques that serve the story; the framework alone does not establish visual quality. The current local HyperFrames baseline has verified renders and transparent-title export, documented below. Recheck the relevant capability before production.

The user is asking for production, not a long research exercise. Make routine reversible creative decisions and proceed. Do not repeatedly ask for app-launch permission. Paid generation, credit spending and security changes retain their separate constraints in the studio instructions. This brief authorizes no paid API or generation spend.

## Absolute roots and public links

| Item | Absolute path / URL |
| --- | --- |
| Project repository | `D:/Hackathon/NASA/Sarpulse` |
| Studio workspace | `D:/VideoEditing` |
| This brief | `D:/Hackathon/NASA/Sarpulse/docs/VIDEO_PRODUCTION_HANDOFF.md` |
| Public app | https://sarpulse.adoredrose256.chatgpt.site |
| Source repository | https://github.com/shoaib2000857/Sarpulse |
| Existing seven-slide web demo | https://sarpulse.adoredrose256.chatgpt.site/demo/ |
| Existing seven-page PDF demo | https://sarpulse.adoredrose256.chatgpt.site/demo/sarpulse-demo.pdf |
| Requested custom domain | `https://sarpulse.shoaibssm.me` — DNS was pending at this handoff; verify before printing it in a final end card |

Use the working public URL in the film unless the requested domain has actually passed DNS and HTTPS verification. Domain records are documented at `D:/Hackathon/NASA/Sarpulse/docs/PUBLIC_DEPLOYMENT.md`.

Read these studio files before launching tools:

- `D:/VideoEditing/AGENTS.md`
- `D:/VideoEditing/STUDIO_WORKFLOW.md`
- `D:/VideoEditing/setup-audit/hyperframes-test/README.md`
- `D:/VideoEditing/setup-audit/HYPERFRAMES_ALPHA_2026-11-02.md`
- `D:/VideoEditing/setup-audit/RESOLVE_TIMESTAMPS_2026-11-06.md`
- `D:/VideoEditing/setup-audit/ADOBE_CONNECTIONS_2026-10-17.md` if using Adobe hosts.
- `D:/VideoEditing/setup-audit/ILLUSTRATOR_AUTOSTART_FIX_2026-10-29.md` if Illustrator is needed.

The verified local HyperFrames installation is `D:/VideoEditing/tools/motion-graphics`, with wrapper `D:/VideoEditing/tools/motion-graphics/hyperframes.cmd`, pinned HyperFrames 0.8.168 and GSAP 3.14.2 in the recorded audit. This does not establish the current version; inspect before use. Remotion was not installed at the recorded audit. The basic and later alpha tests establish specific render paths, not universal 3D/audio support.

Read these project files for authoritative delivered scope:

- `D:/Hackathon/NASA/Sarpulse/README.md`
- `D:/Hackathon/NASA/Sarpulse/AGENTS.md`
- `D:/Hackathon/NASA/Sarpulse/docs/FINAL_STATUS.md`
- `D:/Hackathon/NASA/Sarpulse/docs/SUBMISSION_FINAL.md`
- `D:/Hackathon/NASA/Sarpulse/docs/DATA_INTEGRITY.md`
- `D:/Hackathon/NASA/Sarpulse/DATA_SOURCES.md`
- `D:/Hackathon/NASA/Sarpulse/ATTRIBUTION.md`
- `D:/Hackathon/NASA/Sarpulse/AI_DISCLOSURE.md`
- `D:/Hackathon/NASA/Sarpulse/web/public/models/ATTRIBUTION.md`

The original ambition is in `D:/Hackathon/NASA/Sarpulse/StarFire_SARPulse_2026_Master_Plan (1).md`; the supplied official guide is in `D:/Hackathon/NASA/Sarpulse/infodump.md`. The plan includes conditional ideas that did not ship. The final status, actual UI and scientific JSON take precedence over aspirational descriptions. `docs/SUBMISSION_DRAFT.md` and the November 15 integration notes are historical, superseded material.

## Identity, problem and story

**Name:** SARPulse. **Tagline:** Earth's changes. Revealed by radar. **Team:** StarFire. **Challenge:** Dancing with the SARs, NASA Space Apps 2026. SARPulse is an independent team project, not an official NASA/ISRO product or endorsed operational service.

Its purpose is to make difficult NASA–ISRO NISAR L-band SAR measurements understandable and traceable. The focus is surface-water and wetland change. Clouds can limit optical observation; radar offers another kind of measurement. Interpreting that measurement requires checks, rather than simply subtracting two pictures and calling the result a flood.

The film's central promise is: **See where the radar changed. Inspect what the evidence supports. Understand the uncertainty.** The distinctive feature is the **Change Passport**, which links a location's interpretation to real acquisition IDs, dates, physical values, method and limitations. Let the camera journey progress from Earth to a real floodplain, into the application, then into the evidence behind one highlighted location.

Intended audiences: hackathon judges, educators, environmental researchers, floodplain managers and interested citizens. The film should feel like a precise Earth-observation instrument brought to life: atmospheric but legible, technically credible and emotionally engaging.

## What actually exists

- Ingestion: discovery and inspection of real NISAR L2 GCOV HDF5; available HH/HV channel inspection; masking; common projected-grid alignment; source metadata.
- Analysis: filtered backscatter, interpretable statistical water classification, temporal change rules, candidate water gain/loss, stable classes, ambiguous areas, threshold sensitivity, secondary multi-polarization consistency comparison, baseline diagnostics and optical-reference evaluation for one case.
- Backend: FastAPI scene/summary/layer/sample/evidence delivery and point Change Passports. The full API reads the actual analysed raster pixel.
- Frontend: React/TypeScript/Vite, MapLibre maps, georeferenced radar layers, before/after views, timeline/layer controls, study-area selection, change statistics, Science Lab, Change Passport and downloads, guided Story Mode, and a Three.js/React Three Fiber 3D introductory experience.
- Static public delivery: precomputed data without Earthdata login; point passports use a disclosed nearest precomputed sample and distance. Do not imply that the public static site runs a new global satellite-processing job per click.
- Exports: PNG layers, scientific GeoTIFFs, CSV, JSON metadata/provenance and passports.
- Delivery: Docker combines UI/API/data; CI checks Python on Windows/Linux and frontend types/tests/build. Release evidence includes 40 passing Python tests, 22 frontend tests, connected-science browser checks and complete Docker/public-browser smoke checks. These are software checks, not scientific accuracy.
- Existing seven-slide demo and PDF. They are supporting evidence/reference assets, not the finished cinematic film requested here.

Not delivered: operational flood alerts, verified impacted-population estimates, validated vegetated-inundation mapping, supervised deep-learning superiority, real-time global processing, L/S fusion, GCOV displacement measurement, or a functioning rainfall narrative in the published cases. Do not advertise these as current features.

## Scientific facts available for titles and graphics

Use the actual JSON as the numerical source of truth. Areas below are **classifier-derived candidate changes**, not independently established changes in flood extent. Keep that qualification visible when showing a number.

| Case | Before / after UTC | Valid comparison area | Candidate gain | Candidate loss | Ambiguous area |
| --- | --- | --- | --- | --- | --- |
| Brahmaputra–Majuli, Assam, India | July 22, 2026 23:05:28 / October 14, 2026 23:05:26 | 1,343.8716 km² | 6.7768 km² | 216.2052 km² | 129.0708 km² |
| Biesbosch wetlands, Netherlands | July 19, 2026 18:57:41 / October 11, 2026 18:57:39 | 363.0144 km² | 2.7776 km² | 6.3200 km² | 108.3264 km² |

All four sources are genuine provisional NISAR L2 GCOV, processing CRID P05023, HH/HV. Assam uses track 40 ascending/frame 15 and EPSG:32646; Biesbosch track 167 descending/frame 62 and EPSG:32631. Consult delivered provenance for final grid spacing and processing parameters rather than inventing detail. Source acquisition IDs and download URLs are preserved in each site's `scenes.json`/`provenance.json`.

Assam was retrieved through the user's local Earthdata/ASF access. The Netherlands native subsets came through a documented public mirror; identities were corroborated against ASF metadata. The mirror provenance does not establish full-byte equality with an independent ASF download. Terrain and historical-water context are separate from primary observations.

**Evaluation:** Biesbosch's automatic Sentinel-2C L2A SCL reference was acquired July 15, 2026 at 10:46:41.387Z, 4.34 days before the first radar acquisition. Precision 0.2605, recall 0.8906, F1 0.403. The baseline has substantial false positives. This is agreement with an automatic, time-offset reference, not field accuracy. July radar thresholding has a weak-bimodality flag. Assam has no independent reference comparison. Never replace these facts with an attractive invented accuracy score or present internal model agreement as accuracy.

Backscatter can respond to roughness, moisture, vegetation, geometry and speckle. The conversion is `gamma0_dB = 10 log10(positive valid power)`. HH/HV radar imagery is scientific backscatter, not a natural-colour photo. Cloud penetration does not guarantee all-weather accuracy. Do not animate radar as seeing through everything or label an arbitrary bright/dark patch a confirmed flood.

## Exact asset and source locations

All paths below exist at handoff unless explicitly described as proposed outputs.

| Asset / source | Absolute path |
| --- | --- |
| Frontend source | `D:/Hackathon/NASA/Sarpulse/web/src` |
| Primary styles/tokens | `D:/Hackathon/NASA/Sarpulse/web/src/styles.css` |
| Workspace / 3D styles | `D:/Hackathon/NASA/Sarpulse/web/src/workspace.css`, `D:/Hackathon/NASA/Sarpulse/web/src/orbital.css` |
| App routes and scientific loader | `D:/Hackathon/NASA/Sarpulse/web/src/App.tsx`, `D:/Hackathon/NASA/Sarpulse/web/src/lib/science.ts` |
| 3D scene and radar effects | `D:/Hackathon/NASA/Sarpulse/web/src/components/scene/OrbitalScene.tsx`, `D:/Hackathon/NASA/Sarpulse/web/src/components/scene/SarEffects.tsx` |
| Map implementation | `D:/Hackathon/NASA/Sarpulse/web/src/components/map/GeoWorkspace.tsx` |
| Passport / scientific panels | `D:/Hackathon/NASA/Sarpulse/web/src/components/ChangePassport.tsx`, `D:/Hackathon/NASA/Sarpulse/web/src/components/ScientificEvidence.tsx` |
| Explorer / lab / story | `D:/Hackathon/NASA/Sarpulse/web/src/pages/Explorer.tsx`, `ScienceLab.tsx`, `Story.tsx` in that same `pages` folder |
| API | `D:/Hackathon/NASA/Sarpulse/api` |
| Scientific code | `D:/Hackathon/NASA/Sarpulse/science/ingestion`, `D:/Hackathon/NASA/Sarpulse/science/analysis` |
| Orchestration / contracts | `D:/Hackathon/NASA/Sarpulse/platform`, `D:/Hackathon/NASA/Sarpulse/contracts` |
| Genuine public scientific index | `D:/Hackathon/NASA/Sarpulse/web/public/data/sites.json` |
| Assam published scientific package | `D:/Hackathon/NASA/Sarpulse/web/public/data/sites/brahmaputra-majuli` |
| Netherlands published scientific package | `D:/Hackathon/NASA/Sarpulse/web/public/data/sites/biesbosch-netherlands` |
| Full local Assam processing | `D:/Hackathon/NASA/Sarpulse/data/processed/majuli-release-001` |
| Full local Netherlands processing | `D:/Hackathon/NASA/Sarpulse/data/processed/biesbosch-release-001` |
| Netherlands optical-reference processing | `D:/Hackathon/NASA/Sarpulse/data/processed/biesbosch-reference` |
| Editable web demo | `D:/Hackathon/NASA/Sarpulse/web/public/demo/index.html` |
| Existing demo PDF | `D:/Hackathon/NASA/Sarpulse/web/public/demo/sarpulse-demo.pdf` |
| Seven existing slide PNGs | `D:/Hackathon/NASA/Sarpulse/build/demo-slides/slide-1.png` through `slide-7.png` |
| Existing explorer screenshot | `D:/Hackathon/NASA/Sarpulse/build/release-check/explorer.png` |
| Actual browser test/capture examples | `D:/Hackathon/NASA/Sarpulse/scripts/smoke_release.mjs`, `D:/Hackathon/NASA/Sarpulse/web/tests/e2e/connected.spec.ts` |
| Slide capture utility | `D:/Hackathon/NASA/Sarpulse/scripts/render_demo.mjs` |
| Earth GLB | `D:/Hackathon/NASA/Sarpulse/web/public/models/earth.glb` |
| SMAP spacecraft GLB | `D:/Hackathon/NASA/Sarpulse/web/public/models/smap.glb` |
| Studio HDR | `D:/Hackathon/NASA/Sarpulse/web/public/environment/studio.hdr` |
| Font packages | `D:/Hackathon/NASA/Sarpulse/web/node_modules/@fontsource` — requires the local npm install |

Within either scientific site folder, use `analysis.json`, `scenes.json`, `provenance.json`, `layers.json`, `samples.json`, `time_series.json`, `time_series.csv`, `change_class.tif`, `delta_hh_db.tif`, `evidence/` and `water/`. The Netherlands also has `validation.json`, `source-provenance.json`, `reference-provenance.json`.

Real ready-to-use Assam imagery is in `D:/Hackathon/NASA/Sarpulse/web/public/data/sites/brahmaputra-majuli/web/`:

- `hh_db_2026-07-22.png`, `hh_db_2026-10-14.png`
- `hv_db_2026-07-22.png`, `hv_db_2026-10-14.png`
- `water_2026-07-22.png`, `water_2026-10-14.png`
- `delta_hh_db.png`, `change_class.png`, `water_gained.png`, `water_lost.png`, `ambiguous.png`.

Equivalent Netherlands images are in `D:/Hackathon/NASA/Sarpulse/web/public/data/sites/biesbosch-netherlands/web/`, with dates `2026-07-19` and `2026-10-11`. Use `layers.json` for coordinates, ranges and interpretation. Preserve map orientation, bounds, layer registration, date labels and legend. Geographic transformations must be accurate. A rendered decorative globe is not the measured study-area raster. Existing PNGs may be small; use source GeoTIFFs or a native-resolution UI capture for detailed shots rather than inventing extra resolution.

**Important model identity:** `smap.glb` is NASA **SMAP**, not NISAR. Never relabel it as NISAR, use it as evidence of NISAR hardware, or imply its trajectory represents the real acquisitions. Prefer the Earth asset with an explicitly illustrative sensing visualization. If exact NISAR hardware is necessary, obtain a correctly attributed verified model/reference; do not improvise one and call it authentic. The Earth model is illustrative visual context, not current imagery. Follow original asset notices in `web/public/models/ATTRIBUTION.md`. Poly Haven Studio Small 03 is CC0. NASA/VTAD and NASA/JPL-Caltech credits are recorded there.

## Capture the real application

For repeatable clean captures, start locally from PowerShell:

```powershell
Set-Location D:/Hackathon/NASA/Sarpulse
docker compose up --build
# Full UI/API/data: http://127.0.0.1:8000
```

Alternatively use the static viewer:

```powershell
Set-Location D:/Hackathon/NASA/Sarpulse
npm --prefix web ci
npm --prefix web run dev
# Use the actual Vite URL printed by this command.
```

Actual routes are `/#home`, `/#explore`, `/#science`, `/#story`; demo is `/demo/`. Wait until the scientific investigation and images finish loading. Choose Brahmaputra–Majuli, verify the NASA NISAR observations banner, set the correct comparison dates, compare HH/HV, reveal the fixed-pair change overlay, click a valid map location, then show its Change Passport and the Science Lab. Changing arbitrary dates does not recompute a new change pair. Use the real controls; camera crops, perspective treatments and typography may enhance the recording without fabricating interface behaviour or data.

Static passports disclose nearest-sample support; full API passports read a raster pixel. Keep the distinction if describing point precision. Do not use the synthetic fallback as a real observation. `api/fixtures`, `web/src/data/demo.ts` and ingestion/analysis test fixtures are software-test material. Avoid terminal windows, credential dialogs, local usernames and the repository's raw/download folders in screen recordings.

## Creative direction

Use the app's actual palette as a starting point: black `#000000`, panel `#0a0c10`, line `#1c1f25`, pale text `#edf3f7`, muted `#a8b9c9`, blue/cyan `#00a1ff`, magenta `#e989c5`, amber `#e6bb6f`. Manrope is the established interface font; other installed font packages include Barlow Condensed and IBM Plex Sans. Essential labels must remain readable at delivery size. Preserve the application's gain/loss/uncertainty legend rather than inventing conflicting colours.

Suggested visual grammar: a physically plausible Earth limb with atmospheric falloff and controlled sunlight; a deliberate orbital camera move; an illustrative radar sweep transformed into the real georeferenced river layer; a close, readable comparison wipe; an evidence line resolving into the actual passport; a restrained title/end mark. Use geographic continuity and repeated radar/river shapes to motivate transitions.

Realism should come from coherent scale, camera/lens perspective, texture, physically plausible light, occlusion, depth and motion. Render genuine geometry in Blender when that is what the shot needs. Keep the data and UI crisp. Avoid excessive bloom, arbitrary shallow focus over essential text, random particles, relentless camera movement and generic floating-card montages. Allow a readable hold and an intentional cut. The product evidence should occupy a substantial part of the film, not flash past after a long space intro.

Sound should support the story: restrained atmospheric space/river texture, a deliberate musical build, a few motivated scan/interface cues, and an intelligible human voice if available. Source/licence music and sound; preserve attribution. Do not synthesize speech or use paid music/generation assuming entitlement. A well-mixed local/owned soundtrack is sufficient. Do not assume the video tools currently provide working free TTS.

## Format and suggested 30-second story

The supplied NASA guide permits a video of **30 seconds or less**, or up to seven slides including title/introduction. The seven-slide alternative already exists. Default this film to a compelling **29–30-second, English, 16:9, 1920×1080, 30 fps** cut. Target 29 seconds for small encoding margin; verify the actual container and audio duration remain at or below 30 seconds. These are project defaults, not a claim that NASA requires a particular codec or frame rate. A separate longer cinematic showcase is optional only if useful or subsequently requested; never replace the compliant cut with an overlength demo.

Suggested beats, adjustable to actual footage and delivery:

| Time | Story / visual purpose |
| --- | --- |
| 0–3 s | Team StarFire / Dancing with the SARs; cinematic Earth reveal and a clear question about hidden water change. Establish the project quickly. |
| 3–8 s | Title/tagline; illustrative radar sensing transitions into a geographically honest Assam location. |
| 8–14 s | Real dated July/October HH images and comparison; gain/loss overlay with a concise candidate-change qualifier. |
| 14–21 s | Actual user click and Change Passport: observation dates, measured channels, method and limitations become legible. |
| 21–26 s | Science Lab / reference evidence. A short honest line: “Candidate changes. Uncertainty visible.” Avoid an invented performance claim. |
| 26–29 s | SARPulse, Team StarFire, tagline and verified URL. Give the end card a readable hold. |

Possible narration, a draft to time and revise rather than force into the cut:

> We're Team StarFire. Water landscapes change, even when clouds hide the view. SARPulse turns NASA–ISRO NISAR radar observations into an investigation. Compare real acquisitions. Explore candidate water changes. Open a Change Passport to inspect measurements, sources and uncertainty. Our Science Lab makes limitations visible, so a changed signal isn't mistaken for proof of flooding. SARPulse. Earth's changes. Revealed by radar.

Do not rush an overlong recording to meet duration; edit words or allocate holds based on measured speech. If using another spoken language, provide accurate English subtitles under the supplied guide. Include the team/challenge clearly; team member names can appear in the accompanying description/credits and deck instead of unreadably squeezing six names into a fast shot.

Team credits: **Shoaib** — platform/integration; **Veer** — satellite data/preprocessing; **Naveen** — detection/evaluation; **Nidhi** — frontend/maps; **Shridhar** — API/evidence; **Hansika** — UI/UX/story/presentation.

## Production organisation and practical execution

Use a new project folder, proposed (not yet created): `D:/VideoEditing/SARPulse`. Preserve older work. Suggested structure: `brief/`, `assets/source/`, `assets/derived/`, `code/hyperframes/`, `blender/`, `resolve/`, `renders/`, `audio/`, `captions/`, `qc/`, `deliveries/v01/`. Keep a shot manifest with source paths, timing, factual claims and credits. Do not move original repo assets out of the project. Copy assets into the HyperFrames served project root; the verified lint/render path disallows source traversal outside that root.

1. Read this brief and current studio instructions. Inspect real UI, data images and models; check the needed render/editor connections without auto-launching unrelated apps.
2. Create a timed shot plan and concise script from the actual scope. Capture clean evidence plates early. Do not spend the entire schedule on a space intro.
3. Prove one representative Blender/HyperFrames shot and its Resolve handoff. Use deterministic timing and fonts, verified local assets and fixed seeded randomness where needed. Check current CLI help instead of inventing render flags.
4. Author real 3D shots, graphic/evidence sequences and captions. Preserve `.blend`, HyperFrames HTML/JS/assets and any Fusion/AE native sources. Use proxies/previews to iterate efficiently.
5. Assemble, colour, mix and finish in Resolve; save a versioned native project and export a `.drp` backup. Verify that the export/import actually worked. An XML file alone is not a native Resolve project.
6. Deliver a compatible H.264 MP4 with AAC when audio is present, plus optional higher-quality master, English captions, poster frame, credits/asset manifest and QC report. Keep alpha elements as a verified alpha codec/image sequence, not an alleged transparent H.264 MP4. The alpha audit verified ProRes 4444 `yuva444p12le` for specific HyperFrames title exports; retest receiving-editor interpretation.
7. Inspect the actual exported film, fix material defects and deliver working files. Do not claim a finished film from code or a render command alone.

The Resolve timestamp audit found a real first-frame black insertion problem for some derivatives. Check actual stream start times, frame counts and boundary frames; normalize only affected derivatives and retain originals. Review difficult transitions in motion, not solely contact sheets. Recheck actual format, colour tags, dimensions, fps, duration, start time, complete decoding, audio intelligibility/sync, loudness/clipping, website text, dates, units, geographic orientation and phone-size readability.

## Disclosure, branding, rights and submission boundaries

The supplied 2026 guide requires visible SI-generation indicators for SI-generated images/video and descriptive/metadata acknowledgement for SI-generated audio; code/data assistance has descriptive and metadata disclosure. Apply those requirements to the actual media used, document the scope and centrally update project disclosure. Do not add boilerplate to every source file. Do not invent a claim that externally sourced NASA measurements are SI-generated observations. Verify how the guide applies to the final assembled film and its authored/generated elements.

Generated content must not use, contain or modify NASA branding/design elements contrary to the supplied guide. Use original SARPulse/StarFire identity and plain factual mission references. Do not generate NASA logos, seals, flags, fake mission identifiers or an endorsement badge. Inspect existing models/screens for branding before incorporating them in generated composites, and preserve source-specific asset permissions. No images, voice, video or likeness of under-18 persons may appear in the demo/final project under the supplied guide. Keep Earthdata credentials, hosting tokens and raw private material out of assets, recordings and published logs.

The supplied submission deadline was November 15, 2026 at 23:59 in the applicable event time zone. This work is continuing November 16. Do not claim this film or release was completed before that deadline, or that NASA submission/award eligibility is verified. The task is production and delivery, not submission of a form or acceptance of legal terms.

## Definition of finished

A polished, inspected, cinematic film with meaningful 3D motion and a real product demonstration; true acquisition dates/data; correct candidate-change language; readable evidence and end card; verified URL; appropriate credits/disclosure; compliant short-cut duration; editable native/code sources; a QC record; and final paths clearly handed back to Shoaib. Distinguish completed renders from plans and disclose any remaining limitations plainly.
