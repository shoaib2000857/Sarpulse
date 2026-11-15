/* Pointer-driven 3D tilt for cards and controls. One delegated listener for the
   whole app; mouse only, and off entirely under prefers-reduced-motion. */
const SELECTOR = [
  ".metric",
  ".basemap-option",
  ".layer-option",
  ".sc-stat",
  ".sc-step",
  ".sc-col",
  ".scattering-row",
  ".story-evidence-note",
  ".orbital-destination-links a",
  ".orbital-destination-main",
  ".orbital-steps-row > a",
  ".class-chip",
].join(",");

export function installTilt(root: HTMLElement) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return () => {};
  let current: HTMLElement | null = null;
  const release = (el: HTMLElement) => {
    el.style.transition = "transform .55s cubic-bezier(.2,.8,.2,1)";
    el.style.transform = "";
    window.setTimeout(() => {
      if (el !== current) el.style.transition = "";
    }, 560);
  };
  const move = (e: PointerEvent) => {
    if (e.pointerType !== "mouse") return;
    const el = (e.target as Element).closest?.<HTMLElement>(SELECTOR) ?? null;
    if (el !== current) {
      if (current) release(current);
      current = el;
      if (el) el.style.transition = "transform .12s ease-out";
    }
    if (!el) return;
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5,
      y = (e.clientY - r.top) / r.height - 0.5;
    const max = r.width > 420 ? 3 : 8; // degrees: gentler on wide cards
    const press = e.buttons & 1 ? " scale(.97)" : "";
    el.style.transform = `perspective(900px) rotateX(${(-y * 2 * max).toFixed(2)}deg) rotateY(${(x * 2 * max).toFixed(2)}deg) translateZ(8px)${press}`;
  };
  const leave = () => {
    if (current) release(current);
    current = null;
  };
  root.addEventListener("pointermove", move);
  root.addEventListener("pointerdown", move);
  root.addEventListener("pointerup", move);
  root.addEventListener("pointerleave", leave);
  return () => {
    leave();
    root.removeEventListener("pointermove", move);
    root.removeEventListener("pointerdown", move);
    root.removeEventListener("pointerup", move);
    root.removeEventListener("pointerleave", leave);
  };
}
