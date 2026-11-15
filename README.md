# SARPulse 🌍🛰️

**Team StarFire · NASA Space Apps Challenge 2026**

> Earth's changes. Revealed by radar.

SARPulse is Team StarFire's selected concept for the 2026 challenge **[Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)**. Our goal during the hackathon is to explore how NASA–ISRO **NISAR synthetic-aperture radar observations** can help people investigate changes across Earth's surface.

**Status: connected application with real NISAR investigations.** The project processes and displays two genuine GCOV pairs: Brahmaputra–Majuli, Assam (July 22 / October 14, 2026), and Biesbosch wetlands, Netherlands (July 19 / October 11, 2026). The UI loads precomputed scientific records and georeferenced HH/HV/change images, exposes Change Passports and scientific exports, and includes a seven-slide demonstration. The statistical baseline is exploratory: the Biesbosch optical-reference comparison reveals substantial false positives, and Assam has no independent reference comparison. Read the limitations before interpreting a candidate change as water or flooding.

**Run the complete application:** `docker compose up --build`, then open http://127.0.0.1:8000 . The image includes the frontend, API and both precomputed investigations. Credentials are required to reproduce source-data retrieval, not to view the published results. See [release status](docs/FINAL_STATUS.md).

## Run the integrated project

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.lock.txt
uv pip install --python .venv/Scripts/python.exe --no-deps -e .
.venv/Scripts/python scripts/sarpulse.py doctor
.venv/Scripts/python scripts/sarpulse.py serve --data-dir web/public/data/sites
```

The last command serves the genuine precomputed investigations at http://127.0.0.1:8000/docs and, after `npm --prefix web run build`, the complete frontend at `/`. `api/fixtures` remains available for explicitly synthetic software tests. See [the platform runbook](platform/README.md) and [shared contracts](contracts/README.md).

Start the frontend separately with `cd web`, `npm ci`, then `npm run dev`. It includes geographic exploration, comparisons, a Science Lab, guided stories and a 3D presentation. See [frontend setup and data boundaries](web/README.md).

**Public project:** https://sarpulse.adoredrose256.chatgpt.site · [Seven-slide demo](https://sarpulse.adoredrose256.chatgpt.site/demo/) · [Demo PDF](https://sarpulse.adoredrose256.chatgpt.site/demo/sarpulse-demo.pdf).

Video production: [complete project context, asset paths and cinematic brief](docs/VIDEO_PRODUCTION_HANDOFF.md) for the separate studio Codex session.

Submission material: [final form-ready fields](docs/SUBMISSION_FINAL.md). The requested domain `sarpulse.shoaibssm.me` awaits the records in [public deployment](docs/PUBLIC_DEPLOYMENT.md). The supplied guide requires a **<=30-second video or <=7-slide deck**, superseding the master plan's longer demonstration proposal. This November 16 release does not establish a submission before the supplied November 15 deadline.

## 📅 Important dates

- **7–13 Nov 2026:** team onboarding, reading, skills preparation and environment readiness only.
- **14–15 Nov 2026:** hackathon build window. Begin actual challenge solution work when the event officially starts.
- **15 Nov 2026, 23:59 local time:** project submission deadline. Verify your Local Event's instructions.

Follow the [official 2026 Space Apps event](https://www.spaceappschallenge.org/2026/) and participant/local-event guidance. The pre-event preparation instructions below are retained as historical team policy; current implementation and release evidence are in [final status](docs/FINAL_STATUS.md).

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
5. Read the [full supplied master plan](StarFire_SARPulse_2026_Master_Plan%20%281%29.md), [current supplied challenge/submission material](infodump.md) and [confirmed v0 interfaces](contracts/README.md).

## 📂 Work areas

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

`science/`, `api/`, `platform/`, `contracts/`, `web/` and integration tests contain implementations. `design/` documents the frontend/UX team's delivered experience and its remaining data requirements.

## 🛰️ Data and integrity

NISAR products are scientific measurements, not ordinary photos. Do not label raw visual differences as confirmed floods or invent accuracy, sensor coverage, sample data, or impact numbers. Preserve observation IDs, dates, polarization, versions, georeferencing, attribution and limits. See [Data integrity](docs/DATA_INTEGRITY.md).

## 🔗 Official references

- [2026 challenge statement](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)
- [NASA Space Apps 2026](https://www.spaceappschallenge.org/2026/)
- [Alaska Satellite Facility Vertex](https://search.asf.alaska.edu/)
- [NISAR documentation](https://nisar-docs.asf.alaska.edu/)

---

*Team StarFire is an independent hackathon team; this repository is not an official NASA/ISRO product.*
