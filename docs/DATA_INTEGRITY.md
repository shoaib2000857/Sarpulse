# Scientific data integrity

## Core data requirements
The project's primary measurements must be **real NISAR SAR observations**, with verifiable source product identifiers, observation dates, processing versions, mode, geolocation and polarization.

NISAR Level-2 GCOV data may support a practical terrain-corrected backscatter analysis. Available channels and product structures vary by acquisition.

## Comparability
Before interpreting two scenes as environmental change:
- Confirm product types and processing releases/maturity are comparable.
- Verify valid-data masks, radar polarization and acquisition geometry.
- Align CRS, raster grid and units. Preserve physical values rather than treating rendered pixels as observations.
- Consider speckle, moisture, surface roughness, layover/shadow and geometry-related artifacts.
- Do not assume a pixel difference equals new surface water.

## Interpretation
- Water backscatter can be low for smooth open water, while flooded vegetation may sometimes be brighter through double-bounce responses.
- Rainfall coincidence is **context**, not proof of causality.
- Do not infer precise ground displacement from backscatter-only GCOV imagery.
- Do not claim real-time alerts, certainty, casualty counts or impacted populations from the map alone.
- Separate observed facts, model classifications, physical hypotheses and validation findings.

## Traceability
Record source links, download/access date, observation UTC, coordinates, CRS, channel, units, product version, algorithm version, threshold choices, reference sources, evaluation methodology and uncertainty limitations.

## Data storage and attribution
- Do not upload raw huge NISAR HDF5 products into GitHub. Keep acquisition manifests, small metadata files and legal derived products in appropriate storage.
- Check redistribution terms for NASA/ISRO and ancillary products.
- Never commit Earthdata credentials or tokens.
- Label *all* generated examples and UI fixtures as synthetic until replaced with validated NASA measurements.

References:
- https://nisar-docs.asf.alaska.edu/
- https://search.asf.alaska.edu/
- https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/
