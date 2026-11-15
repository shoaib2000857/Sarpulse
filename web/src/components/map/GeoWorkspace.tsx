import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import { type Map as GLMap, type StyleSpecification } from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import Compare from "@maplibre/maplibre-gl-compare";
import "@maplibre/maplibre-gl-compare/dist/maplibre-gl-compare.css";
import { Crosshair, Minus, Plus, RotateCcw, TriangleAlert } from "lucide-react";
import { Button } from "../ui/button";
import {
  colors,
  observationLabel,
  observationRaster,
  visibleOverlays,
} from "../../lib/study";
import type { Basemap, GeoWorkspaceProps } from "../../types/frontend";

// MapLibre 6 ships a separate worker; keep it on the same origin in dev and builds.
maplibregl.setWorkerUrl(workerUrl);

export default function GeoWorkspace(props: GeoWorkspaceProps) {
  const {
    study,
    observationKey,
    beforeKey,
    mode,
    compare,
    opacity,
    palette,
    basemap,
    camera,
    showFootprint,
    channel,
    onInspect,
  } = props;
  const root = useRef<HTMLDivElement>(null);
  const beforeNode = useRef<HTMLDivElement>(null);
  const afterNode = useRef<HTMLDivElement>(null);
  const maps = useRef<GLMap[]>([]);
  const comparison = useRef<Compare | null>(null);
  const latest = useRef(props);
  latest.current = props;
  const [status, setStatus] = useState<"loading" | "ready" | "unavailable">(
    "loading",
  );
  const [tileError, setTileError] = useState(false);
  const [split, setSplit] = useState(50);

  useEffect(() => {
    if (!beforeNode.current || !afterNode.current || !root.current) return;
    setStatus("loading");
    setTileError(false);
    const nodes = compare
      ? [beforeNode.current, afterNode.current]
      : [afterNode.current];
    const created: GLMap[] = [];
    let readyMaps = 0;
    const style: StyleSpecification = {
      version: 8,
      sources: {},
      layers: [
        {
          id: "background",
          type: "background",
          paint: { "background-color": "#06090d" },
        },
      ],
    };
    try {
      for (const node of nodes) {
        const map = new maplibregl.Map({
          container: node,
          style: structuredClone(style),
          center: study.center,
          zoom: 10.5,
          bounds: [
            [study.bounds[0], study.bounds[1]],
            [study.bounds[2], study.bounds[3]],
          ],
          fitBoundsOptions: { padding: 54 },
          attributionControl: false,
          dragRotate: false,
          pitchWithRotate: false,
          maxPitch: latest.current.camera ? 60 : 0,
        });
        map.addControl(
          new maplibregl.AttributionControl({ compact: true }),
          "bottom-right",
        );
        map.addControl(
          new maplibregl.ScaleControl({ unit: "metric", maxWidth: 110 }),
          "bottom-left",
        );
        map.on("error", (event) => {
          if (/WebGL|Worker failed/.test(event.error?.message ?? ""))
            setStatus("unavailable");
          else setTileError(true);
        });
        map.on("load", () => {
          updateMap(map, latest.current, compare && map === created[0]);
          applyCamera(map, latest.current, false);
          collapseAttribution(node);
          map.once("idle", () => {
            if (++readyMaps === nodes.length) setStatus("ready");
          });
        });
        map.on("click", (event) => {
          const features = map.getLayer("cells")
            ? map.queryRenderedFeatures(event.point, { layers: ["cells"] })
            : [];
          const p = features[0]?.properties;
          latest.current.onInspect?.({
            longitude: event.lngLat.lng,
            latitude: event.lngLat.lat,
            label: p?.label ?? "Map location",
            kind: p?.kind ?? null,
          });
        });
        map
          .getCanvas()
          .setAttribute(
            "aria-label",
            compare && created.length === 0
              ? "Before geographic map"
              : "Interactive geographic map",
          );
        created.push(map);
      }
      maps.current = created;
      if (compare) {
        comparison.current = new Compare(created[0], created[1], root.current, {
          orientation: "vertical",
        });
        comparison.current.setSlider(root.current.clientWidth / 2);
        comparison.current.on(
          "slideend",
          ({ currentPosition }: { currentPosition: number }) => {
            if (root.current)
              setSplit(
                Math.round((currentPosition / root.current.clientWidth) * 100),
              );
          },
        );
      }
    } catch {
      setStatus("unavailable");
    }
    let previousWidth = root.current.clientWidth;
    const resize = new ResizeObserver(() => {
      const width = root.current?.clientWidth ?? previousWidth;
      const fraction = comparison.current
        ? comparison.current.currentPosition / Math.max(previousWidth, 1)
        : 0.5;
      created.forEach((map) => map.resize());
      comparison.current?.setSlider(width * fraction);
      previousWidth = width;
    });
    resize.observe(root.current);
    return () => {
      resize.disconnect();
      comparison.current?.remove();
      comparison.current = null;
      created.forEach((map) => map.remove());
      maps.current = [];
    };
  }, [study, compare]);

  useEffect(() => {
    setTileError(false);
    maps.current.forEach((map, i) => {
      if (map.getLayer("background")) updateMap(map, props, compare && i === 0);
    });
  }, [
    observationKey,
    beforeKey,
    mode,
    opacity,
    palette,
    basemap,
    showFootprint,
    channel,
    study,
    compare,
  ]); // Map state changes without recreating its camera.

  useEffect(() => {
    const map = maps.current[0];
    // loaded() is false while tiles stream in, so test for the style's own layer.
    if (map?.getLayer("background")) applyCamera(map, props, true);
  }, [camera?.zoomOffset, camera?.pitch, camera?.bearing]);

  const obs = study.observations.find((o) => o.key === observationKey)!;
  const baseline = study.observations.find((o) => o.key === beforeKey)!;
  const reset = () =>
    maps.current[0]?.fitBounds(
      [
        [study.bounds[0], study.bounds[1]],
        [study.bounds[2], study.bounds[3]],
      ],
      {
        padding: 54,
        duration: window.matchMedia("(prefers-reduced-motion: reduce)").matches
          ? 0
          : 500,
      },
    );
  const c = colors(palette === "accessible");
  return (
    <div className="geo-workspace" data-map-status={status}>
      <div className="map-canvas-group" ref={root}>
        <div className="map-instance" ref={beforeNode} hidden={!compare} />
        <div className="map-instance" ref={afterNode} />
      </div>
      <div className="map-topline">
        <span className="map-location">
          <Crosshair size={14} /> {study.region}
        </span>
        <span className="map-north" aria-label="North up">
          N ↑
        </span>
      </div>
      <div className="map-date-labels">
        {compare && <span>Before · {observationLabel(baseline)}</span>}
        <span>
          {compare ? "After" : mode === "before" ? "Before" : "View"} ·{" "}
          {observationLabel(mode === "before" && !compare ? baseline : obs)}
        </span>
      </div>
      <div className="map-tools">
        <Button
          size="icon"
          variant="outline"
          aria-label="Zoom in"
          onClick={() => maps.current[0]?.zoomIn()}
        >
          <Plus size={17} />
        </Button>
        <Button
          size="icon"
          variant="outline"
          aria-label="Zoom out"
          onClick={() => maps.current[0]?.zoomOut()}
        >
          <Minus size={17} />
        </Button>
        <Button
          size="icon"
          variant="outline"
          aria-label="Reset map extent"
          onClick={reset}
        >
          <RotateCcw size={16} />
        </Button>
      </div>
      {status === "loading" && (
        <div className="map-message" role="status">
          Opening geographic workspace…
        </div>
      )}
      {status === "unavailable" && (
        <div className="map-message">
          <TriangleAlert />
          <h3>Map rendering is unavailable</h3>
          <p>
            The geographic renderer could not start. Use the controls and
            geometry list below, reload the page, or try a WebGL-enabled
            browser.
          </p>
          <ul>
            {study.overlays.features.map((f) => (
              <li key={f.properties.label}>
                <button
                  onClick={() =>
                    onInspect?.({
                      longitude: f.geometry.coordinates[0][0][0],
                      latitude: f.geometry.coordinates[0][0][1],
                      label: f.properties.label,
                      kind: f.properties.kind,
                    })
                  }
                >
                  {f.properties.label} · {f.properties.kind}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      {tileError && status !== "unavailable" && (
        <div className="tile-warning" role="status">
          Some map resources could not load. Local geometry remains available;
          retry by toggling context or the observation.
        </div>
      )}
      <div className="map-caption">
        <span className="status-dot" />
        {study.status === "synthetic"
          ? "Schematic test cells · not observed change"
          : "Supplied layers · see provenance in Science Lab"}
        {basemapNote[basemap] && <em> · {basemapNote[basemap]}</em>}
      </div>
      <div className="map-legend" aria-label="Map legend">
        {Object.entries(c).map(([key, color]) => (
          <span key={key}>
            <i style={{ background: color }} />
            {key === "stable"
              ? "Persistent / ●"
              : key === "gain"
                ? "Gain / +"
                : key === "loss"
                  ? "Loss / −"
                  : "No data / ×"}
          </span>
        ))}
      </div>
      {compare && (
        <label className="compare-keyboard">
          Comparison divider{" "}
          <input
            aria-label="Comparison divider"
            type="range"
            min="0"
            max="100"
            value={split}
            onChange={(event) => {
              const value = Number(event.target.value);
              setSplit(value);
              comparison.current?.setSlider(
                ((root.current?.clientWidth ?? 0) * value) / 100,
              );
            }}
          />
          <output>{split}%</output>
        </label>
      )}
      {study.status === "synthetic" && (
        <div className="map-watermark">SYNTHETIC / DEMO</div>
      )}
    </div>
  );
}

/** Start the credit control collapsed (its "i" button still opens it). */
export function collapseAttribution(container: HTMLElement) {
  const el = container.querySelector(".maplibregl-ctrl-attrib");
  el?.classList.remove("maplibregl-compact-show");
  el?.removeAttribute("open");
}
const basemapNote: Record<Basemap, string> = {
  satellite: "basemap: optical context imagery, not SAR",
  dark: "basemap: reference map, not SAR",
  streets: "basemap: reference map, not SAR",
  none: "",
};
const basemaps: Record<
  Exclude<Basemap, "none">,
  { tiles: string[]; maxzoom: number; attribution: string; paint: object }
> = {
  satellite: {
    tiles: [
      "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg",
    ],
    maxzoom: 13,
    attribution:
      '<a href="https://s2maps.eu">Sentinel-2 cloudless</a> by EOX IT Services GmbH (contains modified Copernicus Sentinel data 2016) · optical context, not NISAR',
    paint: { "raster-brightness-max": 0.72, "raster-saturation": -0.15 },
  },
  // OpenStreetMap tiles, desaturated and tone-inverted by the renderer. No API key.
  dark: {
    tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
    maxzoom: 19,
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · geographic context, not NISAR',
    paint: {
      "raster-saturation": -1,
      "raster-brightness-min": 0.6,
      "raster-brightness-max": 0.03,
      "raster-contrast": 0.15,
    },
  },
  streets: {
    tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
    maxzoom: 19,
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · geographic context, not NISAR',
    paint: { "raster-opacity": 0.55, "raster-saturation": -0.8 },
  },
};

function applyCamera(map: GLMap, p: GeoWorkspaceProps, animate: boolean) {
  if (!p.camera) return;
  const [w, s, e, n] = p.study.bounds;
  const fitted = map.cameraForBounds(
    [
      [w, s],
      [e, n],
    ],
    { padding: 54 },
  );
  if (!fitted?.center || fitted.zoom === undefined) return;
  const target = {
    center: fitted.center,
    zoom: Math.max(1, fitted.zoom + (p.camera.zoomOffset ?? 0)),
    pitch: p.camera.pitch ?? 0,
    bearing: p.camera.bearing ?? 0,
  };
  if (animate && !window.matchMedia("(prefers-reduced-motion: reduce)").matches)
    map.flyTo({ ...target, duration: 2200, essential: false });
  else map.jumpTo(target);
}

function updateMap(map: GLMap, p: GeoWorkspaceProps, isBefore: boolean) {
  const { study, mode, opacity, palette, showFootprint } = p;
  const key = isBefore || mode === "before" ? p.beforeKey : p.observationKey;
  const observation = study.observations.find((o) => o.key === key)!;
  for (const [name, b] of Object.entries(basemaps)) {
    const id = `basemap-${name}`;
    // Sources are added lazily so an unused tile service is never contacted.
    if (name === p.basemap && !map.getSource(id)) {
      map.addSource(id, {
        type: "raster",
        tiles: b.tiles,
        tileSize: 256,
        maxzoom: b.maxzoom,
        attribution: b.attribution,
      });
      map.addLayer(
        { id, type: "raster", source: id, paint: b.paint },
        map.getLayer("grid") ? "grid" : undefined,
      );
    }
    if (map.getLayer(id))
      map.setLayoutProperty(
        id,
        "visibility",
        name === p.basemap ? "visible" : "none",
      );
  }
  if (!map.getSource("grid")) {
    const [w, s, e, n] = study.bounds;
    const features = [];
    for (let i = 0; i <= 8; i++) {
      const x = w + ((e - w) * i) / 8,
        y = s + ((n - s) * i) / 8;
      features.push({
        type: "Feature" as const,
        properties: {},
        geometry: {
          type: "LineString" as const,
          coordinates: [
            [x, s],
            [x, n],
          ],
        },
      });
      features.push({
        type: "Feature" as const,
        properties: {},
        geometry: {
          type: "LineString" as const,
          coordinates: [
            [w, y],
            [e, y],
          ],
        },
      });
    }
    map.addSource("grid", {
      type: "geojson",
      data: { type: "FeatureCollection", features },
    });
    map.addLayer({
      id: "grid",
      type: "line",
      source: "grid",
      paint: {
        "line-color": "#7294a8",
        "line-width": 0.6,
        "line-opacity": 0.2,
      },
    });
    map.addSource("footprint", { type: "geojson", data: study.footprint });
    map.addLayer({
      id: "footprint",
      type: "line",
      source: "footprint",
      paint: {
        "line-color": "#b1c4ce",
        "line-width": 1.3,
        "line-dasharray": [5, 4],
      },
    });
  }
  map.setLayoutProperty(
    "footprint",
    "visibility",
    showFootprint ? "visible" : "none",
  );
  const data = visibleOverlays(study, key, isBefore ? "before" : mode);
  const c = colors(palette === "accessible");
  if (!map.getSource("cells")) {
    map.addSource("cells", { type: "geojson", data });
    map.addLayer({ id: "cells", type: "fill", source: "cells" });
    map.addLayer({
      id: "cell-lines",
      type: "line",
      source: "cells",
      paint: { "line-color": "#ecf5fb", "line-opacity": 0.7, "line-width": 1 },
    });
    for (const [name, symbol] of Object.entries({
      gain: "+",
      loss: "−",
      "no-data": "×",
      stable: "·",
    })) {
      const canvas = document.createElement("canvas");
      canvas.width = 20;
      canvas.height = 20;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        ctx.fillStyle = "#0b1525";
        ctx.font = "bold 16px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(symbol, 10, 10);
        map.addImage(`pattern-${name}`, ctx.getImageData(0, 0, 20, 20));
      }
    }
    map.addLayer({
      id: "cell-patterns",
      type: "fill",
      source: "cells",
      paint: {
        "fill-pattern": ["concat", "pattern-", ["get", "kind"]],
        "fill-opacity": 0.6,
      },
    });
  } else (map.getSource("cells") as maplibregl.GeoJSONSource).setData(data);
  map.setPaintProperty("cells", "fill-color", [
    "match",
    ["get", "kind"],
    "gain",
    c.gain,
    "loss",
    c.loss,
    "no-data",
    c["no-data"],
    c.stable,
  ]);
  map.setPaintProperty("cells", "fill-opacity", opacity);
  map.setPaintProperty("cell-patterns", "fill-opacity", opacity * 0.75);
  if (map.getLayer("radar")) map.removeLayer("radar");
  if (map.getSource("radar")) map.removeSource("radar");
  const raster = observationRaster(observation, p.channel);
  const tiles = raster?.tiles ?? [];
  if (tiles.length && (isBefore || mode === "before" || mode === "after")) {
    map.addSource("radar", {
      type: "raster",
      tiles,
      tileSize: 256,
      bounds: study.bounds,
      attribution: raster!.attribution
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;"),
    });
    map.addLayer(
      {
        id: "radar",
        type: "raster",
        source: "radar",
        paint: { "raster-opacity": opacity, "raster-fade-duration": 0 },
      },
      "cells",
    );
  }
}
