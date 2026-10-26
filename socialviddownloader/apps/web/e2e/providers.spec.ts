import { test, expect } from "@playwright/test";

test("Snapchat hub directs users to Spotlight beta without a Story tool", async ({ page }) => {
  await page.goto("/snapchat-downloader/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Snapchat Downloader");
  await expect(page.getByRole("link", { name: /Spotlight Downloader · Beta/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /Story Downloader/ })).toHaveCount(0);
  await expect(page.locator("h1, h2, h3")).not.toContainText(["Story"]);
  await page.goto("/snapchat-spotlight-downloader/");
  await expect(page.getByRole("button", { name: "Download", exact: true })).toBeEnabled();
  await expect(page.getByText(/Beta: public-link availability/)).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("temporary provider availability disables submission", async ({ page }) => {
  await page.route(/\/api\/v1\/capabilities\/?$/, route => route.fulfill({ contentType: "application/json", body: JSON.stringify({
    providers: [{ platform: "snapchat", contentTypes: { spotlight: "TEMPORARILY_UNAVAILABLE" } }],
  }) }));
  await page.goto("/snapchat-spotlight-downloader/");
  await expect(page.getByRole("button", { name: "Download", exact: true })).toBeDisabled();
  await expect(page.getByText("This tool is temporarily unavailable. Please try again later.")).toBeVisible();
});

test("internal provider observations require administrator access", async ({ page, request }) => {
  const response = await request.get("/api/admin/providers/");
  expect(response.status()).toBe(401);
  const admin = await page.goto("/admin/");
  if (admin?.status() === 404) {
    // Production has no CMS authentication implementation: the shell and
    // editorial planning records are disabled rather than publicly exposed.
    await expect(page.getByLabel("Administrator access token")).toHaveCount(0);
    expect((await request.get("/admin/content/")).status()).toBe(404);
    return;
  }
  await expect(page.getByLabel("Administrator access token")).toHaveAttribute("type", "password");
  await expect(page.getByText("platform_access_restricted", { exact: true })).toHaveCount(0);
  await page.route("**/api/admin/providers/", route => route.fulfill({ contentType: "application/json", body: JSON.stringify({ providers: [{
    provider: "tiktok", supportedContentTypes: ["video"], status: "degraded", extraction: "degraded", download: "degraded",
    lastTestStatus: "FAIL", lastFailureCategory: "platform_access_restricted", lastSuccessfulLiveTest: null,
  }] }) }));
  await page.getByLabel("Administrator access token").fill("test-only-admin-token");
  await page.getByRole("button", { name: "Load provider status" }).click();
  await expect(page.getByText("platform_access_restricted", { exact: true })).toBeVisible();
  await expect(page.getByLabel("Administrator access token")).toHaveValue("");
});


test("retired Snapchat Story routes, public links and sitemap are absent", async ({ page, request }) => {
  for (const route of ["snapchat-story-downloader", "snapchat-story-viewer", "download-snapchat-story", "snap-story-downloader"]) {
    const response = await request.get(`/${route}/`);
    expect(response.status()).toBe(404);
    expect(await response.text()).not.toContain('rel="canonical" href="https://socialviddownloader.com/' + route);
  }
  const sitemap = await request.get("/sitemap.xml");
  expect(sitemap.status()).toBe(200);
  expect(await sitemap.text()).not.toContain("snapchat-story");
  for (const route of ["/", "/snapchat-downloader/", "/snapchat-spotlight-downloader/"]) {
    await page.goto(route);
    await expect(page.locator('a[href*="snapchat-story"], a[href*="snap-story"], a[href*="download-snapchat-story"]')).toHaveCount(0);
    await expect(page.getByText("Snapchat Story Downloader", { exact: true })).toHaveCount(0);
    for (const data of await page.locator('script[type="application/ld+json"]').allTextContents()) expect(data).not.toContain("snapchat-story");
  }
});
