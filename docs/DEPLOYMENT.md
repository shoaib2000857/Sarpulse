# Deployment and application handoff

## Public application

Live: https://sarpulse.adoredrose256.chatgpt.site

Seven-slide demo: https://sarpulse.adoredrose256.chatgpt.site/demo/

PDF: https://sarpulse.adoredrose256.chatgpt.site/demo/sarpulse-demo.pdf

The published static build loads two genuine precomputed NISAR investigations without Earthdata credentials. Its Change Passports disclose nearest-sample support and distance. [PUBLIC_DEPLOYMENT.md](PUBLIC_DEPLOYMENT.md) records deployment evidence and the three DNS records needed for the requested custom domain. Source: https://github.com/shoaib2000857/Sarpulse .

## Complete frontend and API

```powershell
docker compose up --build
```

Open http://127.0.0.1:8000 . The multi-stage image builds the frontend with `/api` delivery, includes both scientific cases and serves the API and UI together. `/api/health` lists both sites; `/docs` exposes the scientific API. This mode reads the actual analysed raster pixel for a point passport. Docker build and a browser smoke were verified on November 16, including real images, exact-pixel passport, both site records and demo assets. The image installs Linux raster-library runtime dependencies explicitly.

## Static build and configuration

```powershell
npm --prefix web ci
npm --prefix web run build
```

Deploy `web/dist/` to a static host with a fallback to `index.html`. Default scientific index: `/data/sites.json`. Override using `VITE_SARPULSE_DATA_URL` before building; to use an API instead, set `VITE_SARPULSE_API_URL` to its base URL. See `web/.env.example`. Preserve each site's relative image/CSV/GeoTIFF/JSON paths. Raw GCOV products and credentials must never enter the static output. Public models retain their separate attribution.

The public deployment is static-first; new global analyses run separately with the Python pipeline, are inspected, exported and installed using `scripts/install_web_data.py` before rebuilding. Changing arbitrary dates in the viewer does not rerun detection for a new pair.

## Verification and release

GitHub Actions checks Python on Windows/Linux and frontend type checking, unit tests and production build. The manually dispatched release workflow packages the complete static build. `node scripts/smoke_release.mjs <base-url>` verifies real radar images, passports and demo assets; when an API is present it also checks the two-site health response and exact-pixel evidence. Test results and scientific limitations are recorded in [FINAL_STATUS.md](FINAL_STATUS.md).

Publication does not establish NASA submission or eligibility. The supplied local deadline was November 15, 2026 at 23:59; this release was completed November 16.
