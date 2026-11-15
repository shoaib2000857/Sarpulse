import { lazy, Suspense, useState } from "react";
import {
  ArrowRight,
  Download,
  ExternalLink,
  FlaskConical,
  Info,
  Waves,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { downloadFile, observationLabel, summaryCsv } from "../lib/study";
import { safeSourceUrl } from "../lib/validate-package";
import type { StudyPackage } from "../types/frontend";
const SignalChart = lazy(() => import("../components/charts/SignalChart"));

export default function ScienceLab({ study }: { study: StudyPackage }) {
  const [index, setIndex] = useState(0);
  const [downloaded, setDownloaded] = useState("");
  const obs = study.observations[index];
  const metrics = [
    ["Analyzed area", study.statistics.validAreaKm2, "km²"],
    ["Water gained", study.statistics.gainedWaterKm2, "km²"],
    ["Water lost", study.statistics.lostWaterKm2, "km²"],
    ["Changed-area share", study.statistics.changedSharePct, "%"],
  ] as const;
  const metadata = [
    ["Acquisition UTC", obs.acquiredAtUtc],
    ["Product identifier", obs.productId],
    ["Polarization", obs.polarization],
    ["Processing release", obs.processingRelease],
    ["Data maturity", obs.maturity],
    ["Source CRS", obs.crs],
    [
      "Posted pixel spacing",
      obs.pixelSpacingM === null
        ? null
        : `${obs.pixelSpacingM} m (not effective resolution)`,
    ],
  ];
  function exportData(kind: "csv" | "json") {
    downloadFile(
      `sarpulse-${study.status}.${kind}`,
      kind === "csv" ? summaryCsv(study) : JSON.stringify(study, null, 2),
      kind === "csv" ? "text/csv;charset=utf-8" : "application/json",
    );
    setDownloaded(
      `Downloaded ${kind === "csv" ? "CSV summary" : "data package"} with ${study.status} status and provenance.`,
    );
  }
  return (
    <div className="science-page page-width">
      <div className="workspace-heading">
        <div>
          <span className="section-kicker">
            <FlaskConical size={15} />
            Science Lab
          </span>
          <h1>Every change needs evidence.</h1>
          <p>
            Look beyond the visualization. Inspect the source, the signal, and
            the uncertainty.
          </p>
        </div>
        <div className="workspace-heading-actions">
          <Button variant="outline" size="sm" onClick={() => exportData("csv")}>
            <Download size={15} />
            Summary CSV
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => exportData("json")}
          >
            <Download size={15} />
            Data package
          </Button>
        </div>
      </div>
      {downloaded && (
        <p role="status" className="export-notice">
          {downloaded}
        </p>
      )}
      <div className="evidence-status">
        <Info size={19} />
        <div>
          <strong>
            {study.status === "synthetic"
              ? "No scientific results are connected"
              : "Supplied results, not independently verified"}
          </strong>
          <p>
            {study.status === "synthetic"
              ? "Interface geometry and chart values are synthetic. Area statistics remain unavailable until a scientifically supported package is supplied."
              : study.validationStatus}
          </p>
        </div>
        <span className="data-badge">
          {study.status === "synthetic" ? "Unverified" : "Supplied"}
        </span>
      </div>
      <section className="metrics-grid" aria-label="Supplied area statistics">
        {metrics.map(([label, value, unit]) => (
          <div className="metric" key={label}>
            <span>{label}</span>
            <strong>
              {value === null
                ? "—"
                : value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              <small>{unit}</small>
            </strong>
            <p>
              {value === null
                ? "Awaiting validated outputs"
                : "As supplied in local package"}
            </p>
          </div>
        ))}
      </section>
      <div className="science-grid">
        <section className="science-panel">
          <div className="panel-heading">
            <div>
              <h2>Signal through time</h2>
              <p>
                {study.status === "synthetic"
                  ? "Illustrative values · not a NISAR time series"
                  : "Supplied sample-region summary · not sampled from this map"}
              </p>
            </div>
            <span className="data-badge">
              {study.status === "synthetic" ? "Synthetic" : "Supplied"} · dB
            </span>
          </div>
          <Suspense
            fallback={
              <div className="signal-chart" role="status">
                Loading signal chart…
              </div>
            }
          >
            <SignalChart study={study} />
          </Suspense>
          <details className="data-table-details">
            <summary>Read chart values as a table</summary>
            <div className="table-scroll">
              <table>
                <caption>
                  {study.status === "synthetic"
                    ? "Illustrative, synthetic values (dB)"
                    : "Supplied values (dB)"}
                </caption>
                <thead>
                  <tr>
                    <th>Observation</th>
                    <th>Signal (dB)</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {study.observations.map((o) => (
                    <tr key={o.key}>
                      <td>{observationLabel(o)}</td>
                      <td>
                        {study.signalSeries.find(
                          (p) => p.observationKey === o.key,
                        )?.valueDb ?? "Unavailable"}
                      </td>
                      <td>{study.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
          <p className="panel-note">
            Missing values stay missing. No interpolation, pixel sampling, or
            analysis is performed in this viewer.
          </p>
        </section>
        <section className="science-panel metadata-panel">
          <div className="panel-heading">
            <div>
              <h2>Observation passport</h2>
              <p>Source lineage, preserved as supplied</p>
            </div>
          </div>
          <label className="field-label">
            Observation
            <select
              value={index}
              onChange={(e) => setIndex(Number(e.target.value))}
            >
              {study.observations.map((o, i) => (
                <option value={i} key={o.key}>
                  {observationLabel(o)}
                </option>
              ))}
            </select>
          </label>
          <dl className="metadata-list">
            {metadata.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value ?? "Not supplied"}</dd>
              </div>
            ))}
          </dl>
          {safeSourceUrl(obs.sourceUrl) ? (
            <a
              className="text-link"
              href={obs.sourceUrl!}
              rel="noreferrer"
              target="_blank"
            >
              Open source record <ExternalLink size={14} />
            </a>
          ) : (
            <p className="control-note">
              No source product link is available for this fixture.
            </p>
          )}
        </section>
      </div>
      <div className="science-grid lower-science">
        <section className="science-panel">
          <div className="panel-heading">
            <h2>Reading a radar signal</h2>
            <Waves size={23} className="cyan" />
          </div>
          <div className="scattering-row">
            <span className="scattering-mark smooth" aria-hidden="true">
              ↘ ＿ ↗
            </span>
            <div>
              <h3>Smooth open water may appear dark</h3>
              <p>
                A smooth surface can reflect radar energy away from the sensor.
                Wind, roughness, geometry, and vegetation can change that
                response.
              </p>
            </div>
          </div>
          <div className="scattering-row">
            <span className="scattering-mark vegetation" aria-hidden="true">
              ↘ ┴ ↖
            </span>
            <div>
              <h3>Brighter doesn’t always mean drier</h3>
              <p>
                Interactions between water and upright vegetation can increase
                the return. Interpretation depends on the available channel and
                scene conditions.
              </p>
            </div>
          </div>
          <p className="panel-note">
            Physical hypotheses, not classifications or proof of a flood.{" "}
            <a
              href="https://science.nasa.gov/mission/nisar/get-to-know-sar/"
              target="_blank"
              rel="noreferrer"
            >
              Read NASA’s SAR introduction <ExternalLink size={12} />
            </a>
          </p>
        </section>
        <section className="science-panel">
          <div className="panel-heading">
            <h2>Evidence & limitations</h2>
            <span className="data-badge">
              {study.status === "synthetic" ? "Unverified" : "As supplied"}
            </span>
          </div>
          <p className="provenance-text">{study.provenance}</p>
          <ul className="limitations">
            {study.limitations.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
          <div className="validation-status">
            <strong>Validation status</strong>
            <span>{study.validationStatus}</span>
          </div>
          <a className="text-link" href="#story">
            Follow the investigation <ArrowRight size={15} />
          </a>
        </section>
      </div>
    </div>
  );
}
