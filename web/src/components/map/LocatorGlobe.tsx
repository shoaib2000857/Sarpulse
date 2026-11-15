import { useEffect, useRef, useState } from "react";
import * as maplibregl from "maplibre-gl";
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?url";
import type { StudyPackage } from "../../types/frontend";

maplibregl.setWorkerUrl(workerUrl);

const format = (v: number, pos: string, neg: string) =>
  `${Math.abs(v).toFixed(2)}° ${v < 0 ? neg : pos}`;

/** Small globe showing where the study extent sits on Earth. Context only. */
export default function LocatorGlobe({ study }: { study: StudyPackage }) {
  const node = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "unavailable">(
    "loading",
  );
  useEffect(() => {
    if (!node.current) return;
    let map: maplibregl.Map;
    try {
      map = new maplibregl.Map({
        container: node.current,
        center: study.center,
        zoom: 1.6,
        attributionControl: false,
        scrollZoom: false,
        dragRotate: false,
        style: {
          version: 8,
          projection: { type: "globe" },
          sky: { "atmosphere-blend": 0.7 },
          sources: {
            base: {
              type: "raster",
              tiles: [
                "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg",
              ],
              tileSize: 256,
              maxzoom: 13,
              attribution:
                '<a href="https://s2maps.eu">Sentinel-2 cloudless</a> by EOX IT Services GmbH (contains modified Copernicus Sentinel data 2016) · optical context, not NISAR',
            },
            extent: { type: "geojson", data: study.footprint },
          },
          layers: [
            {
              id: "bg",
              type: "background",
              paint: { "background-color": "#0a1420" },
            },
            {
              id: "base",
              type: "raster",
              source: "base",
              paint: { "raster-brightness-max": 0.85 },
            },
            {
              id: "extent",
              type: "line",
              source: "extent",
              paint: { "line-color": "#00a1ff", "line-width": 1.5 },
            },
          ],
        },
      });
    } catch {
      setStatus("unavailable");
      return;
    }
    map.addControl(new maplibregl.AttributionControl({ compact: true }));
    const dot = document.createElement("span");
    dot.className = "locator-dot";
    new maplibregl.Marker({ element: dot }).setLngLat(study.center).addTo(map);
    map.on("error", (e) => {
      if (/WebGL|Worker failed/.test(e.error?.message ?? ""))
        setStatus("unavailable");
    });
    map.on("load", () => {
      setStatus("ready");
      const el = node.current?.querySelector(".maplibregl-ctrl-attrib");
      el?.classList.remove("maplibregl-compact-show");
      el?.removeAttribute("open");
    });
    map.getCanvas().setAttribute("aria-hidden", "true");
    return () => map.remove();
  }, [study]);
  return (
    <div className="locator-globe" data-globe-status={status}>
      <div
        className="locator-globe-map"
        ref={node}
        role="img"
        aria-label={`Globe locating ${study.title} at ${format(study.center[1], "N", "S")}, ${format(study.center[0], "E", "W")}`}
      />
      {status === "unavailable" && (
        <p className="locator-fallback">Globe unavailable in this browser.</p>
      )}
      <dl className="locator-facts">
        <div>
          <dt>Centre</dt>
          <dd>
            {format(study.center[1], "N", "S")},{" "}
            {format(study.center[0], "E", "W")}
          </dd>
        </div>
        <div>
          <dt>Extent (W, S, E, N)</dt>
          <dd>{study.bounds.map((b) => b.toFixed(2)).join(", ")}</dd>
        </div>
        <div>
          <dt>Coordinate CRS</dt>
          <dd>EPSG:4326</dd>
        </div>
      </dl>
    </div>
  );
}
