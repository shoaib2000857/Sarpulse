# Frontend handoff — Hansika and Nidhi

The initial verification and design record below predates the user's requested 3D landing revision. The current landing uses React Three Fiber/Drei with authored NASA SMAP and Earth GLBs, an HDR environment, five pinned GSAP scroll chapters and landing-only Lenis smoothing. SMAP is labeled as a presentation reference, not NISAR. See [Orbital experience revision](ORBITAL_EXPERIENCE.md) for current files, behavior and verification. MapLibre remains the geographic renderer in Explorer and map-based Story Mode; it is no longer embedded in the landing hero.

Implemented locally on `feat/hansika-nidhi-frontend`. All new source and documentation are confined to `web/` and `design/`. No backend, science, shared platform contract, teammate branch, CI or protected-main changes were made. Changes are uncommitted for review; nothing was merged, pushed, submitted or deployed.

## Completed experience

| Owner | Delivered frontend features |
| --- | --- |
| Hansika | Navy/cyan/magenta/amber visual identity; self-hosted typography; reusable shadcn-style Button and visual tokens; landing page; responsive application shell and mobile navigation; Science Lab; modular ECharts signal chart, table alternative and metadata passport; scattering explanations, provenance and limitations; five-chapter GSAP ScrollTrigger Story Mode; explicit chapter navigation, reduced motion and keyboard focus. |
| Nidhi | One shared MapLibre geographic workspace across landing, explorer and story; pan, zoom and extent reset; local EPSG:4326 GeoJSON and geographic inspection; synchronized MapLibre Compare with drag and keyboard divider; before/after selectors and finite timeline playback; fixed package change/gain/loss overlays; opacity, footprint and optional attributed OpenStreetMap context; alternate colors plus class symbols; supplied raster XYZ/TiTiler output consumption and optional supplied-channel selection; missing-raster, resource-error and WebGL fallback states. |
| Shared integration | Frontend-only typed view models; validated local JSON package import; replaceable fixture; CSV, visible GeoJSON and full JSON downloads with provenance; no backend or geoprocessing required. |

The fixture is **SYNTHETIC/DEMO — NOT NASA OBSERVATIONS** throughout the application and exports. It has schematic test rectangles and illustrative dB chart values. Acquisition IDs, actual timestamps, polarization measurements, processing releases, area estimates and scientific performance metrics are not fabricated. Null scientific values remain unavailable. Supplied packages are labeled as supplied, not scientifically verified by the viewer.

## Files added

| Files | Purpose |
| --- | --- |
| `design/FRONTEND_PLAN.md`, `design/FRONTEND_HANDOFF.md` | Initial inspection, separate plans, reference/rule checks and handoff. |
| `web/package.json`, `web/package-lock.json`, `web/tsconfig.json`, `web/vite.config.ts`, `web/components.json`, `web/.gitignore`, `web/index.html` | Reproducible Vite/TypeScript/Tailwind/shadcn-compatible setup; local MapLibre worker packaging. |
| `web/src/main.tsx`, `web/src/App.tsx`, `web/src/styles.css` | Entry, shared state, navigation, imports, page boundaries and responsive design system. |
| `web/src/components/ui/button.tsx`, `web/src/lib/utils.ts` | Reusable accessible button and styling utilities. |
| `web/src/pages/Landing.tsx`, `web/src/pages/Explorer.tsx`, `web/src/pages/ScienceLab.tsx`, `web/src/pages/Story.tsx` | Four working application experiences. |
| `web/src/components/map/GeoWorkspace.tsx`, `web/src/types/maplibre-compare.d.ts` | Single shared map renderer, comparison and typed comparison-plugin boundary. |
| `web/src/components/charts/SignalChart.tsx` | Modular ECharts, UTC time axis for supplied timestamps, illustrative categories otherwise; missing values stay missing. |
| `web/src/types/frontend.ts`, `web/src/data/demo.ts`, `web/src/lib/study.ts`, `web/src/lib/validate-package.ts` | Frontend view model, synthetic fixture, layer/export helpers, structural import validation. |
| `web/tests/study.test.ts`, `web/tests/e2e/frontend.spec.ts`, `web/vitest.config.ts`, `web/playwright.config.ts` | Data integrity and real Chrome interaction checks, including production preview mode. |
| `web/README.md` | Setup, usage, raster/channel adapter, fixture boundary, exports and remaining inputs. |

Generated `dist/`, `test-results/`, installed packages and TypeScript build state are ignored. Browser screenshots in `web/test-results/` were visually reviewed for desktop landing/explorer/Science Lab/Story Mode and mobile explorer.

## Verification completed

Run from `web/`:

| Command | Outcome |
| --- | --- |
| `npm run typecheck` | Passed strict TypeScript checks. |
| `npm test` | 17 tests passed: fixture honesty, missing metadata, layer filtering, CSV provenance/escaping, malformed geometry, unknown references, unsafe links, invalid dates and unsupported package data. |
| `npm run build` | Passed. Build includes the separately packaged, same-origin MapLibre worker. |
| `npm run test:e2e` | 7 Chrome scenarios passed in development: map/comparison/export/playback; Science Lab; valid/invalid imports; Story Mode; mobile; synthetic raster tile integration; WebGL fallback. |
| `SARPULSE_E2E_PREVIEW=1 npm run test:e2e` | All 7 scenarios passed against the final production build (32.5 seconds on this machine). |
| Dependency audit during final install | 0 vulnerabilities reported. Initial MapLibre and Vitest advisories were resolved with patched releases. |

Build emits a size advisory for MapLibre's approximately 1.08 MB minified main chunk (about 296 kB gzip), plus its separate worker. Pages, Story Mode and charts are split into separate lazy-loaded chunks. No heavy globe, additional renderer, competing animation engine, server or ML library is installed.

Browser checks used installed Google Chrome at desktop 1440×1000 and mobile 390×844, with a reduced-motion story path. The tile integration check uses a synthetic PNG response solely to verify renderer wiring; it is not a test against an actual NISAR COG or an operational TiTiler service.

## Remaining frontend checks when actual outputs exist

1. Adapt an agreed real data export into the local view model; verify actual observation ordering, channel availability, source CRS, processing lineage and dates are faithfully presented.
2. Inspect real pre-rendered tile styles, CORS, display ranges and masks. Validate the comparison and legends against the supplied raster outputs.
3. Check real area/series summaries and citations in Science Lab; replace the illustrative narrative with a source-supported site-specific story after scientific review.
4. Recheck on the eventual deployment origin and target devices. Public hosting and final integration were not requested here.

These checks depend on external inputs; they do not authorize frontend work on data acquisition, algorithms, backend services or scientific validation. Pixel sampling, difference calculation, water classification and area computation are deliberately not implemented. Change-class overlays remain the supplied fixed package, not recomputed for arbitrary dates.

## Run locally

```sh
cd web
npm ci
npm run dev
```

Open the printed local Vite URL. Use **Open data package** for a local JSON file or export the example shape from **Science Lab → Data package**. Imported packages remain in memory only; nothing is uploaded.
