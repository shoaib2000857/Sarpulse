# Development and integration workflow

## Before the event
- Read the challenge, the master plan, team ownership and data documentation.
- Confirm GitHub access, Git familiarity, tool availability and required Earthdata accounts.
- Review *documentation*, coordinate contracts and research independently.
- No challenge solution implementation before the official event starts. The event's latest rules prevail.

## Once the build window opens
1. Shoaib confirms event eligibility and locks the initial shared input/output interfaces.
2. Veer verifies actual comparable NISAR acquisitions; no fake data substituted.
3. Each member works in a named branch, owning their defined module.
4. Shared fixture files must be clearly labeled **SYNTHETIC/DEMO — NOT NASA OBSERVATIONS**.
5. Open concise PRs; Shoaib reviews and merges after checking interface compatibility.
6. Run an end-to-end scientific demo early. Polish and optional features come after it works.

## Planned contracts (not finalized)
- Acquisition metadata: product ID, URL/source, acquisition time, instrument/band, polarization, product type, processing version, bounds, CRS and data maturity.
- Analysis-ready rasters: aligned geographic grid, valid-data masks, calibrated values, units and shape.
- Detection result: change mask, per-class area, optional uncertainty and validation details with method/version.
- Web layer manifest: geographic bounds, raster layer URLs, available dates, attribution and the underlying source IDs.
- Evidence passport: scene lineage, processing parameters, observed evidence, plausible interpretations and limitations.

**Shoaib owns final decisions about shared schemas.** Keep the schemas minimal and do not invent implementation-specific JSON fields until the science pipeline is scoped.

## Quality gates
- Valid scientific inputs and consistent comparisons
- One authentic demonstrable case study
- Clear science and data provenance
- A deployed accessible public demo
- Documentation, presentation and deadline checks
