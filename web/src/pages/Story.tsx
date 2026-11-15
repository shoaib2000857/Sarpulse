import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Cloud,
  MapPin,
  Radar,
  ScanLine,
  ShieldQuestion,
} from "lucide-react";
import GeoWorkspace from "../components/map/GeoWorkspace";
import { Button } from "../components/ui/button";
import type { LayerMode, StudyPackage } from "../types/frontend";
gsap.registerPlugin(ScrollTrigger);

export default function Story({ study }: { study: StudyPackage }) {
  const [chapter, setChapter] = useState(0);
  const root = useRef<HTMLDivElement>(null);
  const chapters = [
    {
      title: "A landscape in motion.",
      icon: MapPin,
      text: `${study.title} is our ${study.status === "synthetic" ? "candidate" : "supplied"} area of interest. Start with a place and a question: how do water and wetland patterns change through time?`,
      note:
        study.status === "synthetic"
          ? "The extent and cells are illustrative. Actual acquisition coverage is unconfirmed."
          : "Inspect the supplied footprint and its source metadata before interpretation.",
    },
    {
      title: "Clouds leave a question open.",
      icon: Cloud,
      text: "An optical view can be cloud-obscured. Radar offers a different way to observe the surface, using its own transmitted signal rather than sunlight.",
      note: "Cloud penetration is not a guarantee of usable data or all-weather accuracy. Geometry and surface conditions still matter.",
    },
    {
      title: "A signal, not a photograph.",
      icon: Radar,
      text: "A radar return reflects interactions with water, soil, and vegetation. Comparable acquisitions, polarization, calibration, and processing lineage are needed before comparing that signal.",
      note:
        study.status === "synthetic"
          ? "There are no actual NISAR scenes or polarization layers in this demonstration."
          : "The viewer preserves supplied metadata; it does not check scene comparability.",
    },
    {
      title: "A difference asks why.",
      icon: ScanLine,
      text: "Compare the earlier and later view. Changes in backscatter may point to a surface change, but moisture, roughness, vegetation, and processing artifacts are alternative explanations.",
      note:
        study.status === "synthetic"
          ? "Colored test rectangles demonstrate the interaction only. They are not observed water gains or losses."
          : "Colored classifications are supplied, precomputed outputs. Date controls do not recalculate them.",
    },
    {
      title: "End with evidence. And limits.",
      icon: ShieldQuestion,
      text: "A trustworthy story keeps its source observations, methods, validation, and uncertainty visible. Open Science Lab to inspect what supports the interpretation—and what is still missing.",
      note: `Current status: ${study.validationStatus}. ${study.status === "synthetic" ? "This is a guided interface demonstration, not a confirmed flood investigation." : "Scientific claims require independent review of the supplied evidence."}`,
    },
  ];
  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.utils
        .toArray<HTMLElement>(".story-chapter")
        .forEach((element, i) => {
          ScrollTrigger.create({
            trigger: element,
            start: "top 52%",
            end: "bottom 52%",
            onEnter: () => setChapter(i),
            onEnterBack: () => setChapter(i),
          });
        });
      if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches)
        gsap.fromTo(
          ".story-progress-fill",
          { scaleX: 0 },
          {
            scaleX: 1,
            transformOrigin: "left",
            ease: "none",
            scrollTrigger: {
              trigger: root.current,
              start: "top top",
              end: "bottom bottom",
              scrub: true,
            },
          },
        );
    }, root);
    return () => ctx.revert();
  }, [study]);
  function go(i: number) {
    setChapter(i);
    document.getElementById(`chapter-${i}`)?.scrollIntoView({
      behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "instant"
        : "smooth",
      block: "center",
    });
  }
  const mode: LayerMode =
    chapter === 0 ? "before" : chapter === 4 ? "difference" : "after";
  const Icon = chapters[chapter].icon;
  return (
    <div className="story-page" ref={root}>
      <div className="story-heading page-width">
        <div>
          <span className="section-kicker">
            <BookOpen size={15} />
            Guided story
          </span>
          <h1>Between water and land.</h1>
          <p>
            A five-part investigation into what radar can reveal—and what it
            cannot tell us alone.
          </p>
        </div>
        <span className="data-badge">
          {study.status === "synthetic"
            ? "Interface demonstration"
            : "Supplied evidence"}
        </span>
      </div>
      <div className="story-layout page-width">
        <div className="story-map-sticky">
          <div className="story-map-title">
            <Icon size={17} />
            <span>{study.title}</span>
            <span>{chapter + 1} / 5</span>
          </div>
          <GeoWorkspace
            study={study}
            observationKey={study.observations[1].key}
            beforeKey={study.observations[0].key}
            mode={mode}
            compare={chapter === 3}
            opacity={0.8}
            palette="standard"
            contextMap={false}
            showFootprint={true}
          />
          <div className="story-map-controls">
            <Button
              variant="ghost"
              size="sm"
              disabled={chapter === 0}
              onClick={() => go(chapter - 1)}
            >
              <ArrowLeft size={15} />
              Previous
            </Button>
            <span role="status" aria-live="polite" aria-label="Story progress">
              Chapter {chapter + 1} of 5
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={chapter === 4}
              onClick={() => go(chapter + 1)}
            >
              Next
              <ArrowRight size={15} />
            </Button>
          </div>
          <div className="story-progress">
            <div
              className="story-progress-fill"
              style={{ transform: `scaleX(${(chapter + 1) / 5})` }}
            />
          </div>
          <nav className="story-dots" aria-label="Story chapters">
            {chapters.map((c, i) => (
              <button
                key={c.title}
                aria-label={`Chapter ${i + 1}: ${c.title}`}
                aria-current={chapter === i ? "step" : undefined}
                onClick={() => go(i)}
              >
                <span />
                {i + 1}
              </button>
            ))}
          </nav>
        </div>
        <div className="story-chapters">
          {chapters.map((c, i) => (
            <section
              key={c.title}
              id={`chapter-${i}`}
              className={`story-chapter ${chapter === i ? "active" : ""}`}
              aria-labelledby={`chapter-title-${i}`}
            >
              <div className="chapter-number">
                Chapter {String(i + 1).padStart(2, "0")} <c.icon size={20} />
              </div>
              <h2 id={`chapter-title-${i}`}>{c.title}</h2>
              <p>{c.text}</p>
              <aside className="story-evidence-note">
                <strong>
                  {study.status === "synthetic"
                    ? "Evidence check"
                    : "Interpretation limit"}
                </strong>
                {c.note}
              </aside>
              {i === 4 && (
                <Button asChild>
                  <a href="#science">
                    Inspect the evidence
                    <ArrowRight size={16} />
                  </a>
                </Button>
              )}
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
