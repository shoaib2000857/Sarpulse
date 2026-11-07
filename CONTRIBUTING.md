# Contributing to SARPulse

## Team workflow
1. Read `README.md`, `AGENTS.md`, `docs/TEAM.md` and the master plan before doing any work.
2. Until the official hackathon start, use this repository only for coordination, documentation and permitted preparation. Do **not** commit solution implementation in advance.
3. After the event starts, create a feature branch from up-to-date `main`: `feat/veer-ingestion`, `feat/naveen-analysis`, `feat/nidhi-maps`, `feat/shridhar-api`, `feat/hansika-experience`, `feat/shoaib-platform`.
4. Keep changes focused to your owned module. Make changes to shared contracts only with team agreement.
5. Open a PR into `main`; describe purpose, touched files, tests, real versus fixture data, and any science limitations.
6. **Shoaib reviews PRs and handles merges.** Never push directly to `main` as a normal working practice.
7. Don't commit NASA/Earthdata tokens, secrets, raw satellite datasets or massive binaries.
8. Use honest scientific language; never invent datasets, scene IDs, flood areas or model performance.

## PR readiness
- [ ] Task and scope stated
- [ ] Works locally / relevant checks run
- [ ] No secrets or raw protected data
- [ ] Interfaces and docs updated when necessary
- [ ] Mock/fixture values are conspicuously labeled
- [ ] Scientific claims have evidence or an explicit caveat

Use the PR template in `.github/PULL_REQUEST_TEMPLATE.md`. For collaboration details, see `docs/WORKFLOW.md`.
