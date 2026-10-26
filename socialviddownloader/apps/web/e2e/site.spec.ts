import { test, expect } from "@playwright/test";
test("homepage, validation, and responsive layout", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "Download social media",
  );
  await page
    .getByRole("textbox", { name: "Video URL" })
    .fill("https://evil.example/video");
  await expect(page.locator("#download-message")).toContainText(
    "not supported",
  );
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
test("real API errors are displayed without fake success", async ({ page }) => {
  await page.route(/\/api\/v1\/extract\/?$/, (route) =>
    route.fulfill({
      status: 501,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        error: {
          code: "provider_disabled",
          message: "This YouTube content type is not currently supported.",
        },
      }),
    }),
  );
  await page.goto("/youtube-shorts-downloader/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(
    "YouTube Shorts Downloader",
  );
  await page
    .getByRole("textbox", { name: "Video URL" })
    .fill("https://youtube.com/shorts/test");
  await page.getByRole("button", { name: "Download", exact: true }).click();
  await expect(page.locator("#download-message")).toContainText(
    "not currently supported",
  );
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
    "content",
    /^index, follow$/,
  );
});
test("tool routes and 404", async ({ page }) => {
  for (const path of [
    "instagram-video-downloader",
    "facebook-reels-downloader",
    "snapchat-spotlight-downloader",
    "whatsapp-status-downloader",
  ]) {
    await page.goto(`/${path}/`);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  }
  const response = await page.goto("/missing-tool/");
  expect(response?.status()).toBe(404);
});

test("server proxy returns a real API response and enforces payload limits", async ({
  request,
}) => {
  const response = await request.post("/api/v1/extract/", {
    data: { url: "https://unsupported.example/video" },
  });
  expect([400, 503]).toContain(response.status());
  expect((await response.json()).success).toBe(false);
  const oversized = await request.post("/api/v1/extract/", {
    data: "x".repeat(9000),
  });
  expect(oversized.status()).toBe(413);
  const unknown = await request.post("/api/v1/private-service/");
  expect(unknown.status()).toBe(404);
});
