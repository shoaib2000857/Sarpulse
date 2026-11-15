import { useEffect, useRef } from "react";
import { init, use } from "echarts/core";
import { LineChart } from "echarts/charts";
import {
  AriaComponent,
  GridComponent,
  TooltipComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { observationLabel } from "../../lib/study";
import type { StudyPackage } from "../../types/frontend";
use([
  LineChart,
  AriaComponent,
  GridComponent,
  TooltipComponent,
  CanvasRenderer,
]);

export default function SignalChart({ study }: { study: StudyPackage }) {
  const root = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!root.current) return;
    const chart = init(root.current, undefined, { renderer: "canvas" });
    const hasTimestamps = study.observations.every(
      (o) => o.acquiredAtUtc !== null,
    );
    const values = study.observations.map((o) => {
      const value =
        study.signalSeries.find((q) => q.observationKey === o.key)?.valueDb ??
        null;
      return hasTimestamps ? [Date.parse(o.acquiredAtUtc!), value] : value;
    });
    chart.setOption({
      useUTC: true,
      animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      aria: {
        enabled: true,
        label: {
          description:
            study.status === "synthetic"
              ? "Illustrative backscatter values only, not NASA measurements. A table follows the chart."
              : "Supplied signal summary by observation. A table follows the chart.",
        },
      },
      grid: { left: 50, right: 25, top: 25, bottom: 45 },
      tooltip: {
        trigger: "axis",
        renderMode: "richText",
        backgroundColor: "#20344a",
        borderWidth: 0,
        textStyle: { color: "#edf3f7" },
      },
      xAxis: {
        type: hasTimestamps ? "time" : "category",
        ...(hasTimestamps
          ? {}
          : { data: study.observations.map(observationLabel) }),
        axisLine: { lineStyle: { color: "#3c5065" } },
        axisLabel: {
          color: "#b2c0ce",
          fontFamily: "IBM Plex Sans",
          hideOverlap: true,
        },
      },
      yAxis: {
        type: "value",
        name: "dB",
        nameTextStyle: { color: "#b2c0ce" },
        axisLabel: { color: "#b2c0ce" },
        splitLine: { lineStyle: { color: "#25394e" } },
      },
      series: [
        {
          type: "line",
          name:
            study.status === "synthetic"
              ? "Illustrative signal (dB)"
              : "Supplied signal (dB)",
          data: values,
          connectNulls: false,
          smooth: false,
          symbolSize: 9,
          lineStyle: { color: "#69dce8", width: 2 },
          itemStyle: {
            color: "#69dce8",
            borderWidth: 3,
            borderColor: "#122238",
          },
          areaStyle: { color: "rgba(105,220,232,0.06)" },
        },
      ],
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
      className="signal-chart"
      role="img"
      aria-label={
        study.status === "synthetic"
          ? "Illustrative signal chart, not measured observations. Values in the table below."
          : "Supplied backscatter summary, values in the table below."
      }
    />
  );
}
