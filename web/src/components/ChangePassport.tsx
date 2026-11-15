import { useEffect, useState } from "react";
import { loadPassport } from "../lib/science";
import { downloadFile } from "../lib/study";
import type { StudyPackage } from "../types/frontend";
import type { Passport } from "../types/science";

export default function ChangePassport({study,lon,lat}:{study:StudyPackage;lon:number;lat:number}) {
  const [passport,setPassport] = useState<Passport | null>(null), [error,setError] = useState("");
  useEffect(() => {
    const controller = new AbortController(); setPassport(null); setError("");
    void loadPassport(study,lon,lat,controller.signal).then(setPassport).catch(e => {
      if (!controller.signal.aborted) setError(e instanceof Error ? e.message : "Evidence unavailable");
    });
    return () => controller.abort();
  },[study,lon,lat]);
  return <section className="change-passport" aria-label="Change Passport">
    <h3>Change Passport</h3>
    {error ? <p role="status">{error}</p> : !passport ? <p role="status">Loading scientific evidence…</p> : <>
      <p><strong>{passport.change_class.replaceAll("_"," ")}</strong> · {passport.data_status}</p>
      <p>{passport.limitations[0]}</p>
      {passport.evidence.map((e,i) => <details key={i} open={i<2}><summary>{e.label} — {e.statement}</summary>
        {e.values && <dl>{Object.entries(e.values).map(([k,v]) => <div key={k}><dt>{k.replaceAll("_"," ")}</dt><dd>{v === null ? "Unavailable" : typeof v === "number" ? v.toLocaleString(undefined,{maximumFractionDigits:6}) : typeof v === "object" ? JSON.stringify(v) : String(v)}</dd></div>)}</dl>}
        {e.source && <p>{e.source}</p>}</details>)}
      <details><summary>Limitations and sample support</summary><ul>{passport.limitations.map((l,i)=><li key={i}>{l}</li>)}</ul></details>
      <button onClick={()=>downloadFile("sarpulse-change-passport.json",JSON.stringify(passport,null,2),"application/json")}>Download Change Passport</button>
    </>}
  </section>;
}
