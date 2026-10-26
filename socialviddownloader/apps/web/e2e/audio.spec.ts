import arMessages from "../src/locales/ar.json";
import urMessages from "../src/locales/ur.json";
import { test, expect, type Page } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const english = "a".repeat(20), hindi = "b".repeat(20), spanish = "c".repeat(20);
const quality = "d".repeat(20), lowQuality = "e".repeat(20);
const session = "a".repeat(32), job = "b".repeat(32);
const tracks = [
  {id: english, language_code: "en", language_name: "English", label: "English · Original, Default", is_default: true, is_original: true, codec: "aac", bitrate: 128000},
  {id: hindi, language_code: "hi", language_name: "Hindi", label: "Hindi", is_default: false, is_original: false, codec: "aac", bitrate: 128000},
  {id: spanish, language_code: "es", language_name: "Spanish", label: "Spanish", is_default: false, is_original: false, codec: "aac", bitrate: 128000},
];
let folder: string;
let dualFile: Buffer;
let singleFile: Buffer;
let mkvFile: Buffer;
test.beforeAll(() => {
  folder = mkdtempSync(join(tmpdir(), "socialvid-audio-e2e-"));
  const dual = join(folder, "dual.mp4");
  execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=5",
    "-f", "lavfi", "-i", "sine=frequency=440", "-f", "lavfi", "-i", "sine=frequency=660", "-t", "1",
    "-map", "0:v", "-map", "1:a", "-map", "2:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
    "-metadata:s:a:0", "language=eng", "-metadata:s:a:1", "language=hin", "-disposition:a:0", "default", "-disposition:a:1", "0", "-movflags", "+faststart", dual]);
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", dual, "-map", "0:v", "-map", "0:a:1", "-c", "copy", "-disposition:a:0", "default", "-movflags", "+faststart", join(folder, "single.mp4")]);
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", dual, "-map", "0:v", "-map", "0:a", "-c:v", "copy", "-c:a:0", "copy", "-c:a:1", "libopus", join(folder, "dual.mkv")]);
  dualFile = readFileSync(dual); singleFile = readFileSync(join(folder, "single.mp4")); mkvFile = readFileSync(join(folder, "dual.mkv"));
});
test.afterAll(() => rmSync(folder, {recursive: true, force: true}));

function extracted(audioTracks: Array<Omit<(typeof tracks)[number], "language_code"> & {language_code: string | null}> = tracks, mkv = false) {
  const containers = Object.fromEntries(audioTracks.map(track => [track.id, mkv && track.id === hindi ? "mkv" : "mp4"]));
  return {success: true, sessionId: session, platform: "youtube", title: "Generated multilingual test video", thumbnail: null, creator: "Test fixture", duration: 1,
    audio_tracks: audioTracks, supports_dual_audio: audioTracks.length > 1,
    formats: [{id: quality, quality: "360p", height: 360, extension: "mp4", filesize: null, estimatedFilesize: null,
      hasAudio: true, requiresMerge: true, audio_track_ids: audioTracks.map(track => track.id), default_audio_track_id: audioTracks[0]?.id,
      audio_containers: containers, supports_dual_audio: audioTracks.length > 1},
      {id: lowQuality, quality: "90p", height: 90, extension: "mp4", filesize: null, estimatedFilesize: null,
        hasAudio: true, requiresMerge: false, audio_track_ids: [audioTracks[0]?.id], default_audio_track_id: audioTracks[0]?.id,
        audio_containers: {[audioTracks[0]?.id]: "mp4"}, supports_dual_audio: false}]};
}
async function analyze(page: Page, result = extracted()) {
  await page.route(/\/api\/v1\/extract\/?$/, route => route.fulfill({contentType: "application/json", body: JSON.stringify(result)}));
  await page.goto("/youtube-video-downloader/");
  await page.getByRole("textbox", {name: "Video URL"}).fill("https://youtube.com/watch?v=BaW_jenozKc");
  await page.getByRole("button", {name: "Download", exact: true}).click();
  await expect(page.getByRole("heading", {name: "Generated multilingual test video"})).toBeVisible();
}
async function downloads(page: Page, mkv = false) {
  let sent: {audio_mode: string; audio_track_ids: string[]} | undefined;
  await page.route(/\/api\/v1\/download\/?$/, route => {
    sent = route.request().postDataJSON();
    return route.fulfill({status: 202, contentType: "application/json", body: JSON.stringify({success: true, statusUrl: `/api/v1/jobs/${job}/`})});
  });
  await page.route(/\/api\/v1\/jobs\//, route => route.fulfill({contentType: "application/json", body: JSON.stringify({success: true, status: "ready",
    filename: mkv ? "dual.mkv" : "video.mp4", extension: mkv ? "mkv" : "mp4", filesize: mkv ? mkvFile.length : sent?.audio_mode === "dual" ? dualFile.length : singleFile.length,
    audio_mode: sent?.audio_mode, audio_tracks: tracks.filter(track => sent?.audio_track_ids.includes(track.id)),
    previewUrl: `/api/v1/files/${job}/?inline=1`, downloadUrl: `/api/v1/files/${job}/`})}));
  await page.route(/\/api\/v1\/files\//, route => route.fulfill({contentType: mkv ? "video/x-matroska" : "video/mp4",
    headers: {"Content-Disposition": route.request().url().includes("inline=1") ? "inline" : `attachment; filename="${mkv ? "dual.mkv" : "video.mp4"}"`},
    body: mkv ? mkvFile : sent?.audio_mode === "dual" ? dualFile : singleFile}));
  return () => sent;
}

test("audio options are source-driven and dual tracks are saved separately", async ({page}) => {
  const sent = await downloads(page);
  await analyze(page);
  await expect(page.getByLabel("Audio", {exact: true}).locator("option")).toHaveCount(3);
  await expect(page.locator(".audio-controls")).not.toContainText(["Arabic", "French", "German"]);
  await page.getByRole("radio", {name: "Dual Audio", exact: true}).check();
  await expect(page.getByLabel("Primary Audio")).toHaveValue(english);
  await page.getByLabel("Secondary Audio").selectOption(hindi);
  await expect(page.getByLabel("Secondary Audio").locator(`option[value="${english}"]`)).toHaveCount(0);
  await page.getByRole("button", {name: "Download 360p Dual Audio"}).click();
  await expect(page.getByRole("link", {name: /Save file/})).toBeVisible({timeout: 15000});
  expect(sent()).toMatchObject({audio_mode: "dual", audio_track_ids: [english, hindi]});
  const pending = page.waitForEvent("download");
  await page.getByRole("link", {name: /Save file/}).click();
  const saved = await pending;
  const path = (await saved.path())!;
  expect(readFileSync(path)).toEqual(dualFile);
  const probe = JSON.parse(execFileSync("ffprobe", ["-v", "error", "-show_streams", "-of", "json", path], {encoding: "utf8"}));
  expect(probe.streams.filter((stream: {codec_type: string}) => stream.codec_type === "audio").map((stream: {tags: {language: string}}) => stream.tags.language)).toEqual(["eng", "hin"]);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("single audio sends the chosen language and clears an earlier prepared file", async ({page}) => {
  const sent = await downloads(page);
  await analyze(page);
  await page.getByLabel("Audio", {exact: true}).selectOption(hindi);
  await page.getByRole("button", {name: "Download 360p with Hindi"}).click();
  await expect(page.getByRole("link", {name: /Save file/})).toBeVisible({timeout: 15000});
  expect(sent()).toMatchObject({audio_mode: "single", audio_track_ids: [hindi]});
  const pending = page.waitForEvent("download");
  await page.getByRole("link", {name: /Save file/}).click();
  const saved = await pending;
  const probe = JSON.parse(execFileSync("ffprobe", ["-v", "error", "-show_streams", "-of", "json", (await saved.path())!], {encoding: "utf8"}));
  expect(probe.streams.filter((stream: {codec_type: string}) => stream.codec_type === "audio").map((stream: {tags: {language: string}}) => stream.tags.language)).toEqual(["hin"]);
  await page.getByLabel("Audio", {exact: true}).selectOption(spanish);
  await expect(page.getByRole("link", {name: /Save file/})).toHaveCount(0);
});

test("one unknown-language audio stays compact without invented languages", async ({page}) => {
  await analyze(page, extracted([{...tracks[0], language_code: null, language_name: "Unknown", label: "Original", is_default: false, is_original: false}]));
  await expect(page.getByText("Audio: Original", {exact: true})).toBeVisible();
  await expect(page.locator(".audio-controls")).toHaveCount(0);
  await expect(page.getByRole("radio", {name: "Dual Audio", exact: true})).toHaveCount(0);
  await expect(page.getByRole("button", {name: "Prepare 360p"})).toBeVisible();
});

test("quality changes reset an incompatible dual-audio selection", async ({page}) => {
  await analyze(page);
  await page.getByRole("radio", {name: "Dual Audio", exact: true}).check();
  await page.getByRole("radio", {name: /90p/}).check();
  await expect(page.locator(".audio-controls")).toHaveCount(0);
  await expect(page.getByRole("button", {name: "Prepare 90p"})).toBeVisible();
  await expect(page.locator(".audio-output")).toContainText("MP4");
});

test("required MKV output is explained before preparation and after ready", async ({page}) => {
  await downloads(page, true);
  await analyze(page, extracted(tracks, true));
  await page.getByRole("radio", {name: "Dual Audio", exact: true}).check();
  await page.getByLabel("Secondary Audio").selectOption(hindi);
  await expect(page.locator(".audio-output")).toContainText("MKV is required");
  await page.getByRole("button", {name: "Download 360p Dual Audio"}).click();
  await expect(page.getByRole("link", {name: /Save file/})).toBeVisible({timeout: 15000});
  await expect(page.locator("video")).toHaveCount(0);
  await expect(page.getByText(/MKV preview is unavailable/)).toBeVisible();
});

test("RTL localized quality, dual audio and genuine prepared preview keep the shared download contract", async ({page}) => {
 for(const [locale,messages] of [["ar",arMessages],["ur",urMessages]] as const) {
  const sent=await downloads(page);
  await page.route(/\/api\/v1\/extract\/?$/,route=>route.fulfill({json:extracted()}));
  await page.goto(`/${locale}/youtube-video-downloader/`);
  await page.locator('input[type=url]').fill('https://youtube.com/watch?v=BaW_jenozKc');
  await page.locator('button[type=submit]').click();
  await expect(page.locator('.format-option')).toHaveCount(2);
  await page.getByRole('radio',{name:messages.dual,exact:true}).check();
  await page.getByLabel(messages.secondary,{exact:true}).selectOption(hindi);
  await page.locator('.prepare-button').click();
  await expect(page.locator('.ready-file video')).toBeVisible({timeout:15000});
  expect(sent()).toMatchObject({audio_mode:'dual',audio_track_ids:[english,hindi]});
  await expect(page.locator('.ready-file a')).toContainText(messages.save);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
 }
});
