# Orbital experience revision

The user requested the layout and motion of https://www.endurosat.com/space-service/?utm_source=lenis, with SARPulse content and assets. Their clarification was: **“Same layout and motion, SARPulse assets.”** The initial manually constructed spacecraft revision was replaced with authored GLB assets and React Three Fiber/Drei. Existing Explorer, Science Lab and map-based Guided Story remain functional and within Hansika/Nidhi's frontend ownership.

## Reference and design

The reference's public HTML, stylesheet and script were inspected for layout and interaction structure. Its oversized title is left aligned at approximately 12% of the viewport, with a blue pretitle. Challenge and solution sections use smaller sentence-style headings, followed by a two-step choice and an Earth finale. Sections are pinned overlays sharing a persistent WebGL stage, with bottom-centered segmented navigation. SARPulse follows this composition, black/white/electric-blue palette and scroll-driven subject transforms. It uses five SARPulse investigation stages rather than the reference's commercial service copy.

The browser connection was unavailable, so a live side-by-side visual match was not performed. No proprietary model, font, branded image or source implementation is redistributed. Manrope is an openly licensed substitute for the reference's proprietary typeface. The reference inspection files were kept outside the repository.

## Libraries and assets

- React Three Fiber owns the Three.js renderer and responsive canvas.
- Drei loads and normalizes authored GLBs (`useGLTF`, `Center`, `Resize`), supplies HDR lighting (`Environment`), drag interaction (`PresentationControls`), optional ambient movement (`Float`) and loading progress.
- GSAP drives five model poses and pinned text transitions through ScrollTrigger. Lenis smooths desktop wheel scrolling while the landing route is mounted. No second animation engine is added.
- NASA VTAD's **SMAP** spacecraft model is visibly labeled as SMAP, not NISAR, a live orbit or an observation source. NASA/JPL-Caltech's Earth model supplies illustrative visual context. Poly Haven's Studio Small 03 supplies CC0 HDR lighting.
- All assets are self-hosted. glTF Transform removes redundant data and resizes/encodes embedded textures as WebP, retaining source geometry and material assignments. Spacecraft, Earth and HDR total approximately 6.5 MB. Source links, credits, reuse guidance and font licensing are recorded in `web/public/models/ATTRIBUTION.md`.

No manually generated spacecraft parts or globe textures remain. No backend, data acquisition, SAR processing, scientific classification, shared contracts or other teammates' modules were changed.

## Current files and behavior

| Files | Purpose |
| --- | --- |
| `web/src/pages/Landing.tsx` | One persistent stage with five pinned sections: Introduction, Challenge, Solution, Two steps and Investigation; working Explorer/Science/Story links; chapter navigation; rotation, reset and pause controls. |
| `web/src/components/scene/OrbitalScene.tsx` | Fiber canvas, Drei asset loading, environment and controls; GSAP pose choreography; responsive framing; visibility and reduced-motion handling; asset/WebGL error boundary. |
| `web/src/orbital.css` | Reference-aligned proportions, pinned overlays, segmented navigation and mobile layout. |
| `web/src/App.tsx` | Landing-specific application shell and preserved data-status banner. |
| `web/public/models/`, `web/public/environment/` | Credited NASA GLBs and Poly Haven HDR. |
| `web/scripts/optimize-model.mjs` | Reproducible graphical asset packing with glTF Transform and Sharp. |
| `web/tests/e2e/orbital.spec.ts` | Actual WebGL/model rendering, keyboard/drag pixel changes, settled scroll navigation, two-step destinations, route cleanup, mobile/reduced motion and WebGL failure. |
| `web/tests/e2e/frontend.spec.ts`, `web/playwright.config.ts` | Existing frontend regressions and configurable production-test port. |

Canvas resolution is capped; continuous motion pauses while hidden or offscreen. The canvas unmounts when leaving the route, and Drei caches GLBs for repeat visits. Lenis and ScrollTrigger are removed before entering the interactive map. Reduced motion disables ambient movement and smooth wheel scrolling. Inactive chapter content is inert and hidden from accessibility APIs. Chapter buttons provide alternatives to scrolling; rotation and reset have keyboard-accessible controls. Text and destinations remain available if WebGL fails.

## Verification

Run from `web/`:

| Command/check | Result |
| --- | --- |
| `npm run build` | Passed, including strict TypeScript compilation. Final production build includes the landscape refinement. |
| `npm test` | All 17 data-integrity tests passed. |
| `npm run test:e2e` | All 11 Chrome scenarios passed: original frontend regressions and four orbital scenarios. |
| `SARPULSE_E2E_PORT=5174 SARPULSE_E2E_PREVIEW=1 npm run test:e2e -- --grep orbital` | All four orbital scenarios passed against production files. |
| `SARPULSE_E2E_PORT=5174 SARPULSE_E2E_PREVIEW=1 npm run test:e2e -- --grep 'orbital experience honors'` | Passed after the final short-screen refinement, covering reduced motion, 390×844, width 320 and 844×390 landscape. |
| Dependency installation audit | Zero reported vulnerabilities; unused direct meshoptimizer dependency removed. |
| Running development preview | `http://127.0.0.1:5173/` returned HTTP 200 and remains running. Production tests used a separate temporary server. |

Desktop, portrait mobile and landscape screenshots were visually reviewed. Browser tests use installed Chrome with software WebGL; physical-device performance has not been measured. The lazy-loaded 3D and MapLibre chunks each retain a Vite size advisory (approximately 1.09 MB / 298 kB gzip and 1.08 MB / 296 kB gzip respectively). No frame-rate claim is made. The GLBs and environment add approximately 6.5 MB of local presentation assets.

Earlier results in the initial frontend handoff concern the original frontend and do not describe this renderer.

The scientific fixture boundary remains **SYNTHETIC/DEMO — NOT NASA OBSERVATIONS**. Graphical NASA models do not turn the fixture into scientific data. Verified observations, classifications and raster services remain external inputs for later frontend checks. Work is local and uncommitted on `feat/hansika-nidhi-frontend`.

## Reference-match revision (libraries, not hand-built effects)

The reference was captured in headless Chrome and compared frame by frame. Composition now follows it: hero with a rising planet limb, challenge, solution, a **Two steps** frame (centred globe, no spacecraft, giant COMPARE / INSPECT at the screen edges), and a lit-Earth finale. Colours follow the earlier black / real-Earth scheme at the user's request.

- **three-globe**: atmosphere halo, orbit-streak arcs, and the echo-ripple rings of the SAR footprint. Its dotted-continent mode (reference look) is kept behind `DOTTED_LAND` in `SarEffects.tsx`.
- **world-atlas + topojson-client** (Natural Earth, public domain): land shapes for that optional dotted mode. Antarctica and North Korea's 110 m polygon are skipped because h3 rejects them; decorative only.
- **@react-three/drei `Stars`**, renderer ACES tone mapping (a Bloom pass was trialled and removed for cost).
- `toHologram()` (blue wireframe satellite) remains available but is off in the current colour scheme.
- The SAR beam is an illustrative graphic, not orbit or swath data.
