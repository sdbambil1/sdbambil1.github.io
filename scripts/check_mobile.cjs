// Automated viewport audit of the built Quarto site (GitHub Actions).
// Checks 320, 375, 768, and 1280px widths without changing the website.
const { chromium } = require("playwright");
const { spawn } = require("node:child_process");

const ORIGIN = "http://127.0.0.1:8765";
const pages = [
  "index.html",
  "academic.html",
  "research.html",
  "teaching.html",
  "conferences.html",
  "professional-cv.html",
  "projects.html",
  "bambaganaci.html",
  "cv.html",
  "contact.html"
];
const widths = [320, 375, 768, 1280];

const server = spawn("python3", ["-m", "http.server", "8765", "--bind", "127.0.0.1", "--directory", "_site"], { stdio: "ignore" });
let browser;
async function ready(url) {
  for (let i = 0; i < 45; i++) {
    try { const r = await fetch(url); if (r.ok) return; } catch (_) {}
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  throw new Error("Local preview server did not start");
}
(async () => {
  await ready(ORIGIN + "/index.html");
  browser = await chromium.launch({ headless: true });
  let failures = [];
  for (const width of widths) {
    const context = await browser.newContext({
      viewport: { width, height: 812 },
      deviceScaleFactor: 1
    });
    const page = await context.newPage();
    for (const path of pages) {
      const response = await page.goto(ORIGIN + "/" + path, {
        waitUntil: "domcontentloaded",
        timeout: 25000
      });
      if (response.status() !== 200) {
        failures.push(width + "px " + path + ": HTTP " + response.status());
        continue;
      }
      const m = await page.evaluate(() => ({
        width: window.innerWidth,
        scroll: document.documentElement.scrollWidth,
        body: document.body.scrollWidth,
        viewportTag: !!document.querySelector('meta[name="viewport"]')
      }));
      const overflow = Math.max(m.scroll, m.body) - m.width;
      console.log(width + "px " + path + ": overflow " + overflow + "px");
      if (overflow > 2) {
        failures.push(width + "px " + path + ": horizontal overflow " + overflow + "px");
      }
      if (!m.viewportTag) {
        failures.push(width + "px " + path + ": missing viewport meta");
      }
      if (width <= 375 && path === "index.html") {
        const toggler = page.locator("button.navbar-toggler").first();
        if (await toggler.count() === 0) {
          failures.push(width + "px: no responsive navigation toggle");
        } else {
          if (await toggler.isVisible()) {
            await toggler.click();
            const menu = page.locator(".navbar-collapse").first();
            if (!(await menu.isVisible())) {
              failures.push(width + "px: menu did not open");
            }
          } else {
            failures.push(width + "px: responsive navigation toggle is hidden");
          }
        }
      }
    }
    await context.close();
  }
  // Check documentation page is real and reachable through its link.
  const tab = await browser.newPage();
  await tab.goto(ORIGIN + "/projects.html");
  const docs = tab.getByRole("link", {
    name: "Package documentation and reproducible examples"
  });
  if (await docs.count() !== 1) {
    failures.push("Software page: documentation link missing or duplicated");
  } else {
    await docs.click();
    if (!tab.url().endsWith("/bambaganaci.html")) {
      failures.push("Software documentation link navigates to " + tab.url());
    }
    if (!(await tab.getByText("Supported confidence intervals").count())) {
      failures.push("Software documentation content missing");
    }
  }
  await browser.close();
  if (failures.length) {
    console.error("Responsive checks failed:\n" + failures.join("\n"));
    process.exitCode = 1;
  } else {
    console.log("Passed responsive checks for " + pages.length + " pages at " + widths.join(", ") + "px.");
  }
})().catch(err => { console.error(err); process.exitCode = 1; })
.finally(async () => { if (browser) await browser.close().catch(()=>{}); server.kill(); });
