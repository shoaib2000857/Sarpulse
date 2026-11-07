# StarFire — six-person ownership

This is a collaboration map, **not a hierarchy**. Everyone is expected to help each other and contribute to research, testing and integration.

| Member | Main responsibility | Expected module |
| --- | --- | --- |
| **Shoaib** | Technical architecture, shared contracts, platform orchestration, layer delivery, exports, CI/CD, integration, PR review and merges | `platform/`, `contracts/`, `.github/` |
| **Veer** | Actual NISAR data discovery, product inspection, polarization, calibration/metadata checks, grid alignment and analysis-ready output | `science/ingestion/` |
| **Naveen** | Water/change detection, polarization features, baselines, quantitative evaluation and uncertainty | `science/analysis/` |
| **Nidhi** | React app, map and radar overlays, timeline, comparisons, layer selection and charts | `web/` |
| **Shridhar** | FastAPI and scientific backend services, contextual datasets, evidence/passports and metadata APIs | `api/` |
| **Hansika** | UI/UX direction, visual components, accessible story experience, graphics, presentation and demo | `design/`, coordinated `web/` components |

## Coordination boundaries
- Veer + Naveen: agree what calibrated channels, masks, CRS, timestamps and metadata are delivered to detection.
- Naveen + Shridhar: agree how change features, uncertainty and provenance are exposed.
- Nidhi + Hansika: share one UI design and component system; Nidhi leads map functionality, Hansika leads UX/story design.
- Shoaib + Shridhar: Shoaib owns orchestration and integration; Shridhar owns scientific API logic. Avoid duplicated route ownership.
- **All team PRs are reviewed and merged by Shoaib.** Team members must not independently merge to `main`.

## Team decisions
- Challenge: Dancing with the SARs.
- Project: SARPulse; team: StarFire.
- Focus: scientifically honest NISAR-based water/wetland changes.
- Brahmaputra is a **candidate** region, conditional on compatible downloadable NISAR observations.
- Initial goal: one authentic, reproducible end-to-end investigation. All advanced ideas are conditional on working science.
