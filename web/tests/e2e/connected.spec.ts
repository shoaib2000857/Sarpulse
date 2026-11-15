import { test,expect } from "@playwright/test";

test("real precomputed investigation renders radar images, change layers, passports and reference evidence",async({page})=>{
  await page.goto("/#explore");
  await page.getByRole("combobox",{name:"Scientific investigation"}).selectOption("biesbosch-netherlands");
  await expect(page.getByRole("heading",{name:/Biesbosch/})).toBeVisible();
  await expect(page.locator(".data-banner")).toContainText("NASA NISAR observations");
  await page.getByRole("radio",{name:"Grid",exact:true}).check();
  await expect(page.locator(".geo-workspace")).toHaveAttribute("data-map-status","ready");
  await expect(page.locator(".raster-state")).toContainText("Supplied radar image");
  await page.getByRole("radio",{name:/Water gained/}).check();
  const map=page.locator(".maplibregl-canvas").first(); await map.click({position:{x:250,y:250}});
  await expect(page.getByRole("region",{name:"Change Passport"})).toBeVisible();
  await expect(page.locator(".change-passport")).toContainText("Observed");
  await page.screenshot({path:"test-results/connected-explorer.png",fullPage:true});
  await page.getByRole("link",{name:"Science Lab",exact:true}).click();
  await expect(page.getByRole("region",{name:"Scientific processing evidence"})).toBeVisible();
  await expect(page.locator(".connected-evidence")).toContainText("not field accuracy");
  await expect(page.locator(".connected-evidence")).toContainText("2026-07-19");
  const download=page.waitForEvent("download");
  await page.getByRole("button",{name:"Download full scientific evidence"}).click();
  expect((await download).suggestedFilename()).toBe("sarpulse-scientific-evidence.json");
  await page.screenshot({path:"test-results/connected-science.png",fullPage:true});
});
