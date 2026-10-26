import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const tools = JSON.parse(
  readFileSync(
    new URL("../../../content/pages/tools.json", import.meta.url),
    "utf8",
  ),
);
describe("editorial inventory", () => {
  it("keeps a single URL per tool intent", () => {
    assert.equal(tools.length, 11);
    assert.equal(new Set(tools.map((t) => t.slug)).size, tools.length);
    assert.equal(new Set(tools.map((t) => t.name)).size, tools.length);
    assert.equal(new Set(tools.map((t) => t.description)).size, tools.length);
  });
  it("does not imply enabled support or invent media", () => {
    assert.equal(tools.filter((t) => t.status === "integrated").length, 6);
    assert.ok(
      tools
        .filter(
          (t) =>
            
            t.platform === "WhatsApp" ||
            t.kind === "Story",
        )
        .every((t) => t.capabilityState === "UNSUPPORTED"),
    );
    assert.equal(tools.find(t => t.slug === "snapchat-spotlight-downloader").capabilityState, "BETA");
    assert.equal(tools.find(t => t.platform === "TikTok").capabilityState, "BETA");
    assert.ok(tools.every((t) => t.intro.length > 100));
    assert.ok(tools.some((t) => t.platform === "WhatsApp" && t.example === ""));
  });
});


it("has no public Snapchat Story inventory or substitute keyword tool", () => {
  assert.ok(tools.filter(t => t.platform === "Snapchat").every(t => t.kind !== "Story"));
  assert.deepEqual(tools.filter(t => t.platform === "Snapchat").map(t => t.slug).sort(), ["snapchat-downloader", "snapchat-spotlight-downloader"]);
});

it("publishes only reviewed routable content with unique SEO metadata", () => {
  const pages = JSON.parse(readFileSync(new URL("../../../content/pages/publication.json", import.meta.url), "utf8"));
  assert.equal(pages.length, 24 + 23);
  assert.equal(pages.filter(page => page.indexable).length, 16 + 23);
  for (const field of ["path", "title", "description"]) {
    assert.equal(new Set(pages.map(page => page[field])).size, pages.length);
  }
  for (const tool of tools.filter(tool => tool.status !== "hub")) {
    const page = pages.find(page => page.path === `/${tool.slug}/`);
    assert.ok(page);
    assert.equal(page.indexable, ["integrated", "beta"].includes(tool.status));
  }
  assert.ok(pages.filter(page => ["/blog/", "/whatsapp/"].includes(page.path)).every(page => !page.indexable));
  assert.ok(pages.every(page => !page.path.includes("snapchat-story")));
});
