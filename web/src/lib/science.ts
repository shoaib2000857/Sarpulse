import type { StudyPackage, RasterLayer } from "../types/frontend";
import type { Passport, ScientificAnalysis, ScientificContext, ScientificData, ScientificLayer, ScientificSample, ScientificScene } from "../types/science";
import { parseStudyPackage } from "./validate-package";

const SYNTHETIC = "SYNTHETIC/DEMO — NOT NASA OBSERVATIONS";
const object = (v: unknown): Record<string, any> => {
  if (!v || typeof v !== "object" || Array.isArray(v)) throw new Error("Invalid scientific record");
  return v as Record<string, any>;
};
const array = (v: unknown): any[] => { if (!Array.isArray(v)) throw new Error("Invalid scientific array"); return v; };
const finite = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);
export function assetUrl(path: string, base: string) {
  const url = new URL(path, base.endsWith("/") ? base : base + "/");
  if (url.protocol !== "https:" && !(url.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname)))
    throw new Error("Scientific assets require HTTPS or a local development server");
  if (url.username || url.password) throw new Error("Asset URLs must not contain credentials");
  return url.href;
}

export function adaptScientificBundle(raw: Record<string, unknown>, siteBase: string, apiBase?: string): StudyPackage {
  const site = object(raw.site), analysis = object(raw.analysis) as ScientificAnalysis;
  const scenes = array(raw.scenes) as ScientificScene[], layersDoc = object(raw.layers);
  const timeseries = object(raw.timeseries) as ScientificData["timeseries"];
  const samples = array(raw.samples) as ScientificSample[], context = array(raw.context ?? []) as ScientificContext[];
  if (!["observed", SYNTHETIC].includes(site.data_status)) throw new Error("Unknown radar data status");
  if ([analysis, timeseries, layersDoc, ...scenes].some(r => r.data_status !== site.data_status))
    throw new Error("Inconsistent radar data status in scientific bundle");
  if ([analysis.aoi_id, timeseries.aoi_id, layersDoc.aoi_id].some(id => id !== site.id))
    throw new Error("Scientific bundle has mismatched site identifiers");
  if (!scenes.some(s => s.scene_id === analysis.before_scene_id) || !scenes.some(s => s.scene_id === analysis.after_scene_id))
    throw new Error("Scientific comparison references missing acquisitions");
  if (![analysis.valid_area_km2, analysis.gained_water_km2, analysis.lost_water_km2, analysis.ambiguous_km2].every(v => finite(v) && v >= 0))
    throw new Error("Invalid scientific area measurements");
  if (analysis.gained_water_km2 + analysis.lost_water_km2 + analysis.ambiguous_km2 > analysis.valid_area_km2 + 0.001)
    throw new Error("Classified areas exceed the valid area");
  if (!Array.isArray(layersDoc.image_coordinates) || layersDoc.image_coordinates.length !== 4 ||
      !layersDoc.image_coordinates.every((p: unknown) => Array.isArray(p) && p.length === 2 && p.every(finite)))
    throw new Error("Four geographic image corners are required");
  const layers = array(layersDoc.layers) as ScientificLayer[];
  const raster = (layer?: ScientificLayer): RasterLayer | undefined => layer?.png ? {
    image: { url: assetUrl(layer.png, siteBase), coordinates: layersDoc.image_coordinates },
    attribution: layersDoc.attribution, minDb: layer.display_range_db?.[0] ?? -25,
    maxDb: layer.display_range_db?.[1] ?? 0,
  } : undefined;
  const bbox = object(site.bbox), bounds: [number, number, number, number] = [bbox.west, bbox.south, bbox.east, bbox.north];
  const observed = site.data_status === "observed";
  const sorted = [...scenes].sort((a,b) => a.acquired_at_utc.localeCompare(b.acquired_at_utc));
  if (new Set(sorted.map(s => s.scene_id)).size !== sorted.length) throw new Error("Duplicate acquisition identifiers");
  const study: StudyPackage = {
    schemaVersion: 1, status: observed ? "provided" : "synthetic", title: site.name, region: site.name,
    description: site.description, bounds, center: [(bounds[0]+bounds[2])/2, (bounds[1]+bounds[3])/2],
    footprint: { type: "Feature", properties: { label: "Analysis grid extent" }, geometry: { type: "Polygon", coordinates: [[
      [bounds[0],bounds[1]], [bounds[2],bounds[1]], [bounds[2],bounds[3]], [bounds[0],bounds[3]], [bounds[0],bounds[1]],
    ]] } }, overlays: { type: "FeatureCollection", features: [] },
    observations: sorted.map(s => ({ key: s.scene_id, label: s.acquired_at_utc,
      acquiredAtUtc: s.acquired_at_utc, productId: s.scene_id, sourceUrl: s.data_url ?? null,
      polarization: s.polarizations.includes("HHHH") ? "HH" : s.polarizations[0],
      processingRelease: s.crid, maturity: s.maturity, crs: `EPSG:${s.grid_epsg}`, pixelSpacingM: s.pixel_spacing_m,
      channels: ["HH", "HV"].flatMap(pol => { const r = raster(layers.find(l => l.scene_id === s.scene_id && l.id.startsWith(pol.toLowerCase() + "_db_")));
        return r ? [{ polarization: pol, raster: r }] : []; }),
      raster: raster(layers.find(l => l.scene_id === s.scene_id && l.id.startsWith("hh_db_"))),
    })),
    statistics: { validAreaKm2: observed ? analysis.valid_area_km2 : null,
      gainedWaterKm2: observed ? analysis.gained_water_km2 : null, lostWaterKm2: observed ? analysis.lost_water_km2 : null,
      changedSharePct: observed && analysis.valid_area_km2 > 0 ? 100 * (analysis.gained_water_km2 + analysis.lost_water_km2) / analysis.valid_area_km2 : null },
    signalSeries: [], provenance: `Sources: ${analysis.source_scene_ids.join(", ")}. Method: ${analysis.processing_version}. ${site.data_status}.`,
    limitations: analysis.limitations, validationStatus: analysis.validation_status,
    science: { siteId: site.id, siteBase, apiBase, analysis, scenes: sorted, samples, context, timeseries, layers },
  };
  return parseStudyPackage(study);
}

async function json(url: string, signal?: AbortSignal) {
  const r = await fetch(url, { signal });
  if (!r.ok) throw new Error(`Scientific data request failed (${r.status})`);
  return r.json();
}
export type SiteOption = { id: string; name: string; data_status: string; path?: string };
export async function loadSites(base: string, api: boolean, signal?: AbortSignal): Promise<SiteOption[]> {
  const v = await json(api ? `${base.replace(/\/$/, "")}/sites` : assetUrl("sites.json", base), signal);
  return array(v).map(s => { const o = object(s); if (typeof o.id !== "string" || typeof o.name !== "string" || !/^[\w-]+$/.test(o.id))
    throw new Error("Invalid scientific site listing"); return o as SiteOption; });
}
export async function loadScientificSite(base: string, id: string, api: boolean, signal?: AbortSignal) {
  if (!/^[\w-]+$/.test(id)) throw new Error("Invalid scientific site identifier");
  const siteBase = api ? `${base.replace(/\/$/, "")}/sites/${id}/` : assetUrl(`sites/${id}/`, base);
  const names = api ? ["", "scenes", "summary", "timeseries", "layers", "samples", "evidence"] :
    ["site.json", "scenes.json", "analysis.json", "time_series.json", "layers.json", "samples.json", "context.json"];
  const data = await Promise.all(names.map((n,i) => json(api && i===0 ? siteBase.slice(0,-1) : siteBase+n, signal).catch(e => { if(i===6) return []; throw e; })));
  return adaptScientificBundle(Object.fromEntries(["site","scenes","analysis","timeseries","layers","samples","context"].map((k,i) => [k,data[i]])), siteBase, api ? base : undefined);
}
export function nearestSamplePassport(study: StudyPackage, lon: number, lat: number): Passport {
  const s = study.science;
  if (!s || !s.samples.length) throw new Error("No analysed samples are available for this investigation");
  const distance = (p: ScientificSample) => Math.hypot((p.lon-lon)*111.32*Math.cos(lat*Math.PI/180), (p.lat-lat)*110.57);
  const p = s.samples.reduce((a,b) => distance(a) <= distance(b) ? a : b), d = distance(p);
  return { site_id:s.siteId, lon, lat, before_scene_id:s.analysis.before_scene_id, after_scene_id:s.analysis.after_scene_id,
    change_class:p.change_class, data_status:s.analysis.data_status, provenance:s.analysis.provenance,
    limitations:[`Static delivery: nearest analysed sample is ${(d*1000).toFixed(0)} m away at ${p.lon}, ${p.lat}; this is not a measurement at the clicked coordinate.`,
      ...(!p.valid ? ["This sample has invalid radar data; no environmental interpretation is supported."] : []),
      ...(d > 1 ? ["Sample is more than 1 km away; do not assign its class to the clicked location."] : []), ...s.analysis.limitations],
    evidence:[{label: study.status === "provided" ? "Observed" : "Unverified", statement:"Radar values at the disclosed nearest sample (gamma-0 dB)", values:{...p, sample_distance_km:d}},
      {label:"Derived", statement:s.analysis.threshold_method, values:{change_class:p.change_class, validation_status:s.analysis.validation_status}},
      ...s.context.map(c => ({label:"Context",statement:`${c.kind}: ${c.value ?? "Unavailable"} ${c.units ?? ""}. ${c.caveat}`, values:{data_status:c.data_status}, source:c.source})),
      {label:"Hypothesis",statement: p.valid ? "Radar signatures may be consistent with open-water change. Smooth soil, roughness, vegetation and geometry can also affect the signal; this is not confirmation of flooding." : "No interpretation is supported for invalid radar data."}],
  };
}
export async function loadPassport(study: StudyPackage, lon: number, lat: number, signal?: AbortSignal): Promise<Passport> {
  if (study.science?.apiBase) return json(`${study.science.apiBase.replace(/\/$/, "")}/sites/${study.science.siteId}/passport?lon=${lon}&lat=${lat}`, signal);
  return nearestSamplePassport(study,lon,lat);
}
