import { chromium } from "playwright";

const OUT_DIR = "../output/screenshots";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

await page.goto("http://localhost:5173", { waitUntil: "networkidle" });
await page.waitForSelector(".ticket-card");

for (const id of [101, 102, 103]) {
  const card = page.locator(".ticket-card", { hasText: `#${id}` });
  await card.click();
  // wait for the summary panel to reflect the selected ticket's decision
  await page.waitForTimeout(500);
  await page.screenshot({ path: `${OUT_DIR}/ticket_${id}.png`, fullPage: true });
  console.log(`saved ticket_${id}.png`);
}

await browser.close();
