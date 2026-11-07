# Instructions for coding agents (Codex / Claude Code)

You are working on **SARPulse**, Team StarFire's entry for the 2026 NASA Space Apps challenge *Dancing with the SARs*.

## Read first
- `README.md`, `docs/TEAM.md`, `docs/WORKFLOW.md`, `docs/DATA_INTEGRITY.md`, and the team's master plan.
- Check the official 2026 hackathon rules before generating or modifying challenge-solution code. **Before the event starts, perform only permitted preparatory and documentation tasks.**

## Non-negotiable engineering guidelines
- Treat `main` as protected by team process. Work in a person's feature branch; do not merge. Shoaib owns PR reviews and merges.
- Stay inside the designated module unless changes to shared interfaces are explicitly agreed.
- Inspect existing contracts before inventing APIs, file structures or data schemas.
- Make small, testable, reviewable changes. Report verification commands and outcomes.
- Never claim a fake fixture is NASA data. Don't fabricate acquisition IDs, georeferencing, polarization layers, classification metrics or results.
- Scientific claims must preserve units, timestamp, coordinate reference system, processing release, polarization and provenance.
- NISAR SAR backscatter is not an RGB photo. Changes in signal do not automatically prove flooding.
- Don't imply NISAR GCOV alone measures displacement, or that cloud resistance means all-weather accuracy.
- Prefer robust, precomputed demo outputs to fragile heavy on-demand processing.
- Do not introduce huge ML models, complex infrastructure or an LLM without a clear validated benefit.
- Don't commit credentials, downloads, secrets or data with unclear redistribution rights.

## Team ownership
- Shoaib: `platform/`, shared architecture/CI, integration, review and merges.
- Veer: `science/ingestion/`.
- Naveen: `science/analysis/`.
- Nidhi: primary application in `web/`, mapping and visualizations.
- Shridhar: `api/`.
- Hansika: `design/`, story/UX components in `web/` by coordination with Nidhi, demo assets.

## Definition of done for any future implementation
Relevant tests pass, documentation is accurate, data lineage is retained, and the module integrates through agreed interfaces. Flag blockers honestly; never silently replace missing scientific data with synthetic results.
