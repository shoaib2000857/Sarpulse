import type { Feature, FeatureCollection, Polygon } from "geojson";
import type { ScientificData } from "./science";

// Frontend view model only. This does not establish a backend or shared scientific API.
export type LayerMode = "after" | "before" | "difference" | "gain" | "loss";
export type Palette = "standard" | "accessible";
// Geographic context only. None of these basemaps is NISAR or SAR data.
export type Basemap = "satellite" | "dark" | "streets" | "none";
// Camera relative to the fitted study extent, so it works for any supplied package.
export type MapCamera = {
  zoomOffset?: number;
  pitch?: number;
  bearing?: number;
};
export type ChangeKind = "stable" | "gain" | "loss" | "no-data";
export type RasterLayer = {
  tiles?: string[];
  image?: { url: string; coordinates: [number, number][] };
  attribution: string;
  minDb: number;
  maxDb: number;
};
export type Observation = {
  key: string;
  label: string;
  acquiredAtUtc: string | null;
  productId: string | null;
  sourceUrl: string | null;
  polarization: string | null;
  processingRelease: string | null;
  maturity: string | null;
  crs: string | null;
  pixelSpacingM: number | null;
  raster?: RasterLayer;
  channels?: { polarization: string; raster: RasterLayer }[];
};
export type OverlayProperties = {
  label: string;
  kind: ChangeKind;
  observations: string[];
};
export type MapSelection = {
  longitude: number;
  latitude: number;
  label: string;
  kind: ChangeKind | null;
};
export type StudyPackage = {
  schemaVersion: 1;
  status: "synthetic" | "provided";
  title: string;
  region: string;
  description: string;
  center: [number, number];
  bounds: [number, number, number, number];
  footprint: Feature<Polygon>;
  overlays: FeatureCollection<Polygon, OverlayProperties>;
  observations: Observation[];
  statistics: {
    validAreaKm2: number | null;
    gainedWaterKm2: number | null;
    lostWaterKm2: number | null;
    changedSharePct: number | null;
  };
  // Presentation of supplied summaries only. No pixel sampling or analysis in the browser.
  signalSeries: { observationKey: string; valueDb: number | null }[];
  provenance: string;
  limitations: string[];
  validationStatus: string;
  science?: ScientificData;
};
export type GeoWorkspaceProps = {
  study: StudyPackage;
  observationKey: string;
  beforeKey: string;
  mode: LayerMode;
  compare: boolean;
  opacity: number;
  palette: Palette;
  basemap: Basemap;
  camera?: MapCamera;
  showFootprint: boolean;
  channel?: string;
  onInspect?: (selection: MapSelection) => void;
};
