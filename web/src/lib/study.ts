import type { FeatureCollection, Polygon } from "geojson";
import type {
  LayerMode,
  Observation,
  OverlayProperties,
  RasterLayer,
  StudyPackage,
} from "../types/frontend";

export const observationLabel = (o: Observation) =>
  o.acquiredAtUtc
    ? new Intl.DateTimeFormat("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZoneName: "short",
        timeZone: "UTC",
      }).format(new Date(o.acquiredAtUtc))
    : o.label;

export function visibleOverlays(
  study: StudyPackage,
  key: string,
  mode: LayerMode,
): FeatureCollection<Polygon, OverlayProperties> {
  return {
    type: "FeatureCollection",
    features: study.overlays.features.filter((f) => {
      if (mode === "gain") return f.properties.kind === "gain";
      if (mode === "loss") return f.properties.kind === "loss";
      if (mode === "difference") return f.properties.kind !== "stable";
      return (
        f.properties.kind === "no-data" ||
        f.properties.observations.includes(key)
      );
    }),
  };
}

export const colors = (accessible: boolean) => ({
  stable: "#67d4e4",
  gain: accessible ? "#f0b949" : "#e989c5",
  loss: accessible ? "#738fff" : "#e6bb6f",
  "no-data": "#8995a5",
});

export function observationRaster(
  observation: Observation,
  channel?: string,
): RasterLayer | undefined {
  // Never substitute a different polarization when the selected channel is missing.
  if (channel)
    return (
      observation.channels?.find((c) => c.polarization === channel)?.raster ??
      (observation.polarization === channel ? observation.raster : undefined)
    );
  return observation.raster ?? observation.channels?.[0]?.raster;
}
export function availableChannels(observation: Observation): string[] {
  return [
    ...new Set([
      ...(observation.raster && observation.polarization
        ? [observation.polarization]
        : []),
      ...(observation.channels?.map((c) => c.polarization) ?? []),
    ]),
  ];
}

export function downloadFile(name: string, contents: string, type: string) {
  const url = URL.createObjectURL(new Blob([contents], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

const csvCell = (value: unknown) => {
  const text =
    typeof value === "string" && /^[=+\-@\t\r]/.test(value)
      ? `'${value}`
      : String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
};
export function summaryCsv(study: StudyPackage) {
  const header = [
    "data_status",
    "observation",
    "acquired_at_utc",
    "product_id",
    "polarization",
    "processing_release",
    "crs",
    "illustrative_or_supplied_signal_db",
    "provenance",
  ];
  return [
    header,
    ...study.observations.map((o) => [
      study.status,
      o.label,
      o.acquiredAtUtc,
      o.productId,
      o.polarization,
      o.processingRelease,
      o.crs,
      study.signalSeries.find((p) => p.observationKey === o.key)?.valueDb,
      study.provenance,
    ]),
  ]
    .map((row) => row.map(csvCell).join(","))
    .join("\r\n");
}
