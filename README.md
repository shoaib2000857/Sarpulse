# SARPulse 🌍🛰️

**Team StarFire · NASA Space Apps Challenge 2026**

> Earth's changes. Revealed by radar.

SARPulse is Team StarFire's selected concept for the 2026 challenge **[Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)**. Our goal during the hackathon is to explore how NASA–ISRO **NISAR synthetic-aperture radar observations** can help people investigate changes across Earth's surface.

**Status: scientific modules and platform integrated; real-data execution and frontend delivery pending.** Ingestion, open-water analysis, the FastAPI evidence service, orchestration, exports and integration checks are implemented. Engineering tests use explicitly synthetic inputs. No real environmental measurements or independent accuracy results are claimed by this status.

## Run the integrated project

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements.lock.txt
uv pip install --python .venv/Scripts/python.exe --no-deps -e .
.venv/Scripts/python scripts/sarpulse.py doctor
.venv/Scripts/python scripts/sarpulse.py serve --data-dir api/fixtures
```

The last command serves **synthetic development fixtures** at http://127.0.0.1:8000/docs. See [the platform runbook](platform/README.md) for real GCOV ingestion, analysis, validation and versioned exports; [shared contracts](contracts/README.md) for frontend integration; and [integration status](docs/INTEGRATION_STATUS.md) for verified work and outstanding dependencies.

Submission material: [form-ready draft](docs/SUBMISSION_DRAFT.md). Chosen project URL: https://sarpulse.shoaibssm.me (public availability must be verified; see [deployment](docs/DEPLOYMENT.md)). The current supplied guide requires a **<=30-second video or <=7-slide deck**, superseding the master plan's longer demonstration proposal.

## 📅 Important dates

- **7–13 Nov 2026:** team onboarding, reading, skills preparation and environment readiness only.
- **14–15 Nov 2026:** hackathon build window. Begin actual challenge solution work when the event officially starts.
- **15 Nov 2026, 23:59 local time:** project submission deadline. Verify your Local Event's instructions.

Follow the [official 2026 Space Apps event](https://www.spaceappschallenge.org/2026/) and the latest participant/local-event guidance about when solution work may begin. We are deliberately keeping this scaffold documentation-only before the hackathon and will follow the current official rules.

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

`science/`, `api/`, `platform/`, `contracts/` and integration tests contain implementations. `web/` and `design/` still await the frontend/UX team's delivery in this integrated branch.

## 🛰️ Data and integrity

NISAR products are scientific measurements, not ordinary photos. Do not label raw visual differences as confirmed floods or invent accuracy, sensor coverage, sample data, or impact numbers. Preserve observation IDs, dates, polarization, versions, georeferencing, attribution and limits. See [Data integrity](docs/DATA_INTEGRITY.md).

## 🔗 Official references

- [2026 challenge statement](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/)
- [NASA Space Apps 2026](https://www.spaceappschallenge.org/2026/)
- [Alaska Satellite Facility Vertex](https://search.asf.alaska.edu/)
- [NISAR documentation](https://nisar-docs.asf.alaska.edu/)

---

*Team StarFire is an independent hackathon team; this repository is not an official NASA/ISRO product.*
