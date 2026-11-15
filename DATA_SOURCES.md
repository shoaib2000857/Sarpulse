# Data sources and scientific attribution

## Status

The repository includes catalog metadata and synthetic software-test fixtures. A catalog record confirms discovery, not successful pixel retrieval or environmental validation. Per-run input manifests and exported provenance identify the exact products once processed. Do not describe fixture values as NASA observations.

## Primary NISAR inputs

- Mission: NASA–ISRO NISAR, NASA L-band radar.
- Product: L2 GCOV, radiometrically terrain-corrected gamma-0 covariance diagonal power; HH/HV frequency A in the implemented path.
- Archive: NASA ASF DAAC, https://search.asf.alaska.edu/ .
- Technical guide: https://nisar-docs.asf.alaska.edu/gcov/ .
- Access: https://search.earthdata.nasa.gov/search and https://github.com/nsidc/earthaccess .
- Current candidate catalog: `data/manifests/brahmaputra-majuli/`. Candidate main stack uses collection `NISAR_L2_GCOV_PROVISIONAL_V1`, CRID `P05023`, track 40 ascending, frame 15.
- Attribution: NASA/JPL-Caltech NISAR, distributed by ASF DAAC. Preserve applicable data-use/attribution notices; the repository's code license does not override data rights.

The candidate July 22 / October 14, 2026 pair has catalog-listed acquisitions at 23:05:28Z / 23:05:26Z. See the manifest for complete immutable scene IDs and URLs. Actual results must retain these or their final replacements, UTC dates, CRS, mode, channels and processing maturity.

## Optional context adapters

- **Copernicus DEM GLO-30:** ESA/Copernicus via AWS Open Data, https://registry.opendata.aws/copernicus-dem/ . Used only if the DEM adapter is run. Preserve required Copernicus notices and applicable terms with redistributed derivatives.
- **EC JRC Global Surface Water v1.4:** 1984–2021 occurrence, https://global-surface-water.appspot.com/ . Historical context, not contemporary flood truth. The adapter does not claim to use a newer version.
- **NASA GPM IMERG V07 daily Late Run:** `GPM_3IMERGDL`, https://gpm.nasa.gov/data/imerg . About 0.1-degree resolution; optional authenticated retrieval. Accumulation interval is `[before date, after date)`. Missing days are disclosed; partial totals are not complete-period rainfall.
- **Sentinel-2:** a possible independent reference or optical context, not yet acquired by the integration. Cite actual product/date, masking, annotation method, license and temporal tolerance if used.

## Synthetic test data

`api/fixtures/`, `science/ingestion/tests/synthetic_gcov.py` and `science/analysis/tests/synthetic_stack.py` contain explicitly simulated values. Synthetic HDF5 carries a `sarpulse_synthetic` attribute; derived records retain `SYNTHETIC/DEMO — NOT NASA OBSERVATIONS`.

## Resources

Challenge and resource list were supplied in `infodump.md`; current submission rules were supplied by the team. Official URLs: https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/ and https://www.spaceappschallenge.org/resources/project-submission-guide/ . Scientific method/resource links and software used in this integration are listed in `docs/SUBMISSION_DRAFT.md` and `ATTRIBUTION.md`.
