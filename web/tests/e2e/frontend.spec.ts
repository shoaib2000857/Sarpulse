import { test, expect } from "@playwright/test";
import { demoStudy } from "../../src/data/demo";

test.beforeEach(async ({page}) => {
  await page.route("**/data/sites.json", route => route.fulfill({status:404,body:"No installed package in this fixture test"}));
});

test("landing, explorer controls, actual map rendering, comparison and exports", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Earth’s changes.*made visible/i }),
  ).toBeVisible();
  await expect(page.locator(".data-banner")).toContainText(
    "NOT NASA OBSERVATIONS",
  );
  await expect(page.locator(".orbital-scene")).toHaveAttribute(
    "data-scene-status",
    "ready",
  );
  await page.screenshot({
    path: "test-results/landing-desktop.png",
    fullPage: false,
  });
  await page
    .getByRole("link", { name: "Explore the change", exact: true })
    .click();
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
  await page.getByRole("slider", { name: "Observation timeline" }).fill("2");
  await expect(
    page.getByRole("combobox", { name: "After", exact: true }),
  ).toHaveValue("2");
  await page.getByRole("button", { name: "Compare", exact: true }).click();
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
  await expect(page.locator(".maplibregl-canvas")).toHaveCount(2);
  await page.getByRole("slider", { name: "Comparison divider" }).fill("72");
  await expect(page.locator(".compare-keyboard output")).toHaveText("72%");
  await expect(page.locator(".maplibregl-compare")).toHaveCSS(
    "transform",
    /matrix/,
  );
  await page.screenshot({
    path: "test-results/explorer-desktop.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Exit comparison" }).click();
  await page.getByRole("radio", { name: "Water gained" }).check();
  await page
    .getByRole("checkbox", { name: "Alternative color palette" })
    .check();
  await page.getByRole("button", { name: "Inspect", exact: true }).click();
  await page.getByRole("button", { name: "Test gain A" }).click();
  await expect(page.locator(".inspection-result")).toContainText("93.73000");
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export visible GeoJSON" }).click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toContain("synthetic");
  await page.getByRole("button", { name: "Play timeline" }).click();
  await expect(
    page.getByRole("combobox", { name: "After", exact: true }),
  ).toHaveValue("3");
  await expect(
    page.getByRole("button", { name: "Play timeline" }),
  ).toBeVisible();
  expect(errors).toEqual([]);
});

test("Science Lab preserves unavailable metadata, table alternatives and provenance exports", async ({
  page,
}) => {
  await page.goto("/#science");
  await expect(
    page.getByRole("heading", { name: "Every change needs evidence." }),
  ).toBeVisible();
  await expect(page.locator(".metric strong").first()).toContainText("—");
  await expect(
    page.getByRole("img", { name: /Illustrative backscatter values/ }),
  ).toBeVisible();
  await page.getByText("Read chart values as a table").click();
  await expect(
    page.getByRole("cell", { name: "-23", exact: true }),
  ).toBeVisible();
  await expect(page.locator(".metadata-list")).toContainText("Not supplied");
  const evt = page.waitForEvent("download");
  await page.getByRole("button", { name: "Summary CSV" }).click();
  expect((await evt).suggestedFilename()).toBe("sarpulse-synthetic.csv");
  await page.screenshot({
    path: "test-results/science-desktop.png",
    fullPage: true,
  });
});

test("local package import is shared across views and invalid imports preserve the open package", async ({
  page,
}) => {
  await page.goto("/#explore");
  await page.locator("input[type=file]").setInputFiles({
    name: "bad.json",
    mimeType: "application/json",
    buffer: Buffer.from('{"schemaVersion":9}'),
  });
  await expect(page.getByRole("alert")).toContainText("Unsupported");
  await expect(
    page.getByRole("heading", { name: "Brahmaputra floodplain" }),
  ).toBeVisible();
  const fixture = structuredClone(demoStudy);
  fixture.title = "Local fixture review";
  await page.locator("input[type=file]").setInputFiles({
    name: "fixture.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(fixture)),
  });
  await expect(
    page.getByRole("heading", { name: "Local fixture review" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Science Lab", exact: true }).click();
  await expect(page.locator(".provenance-text")).toContainText(
    "NOT NASA OBSERVATIONS",
  );
  await page.getByRole("button", { name: "Reset demo" }).click();
  await expect(page.locator(".data-banner")).toContainText("SYNTHETIC");
});

test("story has accessible chapter navigation and shares the working comparison map", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/#story");
  await expect(
    page.getByRole("heading", { name: "Between water and land." }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Chapter 4: A difference asks why." })
    .click();
  await expect(
    page.getByRole("status", { name: "Story progress" }),
  ).toContainText("Chapter 4 of 5");
  await expect(
    page.getByRole("slider", { name: "Comparison divider" }),
  ).toBeVisible();
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
  await page.screenshot({ path: "test-results/story-desktop.png" });
  await expect(
    page.getByRole("status", { name: "Story progress" }),
  ).toContainText("Chapter 5 of 5");
  await expect(
    page.getByRole("link", { name: "Inspect the evidence", exact: true }),
  ).toBeVisible();
});

test("mobile navigation, map controls and long pages stay within the viewport", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Earth’s changes.*made visible/i }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "Explore", exact: true }).click();
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
  await page.screenshot({
    path: "test-results/explorer-mobile.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page.getByRole("link", { name: "Guided story", exact: true }).click();
  await page
    .getByRole("button", { name: "Chapter 5: End with evidence. And limits." })
    .click();
  await expect(
    page.getByRole("status", { name: "Story progress" }),
  ).toContainText("Chapter 5 of 5");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("a supplied tile template is rendered by the frontend without any backend implementation", async ({
  page,
}) => {
  // Synthetic integration fixture only: no real acquisition, channel or SAR pixels are invented.
  const fixture = structuredClone(demoStudy);
  fixture.observations[1].raster = {
    tiles: ["/test-tiles/{z}/{x}/{y}.png"],
    attribution: "Synthetic tile renderer test",
    minDb: -30,
    maxDb: 0,
  };
  let requests = 0;
  await page.route("**/test-tiles/**", (route) => {
    requests++;
    return route.fulfill({
      status: 200,
      contentType: "image/png",
      body: Buffer.from(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==",
        "base64",
      ),
    });
  });
  await page.goto("/#explore");
  await page.locator("input[type=file]").setInputFiles({
    name: "tile-fixture.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(fixture)),
  });
  await expect(page.locator(".raster-state")).toContainText(
    "Supplied radar tiles",
  );
  await expect.poll(() => requests).toBeGreaterThan(0);
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "ready",
  );
});

test("WebGL failure leaves accessible geometry inspection and Science Lab available", async ({
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
  await page.goto("/#explore");
  await expect(page.locator(".geo-workspace")).toHaveAttribute(
    "data-map-status",
    "unavailable",
  );
  await page
    .getByRole("button", { name: "Test gain A · gain", exact: true })
    .click();
  await expect(page.locator(".inspection-result")).toContainText("Test gain A");
  await page.getByRole("link", { name: "Science Lab", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Every change needs evidence." }),
  ).toBeVisible();
});
