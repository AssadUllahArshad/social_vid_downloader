import { test, expect } from "@playwright/test";

test("public routes receive protective headers without hiding public assets", async ({ request }) => {
  const response = await request.get("/");
  expect(response.status()).toBe(200);
  expect(response.headers()["x-content-type-options"]).toBe("nosniff");
  expect(response.headers()["x-frame-options"]).toBe("DENY");
  expect(response.headers()["content-security-policy"]).toContain("frame-ancestors 'none'");
  expect((await request.get("/favicon.svg")).status()).toBe(200);
  const robots = await request.get("/robots.txt");
  const text = await robots.text();
  expect(text).toContain("Allow: /");
  expect(text).toContain("Disallow: /admin");
  expect(text).toContain("https://socialviddownloader.com/sitemap.xml");
});

test("download API errors remain private and uncached", async ({ request }) => {
  const response = await request.post("/api/v1/extract/", { data: { url: "http://localhost" } });
  expect([400, 503]).toContain(response.status());
  expect(response.headers()["cache-control"]).toBe("no-store");
  expect(response.headers()["x-content-type-options"]).toBe("nosniff");
  const body = await response.text();
  expect(body).not.toMatch(/Traceback|redis:\/\/|\/Users\/|yt_dlp|ffmpeg -/);
});
