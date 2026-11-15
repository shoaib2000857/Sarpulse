import fs from "node:fs/promises";
import path from "node:path";
import http from "node:http";
import { chromium } from "../web/node_modules/playwright/index.mjs";

const root=path.resolve("web/dist");
const types={".html":"text/html",".json":"application/json",".png":"image/png",".js":"text/javascript",".css":"text/css"};
const server=http.createServer(async(req,res)=>{try{let relative=decodeURIComponent(new URL(req.url,"http://localhost").pathname);if(relative.endsWith("/"))relative+="index.html";const file=path.resolve(root,"."+relative);if(!file.startsWith(root+path.sep))throw Error();const bytes=await fs.readFile(file);res.setHeader("content-type",types[path.extname(file)]??"application/octet-stream");res.end(bytes);}catch{res.writeHead(404);res.end("Not found");}});
await new Promise(resolve=>server.listen(5197,"127.0.0.1",resolve));
const browser=await chromium.launch({channel:"chrome",headless:true});
try {
  const page=await browser.newPage({viewport:{width:1280,height:720}});
  await page.goto("http://127.0.0.1:5197/demo/");
  await page.waitForFunction(()=>document.documentElement.dataset.ready==="true");
  await page.locator("img").evaluateAll(images=>Promise.all(images.map(img=>img.decode())));
  await fs.mkdir("build/demo-slides",{recursive:true});
  await page.addStyleTag({content:"nav{visibility:hidden}"});
  for(let i=0;i<7;i++){
    const slide=page.locator(".slide:not([hidden])");
    await slide.screenshot({path:`build/demo-slides/slide-${i+1}.png`});
    if(i<6)await page.keyboard.press("ArrowRight");
  }
  await fs.mkdir("web/public/demo",{recursive:true});
  await page.pdf({path:"web/public/demo/sarpulse-demo.pdf",width:"13.333in",height:"7.5in",printBackground:true,preferCSSPageSize:true});
  console.log("Rendered seven-slide public web demo and PDF.");
}finally{await browser.close();server.close();}
