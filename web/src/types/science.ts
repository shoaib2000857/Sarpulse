export type ScientificScene = {
  scene_id: string; acquired_at_utc: string; source: string; data_url?: string | null;
  maturity: string; crid: string | null; polarizations: string[];
  grid_epsg: number; pixel_spacing_m: number; data_status: string;
};
export type ScientificSample = {
  lon: number; lat: number; valid: boolean; change_class: string;
  before_hh_db: number | null; after_hh_db: number | null;
  before_hv_db: number | null; after_hv_db: number | null;
  slope_deg?: number | null; jrc_occurrence_pct?: number | null;
};
export type ScientificAnalysis = {
  aoi_id: string; before_scene_id: string; after_scene_id: string;
  source_scene_ids: string[]; data_status: string; processing_version: string;
  valid_area_km2: number; gained_water_km2: number; lost_water_km2: number;
  ambiguous_km2: number; threshold_method: string; validation_status: string;
  limitations: string[]; provenance: Record<string, unknown>;
  area_ranges_km2?: Record<string, unknown>; thresholds?: Record<string, unknown>;
  baseline_comparison?: Record<string, unknown>; method_agreement?: Record<string, unknown>;
  validation?: unknown[];
};
export type ScientificContext = {
  kind: string; source: string; value: number | null; units?: string | null;
  caveat: string; data_status: string; period_start?: string | null; period_end?: string | null;
};
export type ScientificLayer = {
  id: string; kind: string; title: string; png?: string; geotiff?: string;
  scene_id?: string; date?: string; display_range_db?: number[];
};
export type ScientificData = {
  siteId: string; apiBase?: string; siteBase: string;
  analysis: ScientificAnalysis; scenes: ScientificScene[]; samples: ScientificSample[];
  context: ScientificContext[];
  timeseries: { aoi_id: string; points: { date: string; scene_id: string; water_area_km2: number | null;
    water_area_km2_range?: number[]; threshold_db?: number; quality_flags: string[] }[];
    data_status: string; common_valid_area_km2?: number };
  layers: ScientificLayer[];
};
export type Passport = {
  site_id: string; lon: number; lat: number; change_class: string; data_status: string;
  before_scene_id: string; after_scene_id: string;
  evidence: { label: string; statement: string; values?: Record<string, unknown>; source?: string | null }[];
  limitations: string[]; provenance: Record<string, unknown>;
};
