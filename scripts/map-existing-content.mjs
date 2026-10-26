import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { publicationInventory, published } from "../apps/web/src/lib/editorial/workflow.mjs";
import { createHash } from "node:crypto";
const load = path => JSON.parse(readFileSync(path, "utf8"));
const core = load("content/pages/publication.json");
const articles = load("content/editorial/articles.json");
const audit = load("docs/content-system-audit.json");
const graph = audit.pages;
const records = new Map([...core, ...articles].map(page => [page.path, page]));
const baseline = publicationInventory(core, articles).filter(published).map(page => ({
  ...page, ...records.get(page.path),
  id: records.get(page.path)?.id || `SVD-CORE-${createHash("sha256").update(page.path).digest("hex").slice(0, 10)}`,
  links: graph.find(row => row.path === page.path)?.links || [],
}));
const auditedIndexable = graph.filter(page => page.indexable && page.status === 200);
if (baseline.length !== auditedIndexable.length || baseline.some(page => !auditedIndexable.some(row => row.path === page.path))) throw new Error("Refresh HTTP audit before mapping: resolver and audit disagree");
if (existsSync("docs/existing-content-semantic-map.json")) {
  const previous = load("docs/existing-content-semantic-map.json");
  const archive = `docs/existing-content-semantic-map-${previous.baselineIndexable}-baseline.json`;
  if (!existsSync(archive)) writeFileSync(archive, JSON.stringify(previous, null, 2) + "\n");
}
const clean = text => text.replace(/<script\b[^>]*>[\s\S]*?<\/script>/g, " ").replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/\s+/g, " ").trim();
const lexicons = {
  deviceTopics: ["iPhone", "iPad", "Android", "Windows", "Mac", "Chromebook", "USB", "cloud", "Files", "Photos", "storage"],
  browserTopics: ["Chrome", "Safari", "Firefox", "Edge", "browser", "preview", "private browsing", "embedded"],
  formats: ["MP4", "WebM", "MKV", "MOV", "M4A", "4K", "1080p", "720p", "2160p", "portrait"],
  codecs: ["H.264", "HEVC", "VP9", "AV1", "AAC", "Opus"],
  audioTopics: ["stereo", "dual audio", "multi-audio", "language", "default", "original", "dub", "description", "subtitles", "sample rate"],
  subtitleTopics: ["subtitles", "captions", "SRT", "WebVTT", "sidecar", "timing", "encoding"],
  qualityTopics: ["resolution", "bitrate", "frame rate", "4K", "1080p", "720p", "HDR", "SDR"],
  copyrightPrivacy: ["permission", "private", "password", "copyright", "DRM", "authentication", "credentials", "watermark"],
};
const rows = [];
for (const record of baseline) {
  const response = await fetch(`http://127.0.0.1:3000${record.path}`);
  if (response.status !== 200) throw new Error(`Baseline not public: ${record.path}`);
  const html = await response.text();
  const main = html.match(/<main\b[^>]*>([\s\S]*?)<\/main>/)?.[1] || html;
  const text = clean(main);
  const headings = [...main.matchAll(/<h[23]\b[^>]*>([\s\S]*?)<\/h[23]>/g)].map(match => clean(match[1]));
  const row = { id: record.id, path: record.path, title: record.title, type: record.type || "article", platform: record.platform, family: record.family || record.type, primaryIntent: record.intent || (record.type === "tool" ? `Validate and process one authorized ${record.title.replace(/ Downloader$/, "")} link using actual formats` : record.type === "hub" ? `Choose the available ${record.title} content type and understand access limits` : record.description), primaryQuery: record.primaryKeyword || record.title, secondaryQueries: record.secondaryKeywords || [], secondaryIntents: record.secondaryIntents || (record.sections || []).map(section => section.heading), relatedPages: record.related || [], questionsAnswered: [record.title, ...(record.faq || []).map(faq => faq.question), ...headings], answerEvidence: record.intro || record.description, headings, troubleshootingTopics: headings.filter(heading => /check|troubleshoot|fail|problem|verify|unavailable/i.test(heading)), comparisons: /versus| vs |compare/i.test(record.title) ? [record.title] : headings.filter(heading => /compare|distinguish|separate|difference/i.test(heading)), targetTool: record.targetDownloader || (record.type === "tool" ? record.path : null), incoming: graph.filter(page => page.links.includes(record.path)).map(page => page.path), outgoing: record.links || [] };
  for (const [field, words] of Object.entries(lexicons)) row[field] = words.filter(word => text.toLowerCase().includes(word.toLowerCase()));
  rows.push(row);
}
writeFileSync("docs/existing-content-semantic-map.json", JSON.stringify({ baselineIndexable: rows.length, generatedAt: new Date().toISOString(), scope: "Current eligible public pages; mentions are coverage evidence, not proof of an exhaustive answer", pages: rows }, null, 2)+"\n");
const lines = ["# Existing-content semantic map", "", `Current verified baseline: **${rows.length} indexable pages**. Derived from canonical content and actual production-rendered main content. Questions include primary topics and explanatory section headings; a detected device/codec mention does not establish exhaustive task coverage. New candidate review must examine the answer evidence and headings, not only term overlap. No search volumes or observed SERP similarity are claimed.`, ""];
for (const row of rows) {
  lines.push(`## ${row.id} · ${row.path}`, "");
  for (const [field, value] of Object.entries(row).filter(([key]) => !["id", "path"].includes(key))) lines.push(`- **${field}:** ${Array.isArray(value) ? value.join("; ") || "None observed" : value || "Not applicable"}`);
  lines.push("");
}
writeFileSync("docs/existing-content-semantic-map.md", lines.join("\n")+"\n");
console.log(`Mapped ${rows.length} existing indexable pages before candidate generation.`);
