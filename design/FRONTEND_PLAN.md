# Frontend implementation plan — Hansika and Nidhi

The initial landing design and dependency choices below were subsequently revised at the user's explicit request for an EnduroSat-style 3D experience. See [Orbital experience revision](ORBITAL_EXPERIENCE.md) for the current landing direction; frontend ownership and scientific integrity boundaries remain the same.

Work is isolated to `web/` and `design/` on `feat/hansika-nidhi-frontend`. No teammate branches, backend services, science code, or shared contracts are changed.

## Inspection

The original repository contains documentation and empty module placeholders. There is no existing application, dependency manifest, UI, API implementation, or finalized shared contract. Read README, TEAM, WORKFLOW, DATA_INTEGRITY, PROJECT_PLAN, CONTRIBUTING and the supplied November 7 master plan before implementation.

## Hansika's independent plan

1. Establish typography, tokens, responsive shell, accessible buttons and a coherent navigation model.
2. Build the landing experience around the candidate floodplain and clear data readiness.
3. Build Science Lab with charts, metadata, limitations, scattering explanation and local exports.
4. Build a five-step guided story using Nidhi's shared map, GSAP ScrollTrigger and explicit navigation.
5. Check keyboard navigation, reduced motion, mobile layouts and presentation quality.

## Nidhi's independent plan

1. Define a frontend-only `StudyPackage` view model and `GeoWorkspaceProps`; do not dictate backend schemas.
2. Implement one MapLibre renderer for the landing preview, explorer and story.
3. Add candidate-region navigation, fixture GeoJSON, geographic inspection, legends, opacity and accessible colors.
4. Add synchronized MapLibre Compare, before/after choices, discrete observation timeline and playback.
5. Consume supplied raster XYZ URLs (including existing TiTiler COG output), preserve metadata, and handle unavailable raster, network and WebGL states honestly.

## Design plan and review

Palette: deep navy `#0b1525`, panel navy `#122238`, radar cyan `#69dce8`, change magenta `#e989c5`, caution amber `#e6bb6f`, pale text `#edf3f7`. Typography: Barlow Condensed for headlines, IBM Plex Sans for interface and prose, self-hosted. The visual anchor is the map, not decorative space imagery.

Layout: a horizontal navigation bar above a left-aligned two-column landing; explorer uses a narrow control rail, large map and bottom timeline; story pairs a sticky shared map with five sequential chapters. On mobile panels stack and the map retains a usable height. Borders distinguish controls and evidence sections; panels have restrained rounding. No invented statistic cards.

Review against brief: a generic animated globe would duplicate mapping and distract from the investigation. Omit Three.js, globe.gl, deck.gl, Lenis and Motion until a demonstrated need exists. Use GSAP only for story progression; native scrolling preserves map gestures. Tailwind plus a local shadcn-style Button provide the small design system; modular ECharts supplies actual interactive charts.

## Rules and reference checks (November 15, 2026)

Official organizer guidance in https://github.com/nasa/spaceapps/discussions/1827 and /1916 confirms project work begins November 14 at 09:00 local event time, with submission closing November 15 at 23:59. NASA's https://science.nasa.gov/universe/nasa-welcomes-all-ages-experience-levels-for-space-apps-challenge/ also confirms November 14–15. Current client date is within the build window. Direct fetches of the 2026 challenge, legal terms and submission-guide pages returned 502; full current terms could not be read. Team must verify local instructions and submission/disclosure requirements separately. No submission or claim of eligibility is made here.

Approved library reviewed selectively: NASA Worldview (comparison/timeline); Sentinel Hub EO Browser user guide (layer discovery, date selection); Copernicus Browser documentation (visualize/compare); ArcGIS StoryMaps (map/narrative pairing); GSAP ScrollTrigger documentation. Dynamic inspiration homepages expose limited text. These inform interaction patterns; no source code or visual assets are copied.

## Verification and handoff

Build and typecheck, test fixture visibility and package validation, then browser-test timeline, comparison, selection, export, story, reduced motion and mobile. Real acquisitions, supplied raster endpoints, validated area summaries, scientific metrics and final integration remain external inputs. Do not synthesize substitutes for them.
