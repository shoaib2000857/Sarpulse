import type { Feature, Polygon } from "geojson";
import type { OverlayProperties, StudyPackage } from "../types/frontend";

const cell = (
  label: string,
  kind: OverlayProperties["kind"],
  x: number,
  y: number,
  w: number,
  h: number,
  observations: string[],
): Feature<Polygon, OverlayProperties> => ({
  type: "Feature",
  properties: { label, kind, observations },
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [x, y],
        [x + w, y],
        [x + w, y + h],
        [x, y + h],
        [x, y],
      ],
    ],
  },
});

// Original UI fixture. Rectangles are deliberately schematic, not mapped water extents.
// No NASA scenes, polarization measurements, acquisition dates, or processing releases are invented.
export const demoStudy: StudyPackage = {
  schemaVersion: 1,
  status: "synthetic",
  title: "Brahmaputra floodplain",
  region: "Assam, India · candidate study area",
  description:
    "A place to investigate the changing relationship between water and land. Explore the interface with schematic test geometry while verified observations are unavailable.",
  center: [93.8, 26.94],
  bounds: [93.61, 26.8, 93.99, 27.08],
  footprint: {
    type: "Feature",
    properties: {
      label: "Illustrative workspace extent — not an analyzed footprint",
    },
    geometry: {
      type: "Polygon",
      coordinates: [
        [
          [93.61, 26.8],
          [93.99, 26.8],
          [93.99, 27.08],
          [93.61, 27.08],
          [93.61, 26.8],
        ],
      ],
    },
  },
  observations: ["Baseline", "Expansion", "Contraction", "Recovery"].map(
    (label, i) => ({
      key: `fixture-${i}`,
      label,
      acquiredAtUtc: null,
      productId: null,
      sourceUrl: null,
      polarization: null,
      processingRelease: null,
      maturity: null,
      crs: null,
      pixelSpacingM: null,
    }),
  ),
  overlays: {
    type: "FeatureCollection",
    features: [
      cell("Test cell A", "stable", 93.67, 26.86, 0.04, 0.025, [
        "fixture-0",
        "fixture-1",
        "fixture-2",
        "fixture-3",
      ]),
      cell("Test cell B", "stable", 93.73, 26.89, 0.04, 0.025, [
        "fixture-0",
        "fixture-1",
        "fixture-2",
        "fixture-3",
      ]),
      cell("Test cell C", "stable", 93.79, 26.92, 0.04, 0.025, [
        "fixture-0",
        "fixture-1",
        "fixture-2",
        "fixture-3",
      ]),
      cell("Test cell D", "stable", 93.85, 26.95, 0.04, 0.025, [
        "fixture-0",
        "fixture-1",
        "fixture-2",
        "fixture-3",
      ]),
      cell("Test cell E", "stable", 93.91, 26.98, 0.04, 0.025, [
        "fixture-0",
        "fixture-1",
        "fixture-2",
        "fixture-3",
      ]),
      cell("Test gain A", "gain", 93.73, 26.925, 0.04, 0.025, [
        "fixture-1",
        "fixture-2",
      ]),
      cell("Test gain B", "gain", 93.79, 26.955, 0.04, 0.025, ["fixture-1"]),
      cell("Test gain C", "gain", 93.85, 26.985, 0.04, 0.025, [
        "fixture-1",
        "fixture-2",
        "fixture-3",
      ]),
      cell("Test loss A", "loss", 93.79, 26.885, 0.04, 0.025, ["fixture-0"]),
      cell("Test loss B", "loss", 93.85, 26.915, 0.04, 0.025, [
        "fixture-0",
        "fixture-1",
      ]),
      cell("Masked test cell", "no-data", 93.91, 26.945, 0.04, 0.025, []),
    ],
  },
  statistics: {
    validAreaKm2: null,
    gainedWaterKm2: null,
    lostWaterKm2: null,
    changedSharePct: null,
  },
  signalSeries: [-18, -23, -20, -17].map((valueDb, i) => ({
    observationKey: `fixture-${i}`,
    valueDb,
  })),
  provenance:
    "Original frontend fixture by Team StarFire. SYNTHETIC/DEMO — NOT NASA OBSERVATIONS. EPSG:4326 coordinates place test rectangles in the candidate region; shapes do not represent observed water or measured change. Chart values are illustrative.",
  limitations: [
    "No verified NISAR acquisitions are connected.",
    "Test cells are schematic UI geometry, not mapped water or flood classifications.",
    "No area estimates, accuracy scores, or impact figures are available.",
    "Backscatter change alone does not establish flooding. GCOV intensity does not measure ground displacement.",
  ],
  validationStatus: "Not scientifically validated",
};
