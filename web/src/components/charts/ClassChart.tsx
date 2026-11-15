import { useEffect, useRef } from "react";
import { init, use } from "echarts/core";
import { BarChart } from "echarts/charts";
import {
  AriaComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { colors, observationLabel } from "../../lib/study";
import type { ChangeKind, StudyPackage } from "../../types/frontend";
use([
  BarChart,
  AriaComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  CanvasRenderer,
]);

export const classKinds: { kind: ChangeKind; label: string }[] = [
  { kind: "stable", label: "Persistent" },
  { kind: "gain", label: "Gain" },
  { kind: "loss", label: "Loss" },
  { kind: "no-data", label: "No data" },
];
/** Counts supplied overlay cells per class for one observation. No area, no analysis. */
export const classCount = (
  study: StudyPackage,
  key: string,
  kind: ChangeKind,
) =>
  study.overlays.features.filter(
    (f) =>
      f.properties.kind === kind &&
      (kind === "no-data" || f.properties.observations.includes(key)),
  ).length;

export default function ClassChart({ study }: { study: StudyPackage }) {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!root.current) return;
    const chart = init(root.current, undefined, { renderer: "canvas" });
    const c = colors(false);
    const text = { color: "#aeb4bc", fontFamily: "Manrope" };
    chart.setOption({
      animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      aria: { enabled: true },
      grid: { left: 36, right: 12, top: 62, bottom: 30 },
      legend: {
        top: 0,
        left: 0,
        itemWidth: 10,
        itemHeight: 10,
        textStyle: text,
      },
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "shadow" },
        renderMode: "richText",
        backgroundColor: "#14171c",
        borderWidth: 0,
        textStyle: { color: "#fff" },
      },
      xAxis: {
        type: "category",
        data: study.observations.map(observationLabel),
        axisLine: { lineStyle: { color: "#2a2f37" } },
        axisLabel: { ...text, hideOverlap: true },
      },
      yAxis: {
        type: "value",
        name: "cells",
        minInterval: 1,
        nameTextStyle: text,
        axisLabel: text,
        splitLine: { lineStyle: { color: "#1a1d22" } },
      },
      series: classKinds.map(({ kind, label }) => ({
        type: "bar",
        stack: "cells",
        name: label,
        barMaxWidth: 46,
        itemStyle: { color: c[kind] },
        data: study.observations.map((o) => classCount(study, o.key, kind)),
      })),
    });
    const resize = new ResizeObserver(() => chart.resize());
    resize.observe(root.current);
    return () => {
      resize.disconnect();
      chart.dispose();
    };
  }, [study]);
  return (
    <div
      ref={root}
      className="signal-chart class-chart"
      role="img"
      aria-label={
        study.status === "synthetic"
          ? "Count of schematic test cells per class at each stage. Not measured change. Values in the table below."
          : "Count of supplied class cells per observation. Values in the table below."
      }
    />
  );
}
