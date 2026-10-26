import {sitemapLocations} from './sitemap-helper';
import translationRecords from "../../../content/translations/pages.json";
import { test, expect } from "@playwright/test";
import core from "../../../content/pages/publication.json";
import articles from "../../../content/editorial/articles.json";
import briefs from "../../../content/editorial/first-500-inventory.json";
import { publicationInventory, published } from "../src/lib/editorial/workflow.mjs";
import { PAGE_SIZE } from "../src/lib/editorial/collections.mjs";
const pages = publicationInventory(core, articles);

test("public navigation fits narrow screens on tools and long-title guides", async ({ page }) => {
  for (const width of [320, 390]) {
    await page.setViewportSize({ width, height: 844 });
    for (const path of ["/", "/youtube-video-downloader/", "/guides/general/premiere-import-authorized-srt/"]) {
      await page.goto(path);
      for (const label of ["Downloaders", "Guides", "Resources"]) {
        await expect(page.locator(".header").getByRole("link", { name: label, exact: true })).toBeVisible();
      }
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${width}px ${path}`).toBe(true);
    }
  }
});

test("reviewed public inventory agrees with rendered metadata and sitemap", async ({ request }) => {
  test.setTimeout(90_000);
  const sitemap = await request.get("/sitemap.xml");
  expect(sitemap.status()).toBe(200);
  const locations = await sitemapLocations(request);
  expect(locations.length).toBe(pages.filter(published).length + translationRecords.filter(row=>row.status === "PUBLISHED_TRANSLATION" && row.complete && row.reviewApproved && row.englishPath !== "/faq/").length);
  expect(new Set(locations).size).toBe(locations.length);
  for (const page of pages) {
    const response = await request.get(page.path);
    expect(response.status(), page.path).toBe(200);
    expect(response.headers()["x-robots-tag"]).toBeUndefined();
    const html = await response.text();
    expect(html).toContain(`name="robots" content="${page.indexable ? "index" : "noindex"}, follow"`);
    expect(html).toContain(`rel="canonical" href="https://socialviddownloader.com${page.path}"`);
    expect(locations.includes(`https://socialviddownloader.com${page.path}`)).toBe(page.indexable);
    expect(html.match(/<h1(?:\s[^>]*)?>/g)?.length).toBe(1);
  }
  for (const path of ["/snapchat-story-downloader/", "/snapchat-story-viewer/"]) {
    expect((await request.get(path)).status()).toBe(404);
  }
  const alias = await request.get("/snapchat/", { maxRedirects: 0 });
  expect(alias.status()).toBe(308);
  expect(alias.headers()["location"]).toBe("/snapchat-downloader/");
  expect(locations).not.toContain("https://socialviddownloader.com/snapchat/");
  const robots = await (await request.get("/robots.txt")).text();
  expect(robots).toContain("Disallow: /preview/");
  expect(robots).not.toContain("Disallow: /_next");
});


test("consolidated briefs cannot render and categorized guides are reachable", async ({ page, request }) => {
  const pending = briefs.find(brief => brief.disposition.classification === "MERGE_WITH_EXISTING");
  expect(pending).toBeTruthy();
  expect((await request.get(pending!.path)).status()).toBe(404);
  await page.goto("/guides/");
  for (const platform of new Set(articles.map(article => article.platform))) {
    await expect(page.locator(`a[href="/guides/${platform}/"]`)).toBeVisible();
    const platformArticles = articles.filter(article => article.platform === platform);
    let html = "";
    for (let number = 1; number <= Math.ceil(platformArticles.length / PAGE_SIZE); number++) {
      const path = number === 1 ? `/guides/${platform}/` : `/guides/${platform}/page/${number}/`;
      const response = await request.get(path);
      expect(response.status()).toBe(200);
      const part = await response.text();
      expect(platformArticles.filter(article => part.includes(`href="${article.path}"`)).length).toBeLessThanOrEqual(PAGE_SIZE);
      html += part;
    }
    for (const article of platformArticles) expect(html).toContain(`href="${article.path}"`);
  }
  await page.goto(articles[0].path);
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(articles[0].h1);
  const downloader = articles[0].targetDownloader;
  if (!downloader) throw new Error("The tool-linked fixture must have a downloader");
  await expect(page.getByRole("link", { name: "Open the relevant downloader" })).toHaveAttribute("href", downloader);
  await expect(page.locator('script[type="application/ld+json"]')).toHaveCount(2);
  expect((await request.get("/sitemaps/999.xml")).status()).toBe(404);
  expect((await request.get("/sitemaps/0.xml")).status()).toBe(200);
  await page.goto("/guides/general/");
  await page.getByRole("link", { name: "Devices and storage" }).click();
  await expect(page.locator('a[href="/guides/general/android-downloads-folder/"]')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  for (const path of ["/guides/general/page/1/", "/guides/general/page/02/", "/topics/captions/page/999/", "/topics/not-a-family/"]) expect((await request.get(path)).status()).toBe(404);
});

test("WhatsApp education resolves without presenting a downloader", async ({ page, request }) => {
  const educational = articles.filter(article => article.platform === "whatsapp");
  expect(educational.length).toBeGreaterThan(0);
  for (const article of educational) {
    await page.goto(article.path);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(article.h1);
    await expect(page.getByRole("link", { name: "Open the relevant downloader" })).toHaveCount(0);
    await expect(page.getByRole("link", { name: "More media and privacy guidance" })).toHaveAttribute("href", "/guides/");
    await expect(page.locator('main a[href="/whatsapp-status-downloader/"]')).toHaveCount(0);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  }
  const directory = await request.get("/guides/whatsapp/");
  expect(directory.status()).toBe(200);
  expect(await directory.text()).toContain('name="robots" content="noindex, follow"');
});
