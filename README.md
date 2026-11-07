# SARPulse 🌍🛰️

**Team StarFire · NASA Space Apps Challenge 2026**

> Earth's changes. Revealed by radar.

SARPulse is Team StarFire's selected concept for the 2026 challenge **[Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)**. Our goal during the hackathon is to explore how NASA–ISRO **NISAR synthetic-aperture radar observations** can help people investigate changes across Earth's surface.

**Status: team preparation / repository setup.** This is a collaboration scaffold, **not a working scientific application**. Scientific results, interactive maps, data pipelines and performance metrics have not been implemented or validated.

## 📅 Important dates

- **7–13 Nov 2026:** team onboarding, reading, skills preparation and environment readiness only.
- **14–15 Nov 2026:** hackathon build window. Begin actual challenge solution work when the event officially starts.
- **15 Nov 2026, 23:59 local time:** project submission deadline. Verify your Local Event's instructions.

The [2026 Space Apps event](https://www.spaceappschallenge.org/2026/) and [2026 Local Event guidance](https://www.spaceappschallenge.org/2026/local-events/santiago-dominican-republic/) state that development of the competition solution must wait until the official start. This repository is intended to make collaboration easier before then.

## 👥 Team and areas

| Member | Primary area |
| --- | --- |
| **Shoaib** | Core platform, architecture, contracts, integration, CI/CD, PR reviews and merges |
| **Veer** | NISAR data discovery, processing, quality and analysis-ready observations |
| **Naveen** | Change detection, ML, quantitative evaluation and uncertainty |
| **Nidhi** | React frontend, geospatial maps and scientific visualizations |
| **Shridhar** | Backend APIs, scientific context and provenance |
| **Hansika** | UI/UX, interactive experience, story mode, graphics and presentation |

All six contribute to research, testing, documentation and scientific accuracy. See [team ownership](docs/TEAM.md) for details.

## 🚀 Start here

1. Read [Contributing](CONTRIBUTING.md) for branching and pull-request rules.
2. Read [Team ownership](docs/TEAM.md) and [Development workflow](docs/WORKFLOW.md).
3. Read [Agent guidelines](AGENTS.md) before using Codex or Claude Code.
4. See [Pre-event preparation](docs/PRE_EVENT.md); do not start the solution ahead of the competition.
5. Once the hackathon begins, use the shared master plan and agree on interfaces before implementing features.

## 📂 Planned work areas

```text
science/ingestion/   # Veer: data discovery and preprocessing
science/analysis/    # Naveen: change detection and evaluation
api/                 # Shridhar: backend scientific services
web/                 # Nidhi + Hansika: application and experience
platform/            # Shoaib: orchestration and data delivery
design/              # Hansika: UI/UX and narrative assets
contracts/           # shared integration definitions
docs/                # collaboration, science notes and demos
tests/               # integration and validation
```

These folders are **placeholders**, not completed or approved designs.

## 🛰️ Data and integrity

NISAR products are scientific measurements, not ordinary photos. Do not label raw visual differences as confirmed floods or invent accuracy, sensor coverage, sample data, or impact numbers. Preserve observation IDs, dates, polarization, versions, georeferencing, attribution and limits. See [Data integrity](docs/DATA_INTEGRITY.md).

## 🔗 Official references

- [2026 challenge statement](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)
- [NASA Space Apps 2026](https://www.spaceappschallenge.org/2026/)
- [Alaska Satellite Facility Vertex](https://search.asf.alaska.edu/)
- [NISAR documentation](https://nisar-docs.asf.alaska.edu/)

---

*Team StarFire is an independent hackathon team; this repository is not an official NASA/ISRO product.*
