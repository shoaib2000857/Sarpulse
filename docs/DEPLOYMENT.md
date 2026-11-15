# Deployment and frontend handoff

The chosen project URL is **https://sarpulse.shoaibssm.me**. At the November 15 local check the hostname did not resolve. DNS, HTTPS and the actual public site must be verified before using it as the final project link. The public repository is an available alternate project link: https://github.com/shoaib2000857/Sarpulse . The required demo needs its own public slides/video URL.

## Static-first application

Nidhi/Hansika own `web/`; no frontend implementation was present in the branches integrated for this change. The platform does not invent or claim a deployed map interface. Once their app is available:

1. Export a real, inspected science bundle using `sarpulse export` (see `platform/README.md`).
2. Copy that bundle into the app's static data directory, for example `web/public/data/`. Point its loader at `/data/sites.json`.
3. Build the frontend with its own documented package manager; deploy the production output to the chosen host.
4. Configure the custom-domain record to the hosting provider's verified target and enable HTTPS. Do not guess a DNS target.
5. Verify the actual public app, layer URLs, data labels, keyboard controls and downloads in a private browser. Static maps must not depend on Earthdata credentials.

`contracts/README.md` documents static and API loaders. Relative layer URLs must resolve from each site folder. Static CSV/GeoJSON/provenance files can be direct downloads. Dynamic point passports need the API or a clearly disclosed sparse-sample client implementation.

## API container

```powershell
docker build -t sarpulse-api:0.1 .
docker run --rm -p 8000:8000 --mount type=bind,source=<absolute-delivery-folder>,target=/data,readonly -e 'SARPULSE_CORS_ORIGINS=["https://sarpulse.shoaibssm.me"]' sarpulse-api:0.1
```

The mounted folder must contain `sites/<id>/...` (the layout produced by `export`). The API does not process satellite data at runtime. Set CORS to the frontend's actual origins. Container port is 8000; use the host's HTTPS ingress/reverse proxy. `/api/health` reports loaded sites and `/docs` exposes the API. An empty sites list means data is not mounted/configured, even if the HTTP server is running.

The Docker recipe is provided; container execution is only verified if recorded in `docs/INTEGRATION_STATUS.md`. No hosting account, DNS mutation, paid resource or external deployment is implicitly verified by the existence of these files.

## CI/CD

`.github/workflows/ci.yml` runs scientific, API and integration tests and contract checks. `.github/workflows/delivery.yml` packages a validated precomputed delivery from the checked-out repository when explicitly dispatched. Raw GCOV products and Earthdata credentials are never committed or required by CI tests.

Automatic frontend publication awaits the actual frontend and selected host. This avoids publishing a synthetic fixture or overwriting the custom domain with an unrelated scaffold. The deployment artifact is ready for the frontend team's hosting workflow; public scientific readiness remains conditional on authentic processed data.

