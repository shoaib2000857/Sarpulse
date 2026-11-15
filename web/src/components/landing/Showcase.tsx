import { useEffect, useRef } from "react";
import { ArrowUpRight, Check, Minus } from "lucide-react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import "../../showcase.css";

gsap.registerPlugin(ScrollTrigger);

/* Public NASA-ISRO NISAR mission figures (mission overview material).
   They describe the mission, not this project's demo data. */
const stats = [
  { value: 2, suffix: "", label: "radar bands", note: "L-band and S-band" },
  { value: 12, suffix: " days", label: "repeat cycle", note: "global revisit" },
  { value: 242, suffix: " km", label: "swath width", note: "single pass" },
  { value: 5, suffix: "", label: "evidence stages", note: "in this workspace" },
];

const lifecycle = [
  ["Acquire", "Radar passes over the same place again and again."],
  ["Calibrate", "Geometry, units and processing release stay attached."],
  ["Compare", "Observations line up before and after."],
  ["Interpret", "Signal change is a clue, not a verdict."],
  ["Share", "Every figure carries its provenance."],
];

const shows = [
  "Backscatter changed between two dates",
  "Where the signal brightened or darkened",
  "Which polarization and release was used",
];
const cannot = [
  "That a change means flooding on its own",
  "Ground displacement from GCOV alone",
  "All-weather accuracy from cloud penetration",
];

export default function Showcase() {
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const ctx = gsap.context(() => {
      const counters = gsap.utils.toArray<HTMLElement>("[data-count]");
      if (reduce) {
        counters.forEach((c) => (c.textContent = c.dataset.count ?? ""));
        return;
      }
      /* marquee drifts with scroll */
      gsap.utils.toArray<HTMLElement>(".sc-marquee-track").forEach((t, i) =>
        gsap.to(t, {
          xPercent: i % 2 ? 12 : -22,
          ease: "none",
          scrollTrigger: {
            trigger: ".sc-marquee",
            start: "top bottom",
            end: "bottom top",
            scrub: 0.6,
          },
        }),
      );
      /* split-line reveals */
      gsap.utils.toArray<HTMLElement>("[data-reveal]").forEach((n) =>
        gsap.from(n, {
          y: 60,
          autoAlpha: 0,
          duration: 1,
          ease: "power3.out",
          scrollTrigger: { trigger: n, start: "top 88%", once: true },
        }),
      );
      /* count-up */
      counters.forEach((c) => {
        const end = Number(c.dataset.count);
        const o = { v: 0 };
        c.textContent = "0";
        gsap.to(o, {
          v: end,
          duration: 1.8,
          ease: "power3.out",
          onUpdate: () => (c.textContent = String(Math.round(o.v))),
          scrollTrigger: { trigger: c, start: "top 90%", once: true },
        });
      });
      /* stagger cards */
      gsap.from(".sc-step", {
        y: 50,
        autoAlpha: 0,
        stagger: 0.12,
        duration: 0.9,
        ease: "power3.out",
        scrollTrigger: { trigger: ".sc-lifeline", start: "top 82%", once: true },
      });
      gsap.fromTo(
        ".sc-lifeline-fill",
        { scaleX: 0 },
        {
          scaleX: 1,
          ease: "none",
          transformOrigin: "left center",
          scrollTrigger: {
            trigger: ".sc-lifeline",
            start: "top 80%",
            end: "bottom 45%",
            scrub: 0.5,
          },
        },
      );
      gsap.from(".sc-col", {
        y: 60,
        autoAlpha: 0,
        stagger: 0.18,
        duration: 1,
        ease: "power3.out",
        scrollTrigger: { trigger: ".sc-compare", start: "top 80%", once: true },
      });
    }, el);
    /* pointer-follow glow on cards */
    const move = (e: PointerEvent) => {
      const card = (e.target as HTMLElement).closest<HTMLElement>(".sc-glow");
      if (!card) return;
      const r = card.getBoundingClientRect();
      card.style.setProperty("--mx", `${e.clientX - r.left}px`);
      card.style.setProperty("--my", `${e.clientY - r.top}px`);
    };
    el.addEventListener("pointermove", move);
    return () => {
      el.removeEventListener("pointermove", move);
      ctx.revert();
    };
  }, []);

  const word = "RADAR · TIME · EVIDENCE · ";
  return (
    <div className="sc-root" ref={root}>
      <div className="sc-marquee" aria-hidden="true">
        {[0, 1].map((r) => (
          <div className="sc-marquee-track" key={r} data-row={r}>
            {Array.from({ length: 4 }, (_, i) => (
              <span key={i}>{word}</span>
            ))}
          </div>
        ))}
      </div>

      <section className="sc-section sc-stats" aria-labelledby="sc-stats-h">
        <span className="orbital-eyebrow" data-reveal>
          The mission behind the pixels
        </span>
        <h2 id="sc-stats-h" data-reveal>
          Built for a planet
          <br />
          that never holds still.
        </h2>
        <dl className="sc-stat-grid">
          {stats.map((s) => (
            <div className="sc-stat sc-glow" key={s.label}>
              <dt>{s.label}</dt>
              <dd>
                <b data-count={s.value}>{s.value}</b>
                <span>{s.suffix}</span>
              </dd>
              <small>{s.note}</small>
            </div>
          ))}
        </dl>
        <p className="sc-footnote" data-reveal>
          Public NASA–ISRO NISAR mission figures for context. They describe the
          mission, not the demo fixture shown in this workspace.
        </p>
      </section>

      <section className="sc-section" aria-labelledby="sc-life-h">
        <span className="orbital-eyebrow" data-reveal>
          Evidence lifecycle
        </span>
        <h2 id="sc-life-h" data-reveal>
          From echo to explanation.
        </h2>
        <div className="sc-lifeline">
          <div className="sc-lifeline-bar" aria-hidden="true">
            <i className="sc-lifeline-fill" />
          </div>
          <ol>
            {lifecycle.map(([t, d], i) => (
              <li className="sc-step sc-glow" key={t}>
                <small>{String(i + 1).padStart(2, "0")}</small>
                <h3>{t}</h3>
                <p>{d}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="sc-section sc-compare" aria-labelledby="sc-cmp-h">
        <span className="orbital-eyebrow" data-reveal>
          Read it honestly
        </span>
        <h2 id="sc-cmp-h" data-reveal>
          SAR is not a photograph.
        </h2>
        <div className="sc-cols">
          <div className="sc-col sc-glow">
            <h3>What backscatter can show</h3>
            <ul>
              {shows.map((t) => (
                <li key={t}>
                  <Check size={16} /> {t}
                </li>
              ))}
            </ul>
          </div>
          <div className="sc-col sc-glow sc-col-warn">
            <h3>What it cannot claim alone</h3>
            <ul>
              {cannot.map((t) => (
                <li key={t}>
                  <Minus size={16} /> {t}
                </li>
              ))}
            </ul>
            <a href="#science">
              Read the limitations <ArrowUpRight size={15} />
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
