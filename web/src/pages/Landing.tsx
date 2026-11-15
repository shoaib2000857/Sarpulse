import { lazy, Suspense, useEffect, useRef, useState } from "react";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  ChevronLeft,
  ChevronRight,
  Pause,
  Play,
  RotateCcw,
} from "lucide-react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import Lenis from "lenis";
import "lenis/dist/lenis.css";
import "@fontsource/manrope/latin-400.css";
import "@fontsource/manrope/latin-600.css";
import { Button } from "../components/ui/button";
import type { SceneHandle } from "../components/scene/OrbitalScene";
import type { StudyPackage } from "../types/frontend";
import Showcase from "../components/landing/Showcase";
import "../orbital.css";
const OrbitalScene = lazy(() => import("../components/scene/OrbitalScene"));
gsap.registerPlugin(ScrollTrigger);
const chapterNames = [
  "Introduction",
  "The challenge",
  "The solution",
  "Two steps",
  "Start the investigation",
];

export default function Landing({ study }: { study: StudyPackage }) {
  const journey = useRef<HTMLDivElement>(null),
    layers = useRef<HTMLDivElement>(null),
    scene = useRef<SceneHandle>(null),
    progress = useRef(0),
    smoothScroll = useRef<Lenis | null>(null);
  const [chapter, setChapter] = useState(0),
    [motion, setMotion] = useState(
      () => !matchMedia("(prefers-reduced-motion: reduce)").matches,
    );
  useEffect(() => {
    const reduce = matchMedia("(prefers-reduced-motion: reduce)");
    let lenis: Lenis | null = null;
    const configure = () => {
      lenis?.destroy();
      lenis = reduce.matches
        ? null
        : new Lenis({
            duration: 1.3,
            smoothWheel: true,
            syncTouch: false,
            anchors: false,
          });
      lenis?.on("scroll", ScrollTrigger.update);
      smoothScroll.current = lenis;
    };
    configure();
    const tick = (time: number) => lenis?.raf(time * 1000);
    gsap.ticker.add(tick);
    const trigger = ScrollTrigger.create({
      trigger: journey.current,
      start: "top top",
      end: "bottom bottom",
      onUpdate: (self) => {
        progress.current = self.progress;
        setChapter(Math.min(4, Math.floor(self.progress * 4 + 0.45)));
        scene.current?.invalidate();
      },
    });
    const onPreference = () => {
      setMotion(!reduce.matches);
      configure();
    };
    reduce.addEventListener("change", onPreference);
    void document.fonts.ready.then(() => trigger.refresh());
    return () => {
      trigger.kill();
      gsap.ticker.remove(tick);
      reduce.removeEventListener("change", onPreference);
      lenis?.destroy();
      smoothScroll.current = null;
    };
  }, []);
  useEffect(() => {
    if (!layers.current) return;
    const sections =
      layers.current.querySelectorAll<HTMLElement>(".orbital-chapter");
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    sections.forEach((section, i) =>
      gsap.to(section, {
        autoAlpha: i === chapter ? 1 : 0,
        y: i === chapter ? 0 : i < chapter ? -35 : 35,
        duration: reduce ? 0 : 0.65,
        ease: "power2.out",
        overwrite: true,
      }),
    );
    return () => {
      gsap.killTweensOf(sections);
    };
  }, [chapter]);
  function goTo(index: number) {
    const element = journey.current;
    if (!element) return;
    const target =
      element.getBoundingClientRect().top +
      window.scrollY +
      ((element.offsetHeight - innerHeight) * index) / 4;
    if (smoothScroll.current)
      smoothScroll.current.scrollTo(target, { duration: 1.3 });
    else window.scrollTo({ top: target, behavior: "instant" });
  }
  const active = (i: number) => ({
    id: `orbit-chapter-${i}`,
    "aria-hidden": chapter !== i,
    inert: chapter !== i,
  });
  return (
    <div className="orbital-landing">
      <div
        className="orbital-journey"
        ref={journey}
        data-orbit-chapter={chapter}
      >
        <div className="orbital-stage">
          <Suspense
            fallback={
              <div className="orbital-loading">Loading the 3D experience…</div>
            }
          >
            <OrbitalScene ref={scene} progress={progress} motion={motion} />
          </Suspense>
          <div className="orbital-vignette" />
          <div className="orbital-scroll-content" ref={layers}>
            <section {...active(0)} className="orbital-chapter orbital-hero">
              <div className="orbital-hero-title">
                <p>Radar. Time. Evidence.</p>
                <h1>
                  Earth’s changes
                  <br />
                  made visible
                </h1>
              </div>
              <Button asChild className="orbital-hero-cta">
                <a href="#explore">
                  Explore the change <ArrowUpRight size={16} />
                </a>
              </Button>
            </section>
            <section {...active(1)} className="orbital-chapter orbital-reveal">
              <div className="orbital-copy">
                <span className="orbital-eyebrow orbital-orange">
                  The challenge
                </span>
                <h2>
                  A changing landscape
                  <br />
                  is only part of the story.
                  <br />
                  What changed—and why?
                </h2>
              </div>
            </section>
            <section {...active(2)} className="orbital-chapter orbital-reveal">
              <div className="orbital-copy">
                <span className="orbital-eyebrow">The solution</span>
                <h2>
                  Compare observations.
                  <br />
                  Follow their evidence.
                  <br />
                  Keep uncertainty in view.
                </h2>
                <a className="orbital-inline-link" href="#story">
                  Take the guided story <ArrowUpRight size={16} />
                </a>
              </div>
            </section>
            <section {...active(3)} className="orbital-chapter orbital-steps">
              <h2 className="sr-only">Your investigation in two steps</h2>
              <div className="orbital-steps-row">
                <a href="#explore">
                  <span>01</span>
                  <h3>Compare</h3>
                  <p>the observations</p>
                  <ArrowUpRight size={18} />
                </a>
                <span className="orbital-step-gap" aria-hidden="true" />
                <a href="#science">
                  <span>02</span>
                  <h3>Inspect</h3>
                  <p>the evidence</p>
                  <ArrowUpRight size={18} />
                </a>
              </div>
            </section>
            <section {...active(4)} className="orbital-chapter orbital-finale">
              <span className="orbital-eyebrow">
                Earth’s changes. Revealed by radar.
              </span>
              <h2>
                See Earth
                <br />
                differently
              </h2>
              <Button asChild>
                <a href="#explore">
                  Open geographic workspace <ArrowUpRight size={16} />
                </a>
              </Button>
              <p className="orbital-beam-caption">
                Radar lights the ground itself, day or night. The echoes that
                return are recorded as backscatter. Illustrative beam, not to
                scale.
              </p>
            </section>
          </div>
          <div
            className="orbital-scene-controls"
            aria-label="3D model controls"
          >
            <span className="drag-instruction">Drag</span>
            <button
              aria-label="Rotate satellite left"
              onClick={() => scene.current?.rotate(-Math.PI / 8)}
            >
              <ChevronLeft size={14} />
            </button>
            <button
              aria-label="Rotate satellite right"
              onClick={() => scene.current?.rotate(Math.PI / 8)}
            >
              <ChevronRight size={14} />
            </button>
            <button
              aria-label="Reset satellite rotation"
              onClick={() => scene.current?.reset()}
            >
              <RotateCcw size={12} />
            </button>
            <button
              className="orbital-motion-button"
              aria-label={motion ? "Pause 3D motion" : "Resume 3D motion"}
              aria-pressed={!motion}
              onClick={() => setMotion(!motion)}
            >
              {motion ? <Pause size={11} /> : <Play size={11} />}
            </button>
          </div>
          <nav className="orbital-chapter-nav" aria-label="Orbital chapters">
            {chapterNames.map((name, i) => (
              <button
                key={name}
                aria-label={name}
                aria-current={chapter === i ? "step" : undefined}
                onClick={() => goTo(i)}
              >
                <small>{String(i + 1).padStart(2, "0")}</small>
                <span>
                  {name === "Start the investigation" ? "Explore" : name}
                </span>
                <i />
              </button>
            ))}
          </nav>
          <div className="orbital-scroll-cue">
            <span>Continue scrolling</span>
            <ArrowDown size={13} />
          </div>
          <div className="orbital-model-note">
            3D reference: NASA SMAP · not NISAR · not a live orbit
          </div>
        </div>
      </div>
      <Showcase />
      <section className="orbital-destinations">
        <div>
          <span className="orbital-eyebrow">Your field of view</span>
          <h2>{study.title}</h2>
          <p>{study.region}</p>
        </div>
        <a className="orbital-destination-main" href="#explore">
          {study.status === "synthetic"
            ? "Explore the demo workspace"
            : "Explore the supplied package"}
          <ArrowUpRight size={22} />
        </a>
        <div className="orbital-destination-links">
          <a href="#science">
            <span>Science Lab</span>
            <p>Source observations. Signal summaries. Honest limits.</p>
            <ArrowUpRight size={18} />
          </a>
          <a href="#story">
            <span>Guided story</span>
            <p>Five chapters, from a place to its evidence.</p>
            <ArrowUpRight size={18} />
          </a>
        </div>
        <div className="orbital-integrity">
          <p>
            {study.status === "synthetic"
              ? "Synthetic interface demonstration. No verified NISAR observations or scientific results are connected."
              : "Local package loaded. Review its source evidence before interpretation."}
          </p>
          <a href="#science">
            Read the limitations
            <ArrowRight size={14} />
          </a>
        </div>
      </section>
    </div>
  );
}
