#!/usr/bin/env node
// Capture the real site with Playwright. BASE_URL can point to a local server.
// Requires: playwright, Chromium and ImageMagick (`magick`).
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
let chromium;
try {
  ({ chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright'));
} catch (error) {
  // This development machine already has Playwright in the sibling project.
  const sibling = path.resolve(root, '../kanvas/node_modules/playwright');
  if (!fs.existsSync(sibling)) throw error;
  ({ chromium } = require(sibling));
}
const media = path.join(root, 'media');
const base = (process.env.BASE_URL || 'https://lietuva.chat').replace(/\/$/, '');
const lang = (process.env.CAPTURE_LANG || 'en').toLowerCase();
const gifName = process.env.GIF_NAME || (lang === 'en' ? 'lietuva-landing.gif' : `lietuva-landing-${lang}.gif`);
const gifOnly = process.env.GIF_ONLY === '1';
const framesDir = fs.mkdtempSync(path.join(os.tmpdir(), 'lietuva-frames-'));
const question = lang === 'lt' ? 'Kas yra „Sodra“ Lietuvoje?' : 'What is Sodra in Lithuania?';
const headingMark = lang === 'lt' ? 'Lietuvoje' : 'Lithuania';

async function main() {
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
    });
    const page = await browser.newPage({ viewport: { width: 1280, height: 627 }, deviceScaleFactor: 1 });
    await page.emulateMedia({ reducedMotion: 'no-preference' });
    await page.goto(`${base}/set-lang/${lang}`, { waitUntil: 'domcontentloaded' });
    await page.locator('.home-question').waitFor();
    const heading = await page.locator('.home-question').innerText();
    if (!heading.includes(headingMark)) {
      throw new Error(`Expected a ${lang} heading containing "${headingMark}", got: ${heading}`);
    }
    await page.evaluate(() => document.fonts.ready.then(() => true));
    await page.screenshot({ path: path.join(media, `lietuva-home-${lang}.png`) });

    // Hold on the hero long enough for the saulė to draw (2.4s), then scroll.
    const scrollEnd = await page.evaluate(() => Math.min(document.documentElement.scrollHeight - innerHeight, 2200));
    const positions = [
      ...Array(36).fill(0),
      ...Array.from({ length: 48 }, (_, i) => Math.round(scrollEnd * i / 47)),
      ...Array(12).fill(scrollEnd),
    ];
    const frames = [];
    for (let i = 0; i < positions.length; i++) {
      await page.evaluate(y => scrollTo(0, y), positions[i]);
      await page.waitForTimeout(70);
      const frame = path.join(framesDir, `${String(i).padStart(3, '0')}.png`);
      await page.screenshot({ path: frame });
      frames.push(frame);
    }
    const gif = path.join(media, gifName);
    const result = spawnSync('magick', ['-delay', '8', ...frames, '-loop', '0', '-layers', 'Optimize', gif], { encoding: 'utf8' });
    if (result.status !== 0) throw new Error(`ImageMagick failed: ${result.stderr || result.error}`);
    console.log(`Wrote ${gif} (${lang}) from ${base}`);
    if (gifOnly) return;

    await page.locator('#topics').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(media, 'lietuva-topics.png') });

    await page.goto(`${base}/app`, { waitUntil: 'domcontentloaded' });
    await page.locator('#chat-input').waitFor();
    await page.evaluate(() => document.fonts.ready.then(() => true));
    await page.screenshot({ path: path.join(media, 'lietuva-chat.png') });
    await page.locator('#chat-input').fill(question);
    await page.locator('#send-btn').click();
    await page.locator('.msg-assistant .msg-sources a').first().waitFor({ timeout: 120000 });
    await page.waitForFunction(() => !document.querySelector('.msg-assistant .msg-bubble.streaming'));
    await page.screenshot({ path: path.join(media, 'lietuva-answer.png') });
    console.log(`Captured screenshots and ${gif} from ${base}`);
  } finally {
    if (browser) await browser.close();
    fs.rmSync(framesDir, { recursive: true, force: true });
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
