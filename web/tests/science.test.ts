import { describe,it,expect,vi } from "vitest";
import { readFileSync } from "node:fs";
import { adaptScientificBundle, nearestSamplePassport,loadScientificSite } from "../src/lib/science";
import { parseStudyPackage } from "../src/lib/validate-package";

const read=(name:string)=>JSON.parse(readFileSync(new URL(`../public/data/sites/biesbosch-netherlands/${name}.json`,import.meta.url),"utf8"));
const raw=()=>({site:read("site"),scenes:read("scenes"),analysis:read("analysis"),timeseries:read("time_series"),layers:read("layers"),samples:read("samples"),context:read("context")});
describe("scientific frontend connection",()=>{
  it("loads API endpoint URLs exactly, without a trailing slash on the site record",async()=>{
    const r=raw();const endpoints:Record<string,unknown>={"":r.site,scenes:r.scenes,summary:r.analysis,timeseries:r.timeseries,layers:r.layers,samples:r.samples,evidence:r.context};
    const base="https://example.org/api/sites/biesbosch-netherlands";
    const fetcher=vi.fn(async(url:string)=>{
      const suffix=url.slice(base.length);if(suffix==="/")return {ok:false,status:404};
      const key=suffix.startsWith("/")?suffix.slice(1):suffix;
      return {ok:key in endpoints,status:key in endpoints?200:404,json:async()=>endpoints[key]};
    });
    vi.stubGlobal("fetch",fetcher);
    try{expect((await loadScientificSite("https://example.org/api","biesbosch-netherlands",true)).status).toBe("provided");expect(fetcher).toHaveBeenCalledWith(base,expect.anything());}
    finally{vi.unstubAllGlobals();}
  });
  it("loads an actual exported scientific delivery without substituting data or units",()=>{
    const r=raw(), s=adaptScientificBundle(r,"https://example.org/data/sites/biesbosch-netherlands/");
    expect(s.status).toBe("provided");
    expect(s.observations).toHaveLength(r.scenes.length);
    expect(s.statistics.gainedWaterKm2).toBe(r.analysis.gained_water_km2);
    expect(s.science?.timeseries.points).toEqual(r.timeseries.points);
    expect(s.observations[0].channels?.find(c=>c.polarization==="HV")?.raster.image?.url).toContain("hv_db_");
    expect(s.signalSeries).toEqual([]); // Water area must not be relabelled radar dB.
    expect(parseStudyPackage(s)).toBe(s);
  });
  it("rejects mixed-status metadata and scientific area overflow",()=>{
    const r=raw();r.scenes[0].data_status="SYNTHETIC/DEMO — NOT NASA OBSERVATIONS";
    expect(()=>adaptScientificBundle(r,"https://example.org/")).toThrow("Inconsistent");
    const b=raw();b.analysis.gained_water_km2=b.analysis.valid_area_km2+1;
    expect(()=>adaptScientificBundle(b,"https://example.org/")).toThrow("areas exceed");
  });
  it("discloses nearest sample coordinates and distance in a static passport",()=>{
    const s=adaptScientificBundle(raw(),"https://example.org/");const p=s.science!.samples[100];
    const passport=nearestSamplePassport(s,p.lon,p.lat);
    expect(passport.evidence[0].values?.sample_distance_km).toBe(0);
    expect(passport.evidence[0].values?.before_hh_db).toBe(p.before_hh_db);
    expect(passport.limitations[0]).toContain("not a measurement at the clicked coordinate");
    expect(passport.limitations.join(" ")).toContain("4.34 days");
  });
  it("rejects unsafe image sources",()=>{
    const s=adaptScientificBundle(raw(),"https://example.org/");
    s.observations[0].raster!.image!.url="javascript:alert(1)";
    expect(()=>parseStudyPackage(s)).toThrow("HTTPS");
  });
});
