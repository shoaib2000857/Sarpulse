import { test, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

async function settledChapter(page: Page, index: number) {
  await expect(page.locator(".orbital-journey")).toHaveAttribute(
    "data-orbit-chapter",
    String(index),
  );
  await expect
    .poll(() =>
      page.locator(".orbital-journey").evaluate((el) => {
        const start = el.getBoundingClientRect().top + scrollY;
        const distance = (el as HTMLElement).offsetHeight - innerHeight;
        return (scrollY - start) / distance;
      }),
    )
    .toBeCloseTo(index / 4, 2);
  await expect(
    page.locator('.orbital-chapter[aria-hidden="false"]'),
  ).toHaveCount(1);
  await expect(page.locator('.orbital-chapter[aria-hidden="false"]')).toHaveCSS(
    "opacity",
    "1",
  );
  await expect
    .poll(() =>
      page
        .locator('.orbital-chapter[aria-hidden="true"]')
        .evaluateAll((elements) =>
          elements.every((el) => Number(getComputedStyle(el).opacity) === 0),
        ),
    )
    .toBe(true);
}

test("orbital scene renders, responds to rotation and scroll, and releases its route resources", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(page.locator(".orbital-scene")).toHaveAttribute(
    "data-scene-status",
    "ready",
  );
  await expect(page.locator(".orbital-scene")).toHaveAttribute(
    "data-model-source",
    "NASA SMAP GLB",
  );
  await page.getByRole("button", { name: "Pause 3D motion" }).click();
  await expect(
    page.getByRole("button", { name: "Resume 3D motion" }),
  ).toBeVisible();
  const canvas = page.locator(".orbital-scene canvas");
  const before = await canvas.screenshot();
  await page.getByRole("button", { name: "Rotate satellite right" }).click();
  await expect
    .poll(async () => Buffer.compare(before, await canvas.screenshot()))
    .not.toBe(0);
  await page.getByRole("button", { name: "Reset satellite rotation" }).click();
  await page.screenshot({ path: "test-results/orbital-hero-desktop.png" });
  const bounds = (await canvas.boundingBox())!;
  const dragBefore = await canvas.screenshot();
  await page.mouse.move(
    bounds.x + bounds.width * 0.55,
    bounds.y + bounds.height * 0.62,
  );
  await page.mouse.down();
  await page.mouse.move(
    bounds.x + bounds.width * 0.55 + 140,
    bounds.y + bounds.height * 0.62 + 8,
    { steps: 8 },
  );
  await page.mouse.up();
  await expect
    .poll(async () => Buffer.compare(dragBefore, await canvas.screenshot()))
    .not.toBe(0);
  await page
    .getByRole("button", { name: "The challenge", exact: true })
    .click();
  await settledChapter(page, 1);
  await expect(
    page.getByRole("link", { name: "SARPulse home" }),
  ).toBeInViewport();
  await page.screenshot({ path: "test-results/orbital-radar-desktop.png" });
  await page
    .getByRole("button", { name: "Start the investigation", exact: true })
    .click();
  await settledChapter(page, 4);
  await page.screenshot({ path: "test-results/orbital-earth-desktop.png" });
  await page
    .getByRole("link", { name: "Open geographic workspace", exact: true })
    .click();
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
  await expect(page.locator(".orbital-scene")).toHaveCount(0);
  await expect(page.locator("html")).not.toHaveClass(/lenis/);
  await page.getByRole("link", { name: "Overview", exact: true }).click();
  await expect(page.locator(".orbital-scene")).toHaveAttribute(
    "data-scene-status",
    "ready",
  );
  expect(errors).toEqual([]);
});

test("orbital two-step actions open the map and the scientific evidence", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.getByRole("button", { name: "Two steps", exact: true }).click();
  await settledChapter(page, 3);
  await page.getByRole("link", { name: /02 Inspect the evidence/ }).click();
  await expect(page).toHaveURL(/#science$/);
  await expect(page.locator(".orbital-scene")).toHaveCount(0);
  await page.getByRole("link", { name: "Overview", exact: true }).click();
  await page.getByRole("button", { name: "Two steps", exact: true }).click();
  await settledChapter(page, 3);
  await page.getByRole("link", { name: /01 Compare the observations/ }).click();
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
});

test("orbital experience honors reduced motion and fits mobile screens", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(page.locator(".orbital-scene")).toHaveAttribute(
    "data-scene-status",
    "ready",
  );
  await expect(
    page.getByRole("button", { name: "Resume 3D motion" }),
  ).toBeVisible();
  await expect(page.locator("html")).not.toHaveClass(/lenis/);
  await page.screenshot({ path: "test-results/orbital-hero-mobile.png" });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.mouse.wheel(0, 1400);
  await expect(page.locator(".orbital-journey")).not.toHaveAttribute(
    "data-orbit-chapter",
    "0",
  );
  await page.screenshot({ path: "test-results/orbital-scroll-mobile.png" });
  await page.setViewportSize({ width: 320, height: 740 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.setViewportSize({ width: 844, height: 390 });
  await expect(
    page.getByRole("button", { name: "Introduction", exact: true }),
  ).toBeInViewport();
  await page.getByRole("button", { name: "Introduction", exact: true }).click();
  await settledChapter(page, 0);
  await expect(
    page.getByRole("link", { name: "Explore the change", exact: true }),
  ).toBeInViewport();
  await expect(
    page.getByRole("button", { name: "Rotate satellite right" }),
  ).toBeInViewport();
  await page.screenshot({ path: "test-results/orbital-hero-landscape.png" });
});

test("orbital renderer failure keeps the landing and explorer link usable", async ({
  page,
}) => {
  await page.addInitScript(() => {
    const original = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (
      this: HTMLCanvasElement,
      ...args: Parameters<typeof original>
    ) {
      if (String(args[0]).includes("webgl")) return null;
      return original.apply(this, args);
    } as typeof original;
  });
  await page.goto("/");
  await expect(page.locator(".orbital-scene")).toHaveAttribute(
    "data-scene-status",
    "unavailable",
  );
  await expect(
    page.getByText("3D view unavailable.", { exact: false }),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "Explore the change", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Brahmaputra floodplain" }),
  ).toBeVisible();
});
