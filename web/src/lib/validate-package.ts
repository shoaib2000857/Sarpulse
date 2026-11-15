import type { StudyPackage } from "../types/frontend";

const fail = (message: string): never => {
  throw new Error(message);
};
const record = (v: unknown): Record<string, unknown> =>
  v !== null && typeof v === "object" && !Array.isArray(v)
    ? (v as Record<string, unknown>)
    : fail("Expected a JSON object.");
const str = (v: unknown, name: string) =>
  typeof v === "string" && v.trim().length > 0 && v.length <= 12000
    ? v
    : fail(`${name} must be nonempty text.`);
const finite = (v: unknown): v is number =>
  typeof v === "number" && Number.isFinite(v);
const textOrNull = (v: unknown, name: string) =>
  v === null || (str(v, name), true);
export function safeSourceUrl(v: unknown): v is string {
  if (typeof v !== "string") return false;
  try {
    const url = new URL(v);
    return url.protocol === "https:" && !url.username && !url.password;
  } catch {
    return false;
  }
}
function validTile(v: unknown): boolean {
  if (
    typeof v !== "string" ||
    !["{z}", "{x}", "{y}"].every((p) => v.includes(p))
  )
    return false;
  if (v.startsWith("/") && !v.startsWith("//")) return true;
  try {
    const u = new URL(v);
    return (
      u.protocol === "https:" ||
      (u.protocol === "http:" &&
        ["localhost", "127.0.0.1", "[::1]"].includes(u.hostname))
    );
  } catch {
    return false;
  }
}
function raster(v: unknown) {
  const r = record(v);
  str(r.attribution, "Raster attribution");
  if (r.image !== undefined) {
    const image = record(r.image);
    const url = str(image.url, "Raster image URL");
    if (!((url.startsWith("/") && !url.startsWith("//")) || safeSourceUrl(url) || /^http:\/\/(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?\//.test(url)))
      fail("Raster images require HTTPS or a local URL.");
    if (!Array.isArray(image.coordinates) || image.coordinates.length !== 4 || !image.coordinates.every(p =>
      Array.isArray(p) && p.length === 2 && p.every(finite) && Math.abs(p[0]) <= 180 && Math.abs(p[1]) <= 85))
      fail("Raster images require four valid geographic corners.");
  } else if (
    !Array.isArray(r.tiles) ||
    !r.tiles.length ||
    r.tiles.length > 8 ||
    !r.tiles.every(validTile)
  )
    fail("Raster tiles need safe XYZ templates containing {z}, {x}, {y}.");
  if (!finite(r.minDb) || !finite(r.maxDb) || r.minDb >= r.maxDb)
    fail("Raster display range must be increasing dB values.");
}
function polygon(v: unknown) {
  const f = record(v);
  const g = record(f.geometry);
  if (
    f.type !== "Feature" ||
    g.type !== "Polygon" ||
    !Array.isArray(g.coordinates) ||
    !g.coordinates.length
  )
    fail("Geometry must be a GeoJSON Polygon feature.");
  let points = 0;
  for (const ring of g.coordinates as unknown[]) {
    if (!Array.isArray(ring) || ring.length < 4)
      throw new Error("Polygon rings need at least four coordinates.");
    for (const p of ring) {
      if (
        !Array.isArray(p) ||
        p.length !== 2 ||
        !p.every(finite) ||
        Math.abs(p[0]) > 180 ||
        Math.abs(p[1]) > 85
      )
        fail(
          "Polygon coordinates must be longitude/latitude in EPSG:4326 (latitude within ±85°).",
        );
      if (++points > 20000) fail("Polygon exceeds the frontend vertex limit.");
    }
    if (JSON.stringify(ring[0]) !== JSON.stringify(ring[ring.length - 1]))
      fail("Polygon rings must be closed.");
  }
}

export function parseStudyPackage(input: unknown): StudyPackage {
  const p = record(input);
  if (
    p.schemaVersion !== 1 ||
    !["synthetic", "provided"].includes(String(p.status))
  )
    fail("Unsupported package version or data status.");
  ["title", "region", "description", "provenance", "validationStatus"].forEach(
    (k) => str(p[k], k),
  );
  if (
    !Array.isArray(p.bounds) ||
    p.bounds.length !== 4 ||
    !p.bounds.every(finite)
  )
    fail("Bounds must contain west, south, east, north.");
  const [w, s, e, n] = p.bounds as number[];
  if (!(w >= -180 && w < e && e <= 180 && s >= -85 && s < n && n <= 85))
    fail(
      "Bounds are invalid or cross the antimeridian, which this viewer does not support.",
    );
  if (
    !Array.isArray(p.center) ||
    p.center.length !== 2 ||
    !p.center.every(finite) ||
    p.center[0] < w ||
    p.center[0] > e ||
    p.center[1] < s ||
    p.center[1] > n
  )
    fail("Center must be inside bounds.");
  polygon(p.footprint);
  if (
    !Array.isArray(p.observations) ||
    p.observations.length < 2 ||
    p.observations.length > 100
  )
    fail("Provide between 2 and 100 observations.");
  const keys = new Set<string>();
  for (const entry of p.observations as unknown[]) {
    const o = record(entry);
    const key = str(o.key, "Observation key");
    str(o.label, "Observation label");
    if (keys.has(key)) fail("Observation keys must be unique.");
    keys.add(key);
    [
      "productId",
      "polarization",
      "processingRelease",
      "maturity",
      "crs",
      "sourceUrl",
      "acquiredAtUtc",
    ].forEach((k) => textOrNull(o[k], k));
    if (
      o.acquiredAtUtc !== null &&
      (typeof o.acquiredAtUtc !== "string" ||
        !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(o.acquiredAtUtc) ||
        !Number.isFinite(Date.parse(o.acquiredAtUtc)))
    )
      fail("Acquisition timestamps must be valid UTC ISO strings.");
    if (o.sourceUrl !== null && !safeSourceUrl(o.sourceUrl))
      fail("Source links must be HTTPS URLs.");
    if (
      o.pixelSpacingM !== null &&
      (!finite(o.pixelSpacingM) || o.pixelSpacingM <= 0)
    )
      fail("Pixel spacing must be positive metres or null.");
    if (
      p.status === "provided" &&
      [
        "productId",
        "polarization",
        "processingRelease",
        "maturity",
        "crs",
        "sourceUrl",
        "acquiredAtUtc",
        "pixelSpacingM",
      ].some((k) => o[k] === null)
    )
      fail(
        "Supplied observations require full source, UTC, polarization, release, maturity, CRS and spacing metadata.",
      );
    if (o.raster !== undefined) raster(o.raster);
    if (o.channels !== undefined) {
      if (!Array.isArray(o.channels) || o.channels.length > 12)
        fail("Channels must contain at most 12 supplied polarization layers.");
      const names = new Set<string>();
      for (const channel of o.channels as unknown[]) {
        const c = record(channel);
        const name = str(c.polarization, "Channel polarization");
        if (names.has(name)) fail("Channel polarizations must be unique.");
        names.add(name);
        raster(c.raster);
      }
    }
  }
  const overlays = record(p.overlays);
  if (
    overlays.type !== "FeatureCollection" ||
    !Array.isArray(overlays.features) ||
    overlays.features.length > 1000
  )
    fail("Overlays must be a GeoJSON collection of at most 1,000 polygons.");
  for (const f of overlays.features as unknown[]) {
    polygon(f);
    const props = record(record(f).properties);
    str(props.label, "Overlay label");
    if (!["stable", "gain", "loss", "no-data"].includes(String(props.kind)))
      fail("Unknown overlay class.");
    if (
      !Array.isArray(props.observations) ||
      !props.observations.every((k) => typeof k === "string" && keys.has(k))
    )
      fail("Overlay references an unknown observation.");
  }
  const stats = record(p.statistics);
  for (const k of [
    "validAreaKm2",
    "gainedWaterKm2",
    "lostWaterKm2",
    "changedSharePct",
  ]) {
    if (stats[k] !== null && (!finite(stats[k]) || (stats[k] as number) < 0))
      fail("Statistics must be nonnegative numbers or null.");
  }
  if (finite(stats.changedSharePct) && stats.changedSharePct > 100)
    fail("Changed share cannot exceed 100%.");
  if (p.status === "synthetic" && Object.values(stats).some((v) => v !== null))
    fail("Synthetic packages cannot report scientific area statistics.");
  if (!Array.isArray(p.signalSeries) || p.signalSeries.length > 100)
    fail("Signal series must be an array with at most 100 points.");
  const signalKeys = new Set();
  for (const point of p.signalSeries as unknown[]) {
    const q = record(point);
    if (
      !keys.has(String(q.observationKey)) ||
      signalKeys.has(q.observationKey) ||
      (q.valueDb !== null && !finite(q.valueDb))
    )
      fail(
        "Signal points need unique known observation keys and finite dB values or null.",
      );
    signalKeys.add(q.observationKey);
  }
  if (
    !Array.isArray(p.limitations) ||
    p.limitations.length === 0 ||
    p.limitations.length > 100
  )
    fail("Provide at least one limitation.");
  (p.limitations as unknown[]).forEach((v) => str(v, "Limitation"));
  return p as unknown as StudyPackage;
}
