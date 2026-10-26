import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
let folder: string;
let low: Buffer;
let high: Buffer;
test.beforeAll(() => {
  folder = mkdtempSync(join(tmpdir(), "socialvid-e2e-"));
  for (const [name, dimensions] of [
    ["low", "640x360"],
    ["high", "1280x720"],
  ]) {
    execFileSync("ffmpeg", [
      "-v",
      "error",
      "-y",
      "-f",
      "lavfi",
      "-i",
      `testsrc=size=${dimensions}:rate=5`,
      "-f",
      "lavfi",
      "-i",
      "sine=frequency=440",
      "-t",
      "1",
      "-c:v",
      "libx264",
      "-pix_fmt",
      "yuv420p",
      "-c:a",
      "aac",
      "-movflags",
      "+faststart",
      join(folder, `${name}.mp4`),
    ]);
  }
  low = readFileSync(join(folder, "low.mp4"));
  high = readFileSync(join(folder, "high.mp4"));
});
test.afterAll(() => rmSync(folder, { recursive: true, force: true }));
test("real quality choices, preparation, video preview, and file save", async ({
  page,
}) => {
  const token = "a".repeat(32);
  const job = "b".repeat(32);
  let chosen = "";
  let polls = 0;
  await page.route(/\/api\/v1\/extract\/?$/, (route) =>
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        sessionId: token,
        platform: "youtube",
        title: "Generated test video",
        creator: "Test fixture",
        duration: 1,
        thumbnail: null,
        formats: [
          {
            id: "c".repeat(20),
            quality: "720p HD",
            height: 720,
            extension: "mp4",
            filesize: high.length,
            estimatedFilesize: null,
            requiresMerge: false,
            hasAudio: true,
          },
          {
            id: "d".repeat(20),
            quality: "360p",
            height: 360,
            extension: "mp4",
            filesize: low.length,
            estimatedFilesize: null,
            requiresMerge: false,
            hasAudio: true,
          },
        ],
      }),
    }),
  );
  await page.route(/\/api\/v1\/download\/?$/, (route) => {
    chosen = route.request().postDataJSON().formatId;
    return route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        status: "queued",
        jobId: job,
        statusUrl: `/api/v1/jobs/${job}/`,
      }),
    });
  });
  await page.route(/\/api\/v1\/jobs\//, (route) =>
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(
        ++polls === 1
          ? { success: true, status: "processing" }
          : {
              success: true,
              status: "ready",
              filename: "test.mp4",
              filesize: chosen === "c".repeat(20) ? high.length : low.length,
              downloadUrl: `/api/v1/files/${job}/`,
              previewUrl: `/api/v1/files/${job}/?inline=1`,
            },
      ),
    }),
  );
  await page.route(/\/api\/v1\/files\//, (route) =>
    route.fulfill({
      contentType: "video/mp4",
      headers: {
        "Content-Disposition": route.request().url().includes("inline=1")
          ? "inline"
          : 'attachment; filename="test.mp4"',
      },
      body: chosen === "c".repeat(20) ? high : low,
    }),
  );
  await page.goto("/youtube-video-downloader/");
  await page
    .getByRole("textbox", { name: "Video URL" })
    .fill("https://youtube.com/watch?v=BaW_jenozKc");
  await page.getByRole("button", { name: "Download", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Generated test video" }),
  ).toBeVisible();
  await expect(page.getByRole("radio")).toHaveCount(2);
  await expect(page.getByText("4K", { exact: true })).toHaveCount(0);
  await page.getByRole("radio").nth(1).check();
  await page.getByRole("button", { name: "Prepare 360p" }).click();
  await expect(page.getByRole("link", { name: /Save file/ })).toBeVisible({
    timeout: 15000,
  });
  expect(chosen).toBe("d".repeat(20));
  const video = page.locator("video");
  await expect(video).toBeVisible();
  await expect
    .poll(() =>
      video.evaluate((element: HTMLVideoElement) => element.videoHeight),
    )
    .toBe(360);
  const pending = page.waitForEvent("download");
  await page.getByRole("link", { name: /Save file/ }).click();
  const download = await pending;
  const path = await download.path();
  expect(readFileSync(path!)).toEqual(low);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
test("late extraction responses cannot replace a cleared link", async ({
  page,
}) => {
  await page.route(/\/api\/v1\/extract\/?$/, async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 300));
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        sessionId: "a".repeat(32),
        platform: "youtube",
        title: "Stale result",
        thumbnail: null,
        duration: null,
        creator: null,
        formats: [],
      }),
    });
  });
  await page.goto("/");
  await page
    .getByRole("textbox", { name: "Video URL" })
    .fill("https://youtu.be/BaW_jenozKc");
  await page.getByRole("button", { name: "Download", exact: true }).click();
  await page.getByRole("button", { name: "Clear URL" }).click();
  await expect(page.getByRole("textbox", { name: "Video URL" })).toHaveValue(
    "",
  );
  await expect(page.getByRole("heading", { name: "Stale result" })).toHaveCount(
    0,
  );
});
