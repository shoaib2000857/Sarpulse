import { useState } from "react";
import { assetUrl } from "../lib/science";
import { downloadFile } from "../lib/study";
import type { ScientificData } from "../types/science";

export default function ScientificEvidence({science}:{science:ScientificData}) {
  const [layerId,setLayerId] = useState("change_class");
  const layer = science.layers.find(l=>l.id===layerId), a=science.analysis;
  return <section className="science-panel connected-evidence" aria-label="Scientific processing evidence">
    <h2>Scientific processing evidence</h2>
    <p>{a.data_status} · {a.processing_version}</p>
    <p><strong>Method:</strong> {a.threshold_method}</p>
    <p><strong>Independent validation:</strong> {a.validation_status}</p>
    <label className="field-label">Processed layer
      <select value={layerId} onChange={e=>setLayerId(e.target.value)}>{science.layers.filter(l=>l.png).map(l=><option value={l.id} key={l.id}>{l.title}</option>)}</select>
    </label>
    {layer?.png && <figure><img src={assetUrl(layer.png,science.siteBase)} alt={layer.title} style={{maxWidth:"100%",maxHeight:440,objectFit:"contain",background:"#151c27"}} />
      <figcaption>{layer.title}{layer.display_range_db ? ` · display range ${layer.display_range_db.join(" to ")} dB` : " · derived classification"}</figcaption>
      {layer.geotiff && <a href={assetUrl(layer.geotiff,science.siteBase)} download>Download source GeoTIFF</a>}</figure>}
    <details open><summary>Water extent through time (km²)</summary><div className="table-scroll"><table>
      <caption>Common valid area: {science.timeseries.common_valid_area_km2 ?? "not supplied"} km². {a.data_status}</caption>
      <thead><tr><th>Observation UTC date</th><th>Water area (km²)</th><th>Threshold sensitivity (km²)</th><th>Quality flags</th></tr></thead>
      <tbody>{science.timeseries.points.map(p=><tr key={p.scene_id}><td>{p.date}</td><td>{p.water_area_km2 ?? "Unavailable"}</td>
        <td>{p.water_area_km2_range?.join(" – ") ?? "Unavailable"}</td><td>{p.quality_flags.join(", ") || "None reported"}</td></tr>)}</tbody>
    </table></div><p>Acquisitions are discrete. Sensitivity ranges are not calibrated probabilities or confidence intervals.</p></details>
    {science.context.length>0 && <details open><summary>Contextual evidence</summary>{science.context.map((c,i)=><p key={i}><strong>{c.kind}:</strong> {c.value ?? "Unavailable"} {c.units}. {c.caveat} Source: {c.source}. Status: {c.data_status}.</p>)}</details>}
    {(["thresholds","area_ranges_km2","baseline_comparison","method_agreement","validation"] as const).map(k=>a[k] && <details key={k}><summary>{k.replaceAll("_"," ")}</summary><pre>{JSON.stringify(a[k],null,2)}</pre>
      {k==="method_agreement" && <p>Internal method consistency only; not independent accuracy.</p>}</details>)}
    <button onClick={()=>downloadFile("sarpulse-scientific-evidence.json",JSON.stringify(science,null,2),"application/json")}>Download full scientific evidence</button>
  </section>;
}
