import { useEffect, useState } from "react";
import {
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Download,
  Info,
  Layers,
  MapPin,
  Pause,
  Play,
  SlidersHorizontal,
  SplitSquareHorizontal,
} from "lucide-react";
import GeoWorkspace from "../components/map/GeoWorkspace";
import { Button } from "../components/ui/button";
import {
  availableChannels,
  downloadFile,
  observationLabel,
  observationRaster,
  visibleOverlays,
} from "../lib/study";
import type {
  LayerMode,
  MapSelection,
  Palette,
  StudyPackage,
} from "../types/frontend";

const modes: { key: LayerMode; label: string; detail: string }[] = [
  { key: "after", label: "After", detail: "Selected observation" },
  { key: "before", label: "Before", detail: "Reference observation" },
  {
    key: "difference",
    label: "Change classes",
    detail: "Fixed package classification",
  },
  { key: "gain", label: "Water gained", detail: "Supplied gain geometry" },
  { key: "loss", label: "Water lost", detail: "Supplied loss geometry" },
];
export default function Explorer({ study }: { study: StudyPackage }) {
  const [index, setIndex] = useState(1);
  const [beforeIndex, setBeforeIndex] = useState(0);
  const [mode, setMode] = useState<LayerMode>("after");
  const [compare, setCompare] = useState(false);
  const [opacity, setOpacity] = useState(0.8);
  const [palette, setPalette] = useState<Palette>("standard");
  const [channel, setChannel] = useState("");
  const [contextMap, setContextMap] = useState(false);
  const [footprint, setFootprint] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [selection, setSelection] = useState<MapSelection | null>(null);
  const [tab, setTab] = useState<"layers" | "inspect">("layers");
  const [exported, setExported] = useState(false);
  const obs = study.observations[index],
    baseline = study.observations[beforeIndex];
  const channels = availableChannels(obs),
    selectedRaster = observationRaster(obs, channel || undefined);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(
      () =>
        setIndex((i) => {
          if (i >= study.observations.length - 1) {
            setPlaying(false);
            return i;
          }
          return i + 1;
        }),
      1500,
    );
    return () => window.clearInterval(timer);
  }, [playing, study.observations.length]);
  useEffect(() => {
    if (index === beforeIndex) setCompare(false);
  }, [index, beforeIndex]);
  const selectIndex = (i: number) => {
    setIndex(i);
    setPlaying(false);
  };
  const exportGeometry = () => {
    downloadFile(
      `sarpulse-${study.status}-visible.geojson`,
      JSON.stringify(
        {
          ...visibleOverlays(
            study,
            mode === "before" ? baseline.key : obs.key,
            mode,
          ),
          dataStatus: study.status,
          provenance: study.provenance,
          classificationScope:
            "Fixed supplied package; not recalculated for selected dates.",
        },
        null,
        2,
      ),
      "application/geo+json",
    );
    setExported(true);
  };
  return (
    <div className="explorer-page">
      <div className="workspace-heading">
        <div>
          <span className="section-kicker">Geographic workspace</span>
          <h1>{study.title}</h1>
          <p>{study.region}</p>
        </div>
        <div className="workspace-heading-actions">
          <Button variant="outline" size="sm" onClick={exportGeometry}>
            <Download size={15} />
            Export visible GeoJSON
          </Button>
          <Button asChild variant="ghost" size="sm">
            <a href="#science">
              Inspect evidence <ArrowRight size={15} />
            </a>
          </Button>
        </div>
      </div>
      {exported && (
        <p role="status" className="export-notice">
          Exported visible geometry with {study.status} status and provenance.
        </p>
      )}
      <div className="explorer-grid">
        <aside className="control-panel" aria-label="Explorer controls">
          <div className="panel-tabs">
            <button
              aria-pressed={tab === "layers"}
              onClick={() => setTab("layers")}
            >
              <Layers size={15} />
              Layers
            </button>
            <button
              aria-pressed={tab === "inspect"}
              onClick={() => setTab("inspect")}
            >
              <MapPin size={15} />
              Inspect
            </button>
          </div>
          {tab === "layers" ? (
            <>
              <section className="control-section">
                <h2>Observation view</h2>
                <div className="layer-list">
                  {modes.map((m) => (
                    <label
                      className={
                        mode === m.key
                          ? "layer-option selected"
                          : "layer-option"
                      }
                      key={m.key}
                    >
                      <input
                        type="radio"
                        name="map-layer"
                        value={m.key}
                        checked={mode === m.key}
                        onChange={() => setMode(m.key)}
                      />
                      <span>
                        <strong>{m.label}</strong>
                        <small>{m.detail}</small>
                      </span>
                    </label>
                  ))}
                </div>
                <p className="control-note">
                  {study.status === "synthetic"
                    ? "All classes are schematic test cells."
                    : "Class geometry is precomputed for this package."}{" "}
                  Changing dates does not rerun classification.
                </p>
              </section>
              <section className="control-section">
                <h2>
                  <SlidersHorizontal size={15} />
                  Display
                </h2>
                <label className="range-label">
                  Layer opacity <output>{Math.round(opacity * 100)}%</output>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={Math.round(opacity * 100)}
                    onChange={(e) => setOpacity(Number(e.target.value) / 100)}
                  />
                </label>
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={footprint}
                    onChange={(e) => setFootprint(e.target.checked)}
                  />
                  Show{" "}
                  {study.status === "synthetic"
                    ? "illustrative extent"
                    : "supplied footprint"}
                </label>
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={contextMap}
                    onChange={(e) => setContextMap(e.target.checked)}
                  />
                  OpenStreetMap context{" "}
                  <span className="tiny-label">online</span>
                </label>
                <label className="check-row">
                  <input
                    type="checkbox"
                    checked={palette === "accessible"}
                    onChange={(e) =>
                      setPalette(e.target.checked ? "accessible" : "standard")
                    }
                  />
                  Alternative color palette
                </label>
              </section>
              <section className="control-section">
                <label className="field-label">
                  Radar channel
                  <select
                    value={channel}
                    disabled={channels.length === 0}
                    onChange={(e) => setChannel(e.target.value)}
                  >
                    <option value="">
                      {channels.length
                        ? "Default supplied channel"
                        : "No channels supplied"}
                    </option>
                    {[
                      ...new Set([...channels, ...(channel ? [channel] : [])]),
                    ].map((c) => (
                      <option value={c} key={c}>
                        {c}
                        {!channels.includes(c)
                          ? " (unavailable on this date)"
                          : ""}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="raster-state">
                  <Info size={16} />
                  <p>
                    {selectedRaster
                      ? `Supplied radar tiles · ${channel || obs.polarization || "channel unspecified"} · ${selectedRaster.minDb} to ${selectedRaster.maxDb} dB`
                      : "Radar raster unavailable. No COG or TiTiler tile URL has been supplied for this observation and channel."}
                  </p>
                </div>
                {compare &&
                  !observationRaster(baseline, channel || undefined) && (
                    <p className="control-note">
                      The before view has no supplied raster for this channel.
                    </p>
                  )}
              </section>
            </>
          ) : (
            <section className="control-section inspect-section">
              <h2>Geographic inspection</h2>
              <p>
                Click the map to inspect a location, or select a visible cell
                below.
              </p>
              {selection ? (
                <div className="inspection-result" aria-live="polite">
                  <strong>{selection.label}</strong>
                  <dl>
                    <dt>Longitude</dt>
                    <dd>
                      {Math.abs(selection.longitude).toFixed(5)}°{" "}
                      {selection.longitude < 0 ? "W" : "E"}
                    </dd>
                    <dt>Latitude</dt>
                    <dd>
                      {Math.abs(selection.latitude).toFixed(5)}°{" "}
                      {selection.latitude < 0 ? "S" : "N"}
                    </dd>
                    <dt>Coordinate CRS</dt>
                    <dd>EPSG:4326</dd>
                    <dt>Class</dt>
                    <dd>{selection.kind ?? "No feature selected"}</dd>
                    <dt>Pixel intensity</dt>
                    <dd>Not sampled</dd>
                  </dl>
                  <p>
                    {study.status === "synthetic"
                      ? "Synthetic geometry. These coordinates do not identify a measured radar pixel."
                      : "Coordinates and supplied class only. Pixel measurements are not exposed by the tile renderer."}
                  </p>
                </div>
              ) : (
                <div className="empty-inspection">
                  <MapPin />
                  <span>No location selected</span>
                </div>
              )}
              <div className="cell-list">
                {visibleOverlays(
                  study,
                  mode === "before" ? baseline.key : obs.key,
                  mode,
                ).features.map((f) => (
                  <button
                    key={f.properties.label}
                    onClick={() =>
                      setSelection({
                        label: f.properties.label,
                        kind: f.properties.kind,
                        longitude: f.geometry.coordinates[0][0][0],
                        latitude: f.geometry.coordinates[0][0][1],
                      })
                    }
                  >
                    {f.properties.label}
                    <ChevronRight size={13} />
                  </button>
                ))}
              </div>
            </section>
          )}
          <a className="panel-evidence-link" href="#science">
            Source metadata & limitations <ArrowRight size={14} />
          </a>
        </aside>
        <div className="map-column">
          <div className="map-toolbar">
            <span>
              <span className="status-dot" />
              {study.status === "synthetic"
                ? "Synthetic interface demonstration"
                : "Local package loaded"}
            </span>
            <Button
              variant={compare ? "default" : "outline"}
              size="sm"
              disabled={index === beforeIndex}
              aria-pressed={compare}
              onClick={() => setCompare(!compare)}
            >
              <SplitSquareHorizontal size={15} />
              {compare ? "Exit comparison" : "Compare"}
            </Button>
          </div>
          <GeoWorkspace
            study={study}
            observationKey={obs.key}
            beforeKey={baseline.key}
            mode={mode}
            compare={compare}
            opacity={opacity}
            palette={palette}
            contextMap={contextMap}
            showFootprint={footprint}
            channel={channel || undefined}
            onInspect={(s) => {
              setSelection(s);
              setTab("inspect");
            }}
          />
          <div className="timeline">
            <div className="timeline-heading">
              <div>
                <h2>
                  {study.status === "synthetic"
                    ? "Illustrative sequence"
                    : "Observation timeline"}
                </h2>
                <p>
                  {study.status === "synthetic"
                    ? "Four fictional stages, not acquisition dates."
                    : "Only supplied acquisitions are shown. Missing dates are not interpolated."}
                </p>
              </div>
              <span>
                {index + 1} / {study.observations.length}
              </span>
            </div>
            <div className="timeline-player">
              <Button
                size="icon"
                variant="outline"
                aria-label={playing ? "Pause timeline" : "Play timeline"}
                onClick={() => {
                  if (!playing && index === study.observations.length - 1)
                    setIndex(0);
                  setPlaying(!playing);
                }}
              >
                {playing ? <Pause size={16} /> : <Play size={16} />}
              </Button>
              <div className="timeline-track">
                <input
                  type="range"
                  aria-label="Observation timeline"
                  aria-valuetext={observationLabel(obs)}
                  min="0"
                  max={study.observations.length - 1}
                  step="1"
                  value={index}
                  onChange={(e) => selectIndex(Number(e.target.value))}
                />
                <div className="timeline-ticks">
                  {study.observations.map((o, i) => (
                    <button
                      key={o.key}
                      aria-current={index === i ? "step" : undefined}
                      onClick={() => selectIndex(i)}
                    >
                      {observationLabel(o)}
                    </button>
                  ))}
                </div>
              </div>
              <Button
                size="icon"
                variant="ghost"
                aria-label="Previous observation"
                disabled={index === 0}
                onClick={() => selectIndex(index - 1)}
              >
                <ChevronLeft size={18} />
              </Button>
              <Button
                size="icon"
                variant="ghost"
                aria-label="Next observation"
                disabled={index === study.observations.length - 1}
                onClick={() => selectIndex(index + 1)}
              >
                <ChevronRight size={18} />
              </Button>
            </div>
            <div className="date-selectors">
              <label>
                Before
                <select
                  value={beforeIndex}
                  onChange={(e) => {
                    setBeforeIndex(Number(e.target.value));
                    setPlaying(false);
                  }}
                >
                  {study.observations.map((o, i) => (
                    <option key={o.key} value={i}>
                      {observationLabel(o)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                After
                <select
                  value={index}
                  onChange={(e) => selectIndex(Number(e.target.value))}
                >
                  {study.observations.map((o, i) => (
                    <option key={o.key} value={i}>
                      {observationLabel(o)}
                    </option>
                  ))}
                </select>
              </label>
              {index === beforeIndex && (
                <span className="control-note">
                  Choose different observations to compare.
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
