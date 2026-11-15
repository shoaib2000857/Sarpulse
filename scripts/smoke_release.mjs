import { chromium } from "../web/node_modules/playwright/index.mjs";
import assert from "node:assert/strict";
import fs from "node:fs/promises";

const base=process.argv[2]??"http://127.0.0.1:8011";
for(let attempt=0;attempt<20;attempt++){
  try{const response=await fetch(base+"/");if(response.ok)break;}catch{}
  if(attempt===19)throw Error("Release server did not become ready");
  await new Promise(resolve=>setTimeout(resolve,500));
}
const browser=await chromium.launch({channel:"chrome",headless:true,args:["--enable-webgl","--use-angle=swiftshader","--enable-unsafe-swiftshader"]});
try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  await page.goto(base+"/#explore");
  const picker=page.getByRole("combobox",{name:"Scientific investigation"});
  await picker.waitFor();await picker.selectOption("brahmaputra-majuli");
  await page.getByRole("heading",{name:/Brahmaputra/}).waitFor();
  await page.waitForFunction(()=>document.querySelector(".data-banner")?.textContent.includes("NASA NISAR observations"));
  await page.getByRole("radio",{name:"Grid",exact:true}).check();
  await page.waitForFunction(()=>document.querySelector(".geo-workspace")?.getAttribute("data-map-status")==="ready");
  assert.match(await page.locator(".raster-state").innerText(),/Supplied radar image/);
  await page.locator(".maplibregl-canvas").first().click({position:{x:400,y:300}});
  await page.getByRole("button",{name:"Download Change Passport"}).waitFor();
  assert.match(await page.locator(".change-passport").innerText(),/Observed/);
  await fs.mkdir("build/release-check",{recursive:true});
  await page.screenshot({path:"build/release-check/explorer.png",fullPage:true});
  const health=await page.request.get(base+"/api/health");
  if(health.ok()){
    assert.equal((await health.json()).sites.length,2);
    const p=await page.request.get(base+"/api/sites/brahmaputra-majuli/passport?lon=94.1&lat=26.95");
    assert.equal(p.status(),200);assert.ok((await p.json()).evidence[0].values.sample_distance_km<0.05);
    console.log("Exact-pixel API passport passed.");
  }
  const demo=await page.request.get(base+"/demo/");assert.equal(demo.status(),200);
  const pdf=await page.request.get(base+"/demo/sarpulse-demo.pdf");assert.equal(pdf.status(),200);
  console.log("Complete release smoke passed: real images, live/static passport, two-site bundle and public demo assets.");
}finally{await browser.close();}
