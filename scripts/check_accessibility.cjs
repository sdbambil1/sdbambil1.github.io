// WCAG 2.1 AA automated audit of built Quarto portfolio.
// Uses axe-core against each rendered page at desktop and mobile sizes.
// Reports all violations; WCAG critical/serious failures block publication.
const { chromium } = require("playwright");
const fs = require("node:fs");
const { spawn } = require("node:child_process");
const axeSource = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const origin = "http://127.0.0.1:8766";
const paths = [
  "index.html","academic.html","research.html","teaching.html",
  "conferences.html","professional-cv.html","projects.html",
  "bambaganaci.html","cv.html","contact.html",
  "evt-fireloss-references.html"
];
const server = spawn("python3", ["-m","http.server","8766","--bind","127.0.0.1","--directory","_site"], {stdio:"ignore"});
let browser;
(async()=>{
  for(let i=0;i<50;i++){
    try{if((await fetch(origin+"/index.html")).ok)break;}catch(e){}
    await new Promise(r=>setTimeout(r,250));
  }
  browser=await chromium.launch({headless:true});
  const failures=[];
  for(const width of [375,1280]){
    const context=await browser.newContext({viewport:{width,height:812},bypassCSP:true});
    const page=await context.newPage();
    for(const path of paths){
      const res=await page.goto(origin+"/"+path,{waitUntil:"domcontentloaded",timeout:25000});
      if(!res||res.status()!==200){failures.push(path+" HTTP "+res?.status());continue;}
      await page.addScriptTag({content:axeSource});
      const result=await page.evaluate(async()=>window.axe.run(document,{
        runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa","best-practice"]}
      }));
      for(const v of result.violations){
        console.log("AXE "+width+"px "+path+" "+v.impact+" "+v.id+" ("+v.nodes.length+" nodes): "+v.help);
        for(const n of v.nodes.slice(0,3)){
          console.log("  "+JSON.stringify({target:n.target,summary:n.failureSummary}).slice(0,450));
        }
        if(["critical","serious"].includes(v.impact)){
          failures.push(width+"px "+path+": "+v.impact+" "+v.id);
        }
      }
    }
    await context.close();
  }
  if(failures.length){console.error("Accessibility problems:\n"+failures.join("\n"));process.exitCode=1;}
  else{console.log("PASS: no serious or critical automated axe-core accessibility violations.");}
})().catch(e=>{console.error(e);process.exitCode=1;})
.finally(async()=>{if(browser)await browser.close().catch(()=>{});server.kill();});
