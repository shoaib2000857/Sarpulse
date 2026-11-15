import { describe, expect, it } from "vitest";
import { demoStudy } from "../src/data/demo";
import {
  observationLabel,
  summaryCsv,
  visibleOverlays,
} from "../src/lib/study";
import { parseStudyPackage } from "../src/lib/validate-package";

describe("frontend data integrity", () => {
  it("keeps synthetic scientific metadata and area statistics unavailable", () => {
    expect(parseStudyPackage(demoStudy)).toBe(demoStudy);
    expect(Object.values(demoStudy.statistics).every((v) => v === null)).toBe(
      true,
    );
    expect(
      demoStudy.observations.every(
        (o) =>
          o.acquiredAtUtc === null &&
          o.productId === null &&
          o.polarization === null &&
          o.processingRelease === null,
      ),
    ).toBe(true);
    expect(demoStudy.provenance).toContain("NOT NASA OBSERVATIONS");
  });
  it("never turns a fixture stage into an acquisition date", () =>
    expect(observationLabel(demoStudy.observations[0])).toBe("Baseline"));
  it("shows only active cells for selected observations and keeps a no-data class", () => {
    const before = visibleOverlays(demoStudy, "fixture-0", "before");
    const after = visibleOverlays(demoStudy, "fixture-1", "after");
    expect(
      before.features.some((f) => f.properties.label === "Test gain A"),
    ).toBe(false);
    expect(
      after.features.some((f) => f.properties.label === "Test gain A"),
    ).toBe(true);
    expect(after.features.some((f) => f.properties.kind === "no-data")).toBe(
      true,
    );
  });
  it("treats change classes as fixed supplied geometry rather than rerunning a detector", () => {
    expect(
      visibleOverlays(demoStudy, "fixture-0", "gain").features.every(
        (f) => f.properties.kind === "gain",
      ),
    ).toBe(true);
    expect(
      visibleOverlays(demoStudy, "fixture-1", "difference").features.some(
        (f) => f.properties.kind === "stable",
      ),
    ).toBe(false);
  });
  it("retains status, units and provenance in exported CSV", () => {
    const csv = summaryCsv(demoStudy);
    expect(csv).toContain("illustrative_or_supplied_signal_db");
    expect(csv).toContain("synthetic");
    expect(csv).toContain("NOT NASA OBSERVATIONS");
    expect(csv).not.toContain("undefined");
    expect(csv).not.toContain("null");
  });
  it("escapes spreadsheet formulas and CSV quotes in free text", () => {
    const study = structuredClone(demoStudy);
    study.observations[0].label = '=HYPERLINK("test")';
    expect(summaryCsv(study)).toContain("'=HYPERLINK");
    expect(summaryCsv(study)).toContain('""test""');
  });
});

describe("local package boundary", () => {
  it.each([
    [
      "duplicate keys",
      (p: typeof demoStudy) => {
        p.observations[1].key = p.observations[0].key;
      },
    ],
    [
      "unsafe source links",
      (p: typeof demoStudy) => {
        p.observations[0].sourceUrl = "javascript:alert(1)";
      },
    ],
    [
      "invented synthetic area results",
      (p: typeof demoStudy) => {
        p.statistics.validAreaKm2 = 100;
      },
    ],
    [
      "unclosed polygons",
      (p: typeof demoStudy) => {
        p.footprint.geometry.coordinates[0].pop();
      },
    ],
    [
      "invalid coordinates",
      (p: typeof demoStudy) => {
        p.overlays.features[0].geometry.coordinates[0][1][1] = 100;
      },
    ],
    [
      "unknown observation references",
      (p: typeof demoStudy) => {
        p.overlays.features[0].properties.observations = ["missing"];
      },
    ],
    [
      "incomplete supplied metadata",
      (p: typeof demoStudy) => {
        p.status = "provided";
      },
    ],
    [
      "bad UTC timestamps",
      (p: typeof demoStudy) => {
        p.observations[0].acquiredAtUtc = "yesterday";
      },
    ],
    [
      "untraceable series",
      (p: typeof demoStudy) => {
        p.signalSeries[0].observationKey = "missing";
      },
    ],
    [
      "duplicate series points",
      (p: typeof demoStudy) => {
        p.signalSeries.push(p.signalSeries[0]);
      },
    ],
  ])("rejects %s", (_label, mutate) => {
    const p = structuredClone(demoStudy);
    mutate(p);
    expect(() => parseStudyPackage(p)).toThrow();
  });
  it("accepts a local rendered-tile fixture without claiming a scientific observation", () => {
    const p = structuredClone(demoStudy);
    p.observations[0].raster = {
      tiles: ["/test-tiles/{z}/{x}/{y}.png"],
      attribution: "Synthetic renderer test only",
      minDb: -30,
      maxDb: 0,
    };
    expect(parseStudyPackage(p).status).toBe("synthetic");
    p.observations[0].raster.tiles = ["//unsafe.test/{z}/{x}/{y}.png"];
    expect(() => parseStudyPackage(p)).toThrow();
  });
});
