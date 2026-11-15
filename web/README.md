# SARPulse frontend

Hansika and Nidhi's React/Vite/TypeScript application. This folder is independent of backend and science implementations. No teammate branches are required.

```sh
cd web
npm ci
npm run dev
```

Open the URL printed by Vite (normally http://127.0.0.1:5173). Hash navigation supports Overview, Explore, Science Lab and Guided story without server routing configuration.

```sh
npm run typecheck
npm test
npm run build
npm run test:e2e
```

After building, run `SARPULSE_E2E_PREVIEW=1 npm run test:e2e` to check the same scenarios against the static production files. Run `npm run format` for consistent source formatting.

Browser checks use locally installed Google Chrome through Playwright. Install Chrome separately if absent; no browser is downloaded by this project. Unit tests need no browser. `npm run preview` serves the production build.

## Features and ownership

- Hansika: React Three Fiber/Drei landing with loaded NASA spacecraft/Earth GLBs, five pinned scroll chapters, HDR lighting, Lenis scrolling, drag/keyboard rotation and pause/reset controls; responsive navigation and self-hosted fonts; Science Lab, modular ECharts chart with table alternative, provenance and local exports; five-chapter GSAP ScrollTrigger map story with reduced-motion support.
- Nidhi: shared MapLibre `GeoWorkspace`, synchronized GL Compare plus keyboard divider, candidate extent, GeoJSON display and inspection, fixed classification views, before/after selectors, discrete timeline and finite playback, opacity, alternative colors, contextual OSM toggle, raster tile consumption and WebGL/error states.

`src/types/frontend.ts` defines **local view models**, not a proposed shared backend contract. `GeoWorkspaceProps` is the single map integration interface used by Explorer and the map-based Story Mode. The landing's separate 3D presentation does not duplicate mapping. The map renderer consumes supplied data; it neither classifies pixels nor fetches scene catalogs nor creates tiles. Classification geometry is fixed to the package, so switching dates does not recompute change classes.

## Demo and real-data boundary

The included fixture is **SYNTHETIC/DEMO — NOT NASA OBSERVATIONS**. The rectangles are schematic UI test cells placed in a candidate geographic region, not actual river/water geometry. Illustrative signal values have no claimed polarization. Source fields and scientific statistics are null. Geographic coordinates are EPSG:4326; this is not a claim about a source raster CRS. There are no invented scene IDs, acquisitions, processing releases, areas or accuracy metrics.

Open **Science Lab → Data package** to export the complete example shape. **Open data package** accepts a local JSON file (maximum 5 MB), validates its view-model fields and replaces the fixture across all views. Invalid imports leave the current package untouched. Nothing is uploaded or sent to a backend. Packages are held in memory and clear on reload.

For `status: "provided"`, each observation needs actual acquisition UTC, product ID, HTTPS source link, polarization, processing release, maturity, source CRS and positive posted spacing. This validates structure, not scientific validity. Preserve the supplied validation status and limitations; the UI labels it as supplied, not independently verified. Actual shared contracts should be translated into this view model once agreed by the team; no existing shared contract is changed here.

Optional `observation.raster` accepts `tiles` (XYZ templates containing `{z}`, `{x}`, `{y}`), `attribution`, `minDb` and `maxDb`. An observation can also provide `channels: [{ polarization, raster }]`; the explorer offers only supplied channels and never substitutes a different polarization when a selected channel is missing on one date. These can be templates from an **existing** TiTiler service serving a COG, or static pre-rendered tiles. The frontend does not implement TiTiler, download HDF5, preprocess SAR, or sample scientific values from rendered colors. Tile services must support CORS. HTTPS, root-relative local tiles and HTTP loopback development services are supported. Do not put secrets in packages. Keep pre-rendered styles and dB display ranges consistent with their source metadata; this viewer does not recolor tiles or change a channel it was not supplied.

The optional OpenStreetMap basemap is geographic context, not NISAR data or satellite imagery. It requires internet and retains attribution. The default local grid and geometry do not require network access after app assets load. Google Chrome/WebGL is needed for full mapping; a cell-list inspection fallback and the rest of the application remain available without it.

## Exports

- Visible GeoJSON includes package status and provenance; it is the current overlay subset (the after side in comparison), not new scientific output.
- CSV contains supplied/illustrative signal rows, units, source metadata and provenance; null scientific metadata remains blank.
- JSON exports the complete input view model, unchanged, for review/replacement.

## Dependency choices

One mapping renderer (MapLibre), one comparison plugin, one animation library (GSAP), one modular chart library (ECharts). React Three Fiber and Drei manage the requested Three.js presentation: GLB loading, normalization, HDR environment, drag interaction and floating motion. GSAP supplies the scroll choreography; Lenis smooths wheel scrolling only while the landing route is mounted. No globe.gl, deck.gl or competing animation engine is added. The local shadcn-style Button uses Radix Slot, cva and Tailwind utilities. Fonts, GLBs and the HDR environment are self-hosted. No server, geoprocessing or ML dependency is installed.

The spacecraft is NASA's authored **SMAP model, explicitly labeled as SMAP, not NISAR or a live orbit**. The NASA Earth model is illustrative visual context, not SAR observations or acquisition coverage. Source credits and reuse guidance are in `public/models/ATTRIBUTION.md`; the environment is Poly Haven CC0. `scripts/optimize-model.mjs` repacks these graphical assets using glTF Transform and WebP textures, retaining the source geometry and material assignments. The local assets total approximately 6.5 MB. No spacecraft geometry or globe texture is manually generated.

The landing follows the requested EnduroSat reference's left-aligned oversized type, persistent black WebGL stage, pinned text transitions, changing model poses and bottom segmented navigation, using SARPulse content and credited assets. Manrope supplies an openly licensed font substitute. The 3D module loads separately, caps rendering resolution, pauses offscreen/hidden, respects reduced-motion preferences and allows an explicit user override. The canvas unmounts when leaving the route; Drei caches loaded GLBs for repeat visits. Lenis is removed before the geographic workspace opens, preserving map wheel/touch gestures. Text and investigation links remain available when WebGL or model loading fails.

## Remaining external inputs

Verified NISAR acquisitions, actual polarizations and raster URLs, confirmed AOI, comparable processing metadata, validated classifications/area summaries, chart summaries tied to a real sample region, scientific evidence and final team integration. Actual remote COG/TiTiler rendering cannot be validated against science data until such inputs exist. Backend and scientific work remain outside this frontend.

See `../design/FRONTEND_PLAN.md` for the independent ownership plans and event/reference checks.

See `../design/FRONTEND_HANDOFF.md` for the complete file inventory, verification results and remaining real-data frontend checks.

See `../design/ORBITAL_EXPERIENCE.md` for the user-requested EnduroSat-inspired 3D redesign and its verification notes.
