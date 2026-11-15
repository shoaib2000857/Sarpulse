# Data sources and scientific attribution

## Status

The application includes genuine processed NISAR observations for Brahmaputra–Majuli and Biesbosch, plus separately labelled synthetic software fixtures. Exact acquisitions, physical units, CRS, processing release, derived rasters and reference results are retained in `web/public/data/sites/`. A real observation does not establish classifier accuracy or a confirmed flood.

Assam uses July 22 / October 14, 2026 GCOV data, retrieved directly from ASF with the user's local Earthdata credentials. Biesbosch uses July 19 / October 11, 2026 GCOV data, with original NASA product identifiers corroborated against live ASF metadata; native subsets were accessed through a public mirror. The transport source, native windows, hashes and reuse evidence are retained in `web/public/data/sites/biesbosch-netherlands/source-provenance.json`. No HDF5 originals or credentials are committed.

Biesbosch's independent cross-sensor reference is Sentinel-2C L2A `S2C_31UFT_20260715_0_L2A`, July 15, 2026 at 10:46:41.387Z. SCL 6 is reference water, 4/5 reference land; other classes are excluded. The optical observation is 4.34 days earlier than NISAR and uses automatic classification, so this comparison is reference agreement, not field accuracy. Water precision 0.2605, recall 0.8906 and F1 0.403 expose substantial false positives; see the full confusion matrix and caveats in the delivered analysis.

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
- **Sentinel-2:** the Biesbosch reference above was obtained from public Sentinel-2 COGs via Earth Search STAC. Processing/SCL definitions: https://sentiwiki.copernicus.eu/web/s2-processing . Source links and hashes are retained in `reference-provenance.json`; Sentinel reuse terms apply.

## Synthetic test data

`api/fixtures/`, `science/ingestion/tests/synthetic_gcov.py` and `science/analysis/tests/synthetic_stack.py` contain explicitly simulated values. Synthetic HDF5 carries a `sarpulse_synthetic` attribute; derived records retain `SYNTHETIC/DEMO — NOT NASA OBSERVATIONS`.

## Resources

Challenge and resource list were supplied in `infodump.md`; current submission rules were supplied by the team. Official URLs: https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/ and https://www.spaceappschallenge.org/resources/project-submission-guide/ . Scientific method/resource links and software used in this integration are listed in `docs/SUBMISSION_DRAFT.md` and `ATTRIBUTION.md`.
