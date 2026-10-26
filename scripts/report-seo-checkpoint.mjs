import { readFileSync, writeFileSync } from "node:fs";
import { publicationInventory, published, bodyText } from "../apps/web/src/lib/editorial/workflow.mjs";

const load = path => JSON.parse(readFileSync(path, "utf8"));
const audit = load("docs/content-system-audit.json");
const articles = load("content/editorial/articles.json");
const briefs = load("content/editorial/first-500-inventory.json");
const inventory = publicationInventory(load("content/pages/publication.json"), articles);
const expected = inventory.map(page => page.path).sort();
const actual = audit.pages.map(page => page.path).sort();
if (JSON.stringify(expected) !== JSON.stringify(actual)) throw new Error("Run the production HTTP audit before reporting a changed inventory");
const eligible = audit.pages.filter(page => page.indexable);
const baseline = new Set(load("docs/existing-content-semantic-map-90-baseline.json").pages.map(page => page.path));
const added = articles.filter(page => published(page) && !baseline.has(page.path));
const expansion = briefs.filter(brief => brief.batch?.startsWith("expansion-"));
const stageA = briefs.filter(brief => brief.batch === "expansion-stage-a-2026-10-08");
const stageADrafts = stageA.filter(brief => brief.status === "DRAFT");
const stageARejected = stageA.filter(brief => /^REJECT(?:ED)?_/.test(brief.disposition.classification));
const draftRouteAudit = load("docs/stage-a-draft-route-audit.json");
const verifiedDraftExclusions = draftRouteAudit.routeChecks.filter(row => row.status === 404).length;
const outcomes = rows => rows.reduce((counts, row) => {
  const decision = row.disposition?.outcome === "PUBLISHED" ? "PUBLISHED" : row.disposition?.classification === "MERGE_WITH_EXISTING" ? "MERGED" : row.disposition?.classification;
  counts[decision] = (counts[decision] || 0) + 1;
  return counts;
}, {});
const counts = (rows, field) => rows.reduce((result, row) => {
  const key = field(row);
  result[key] = (result[key] || 0) + 1;
  return result;
}, {});
const platformCounts = counts(eligible, page => page.path.includes("youtube-shorts") ? "youtube-shorts" : page.platform || "general");
const familyCounts = counts(eligible, page => page.family);
// Preserve stored families and separately provide a non-overlapping subject
// breakdown matching the user's report categories. Legacy format records
// include codec and audio topics; reporting must make that mapping explicit.
const requestedFamilyCounts = counts(eligible, page => {
  if (page.family === "formats") {
    if (/\/(av1-video-codec|vp9-video-codec)\/$/.test(page.path)) return "Codecs";
    if (page.path.endsWith("/audio-bitrate/")) return "Audio/multilingual";
    if (page.path.endsWith("/mp4-vs-mov/")) return "Formats";
    return "Video quality";
  }
  if (page.family === "how-to") return page.path.endsWith("/inspect-local-video-with-ffprobe/") ? "Other" : "Platform help";
  return ({ troubleshooting: "Troubleshooting", faq: "FAQ/Q&A", device: "Device", browser: "Browser", "platform-help": "Platform help", codecs: "Codecs", audio: "Audio/multilingual", captions: "Subtitles/captions", comparison: "Comparisons", glossary: "Glossary", copyright: "Copyright/privacy", creator: "Creator/backup/editing" })[page.family] || "Other";
});
const sentences = new Map();
for (const page of added) {
  for (const sentence of bodyText(page).split(/[.!?](?:\s|$)/)) {
    const normalized = sentence.trim().toLowerCase().replace(/\s+/g, " ");
    if (normalized.split(" ").length < 15) continue;
    if (!sentences.has(normalized)) sentences.set(normalized, new Set());
    sentences.get(normalized).add(page.path);
  }
}
const repeated = [...sentences].filter(([, paths]) => paths.size > 1).map(([sentence, paths]) => ({ sentence, paths: [...paths] }));
const copyReview = {
  baselineIndexable: 90,
  reviewedNewArticles: added.length,
  reviewedPaths: added.map(page => page.path),
  reReviewedExistingPaths: [
    '/guides/general/tracked-video-blur-handoff-review/',
    '/guides/youtube/youtube-content-id-claim-vs-strike/',
    '/guides/general/audio-channel-downmix/',
    '/guides/general/playback-speed-vs-retimed-video/',
    '/guides/general/video-shortcut-vs-retained-file/',
    "/guides/general/frame-rate-vs-resolution/",
    "/guides/facebook/facebook-video-copy-direct-link/",
    "/guides/instagram/instagram-video-copy-direct-link/",
    "/guides/tiktok/tiktok-video-copy-direct-link/",
    "/guides/facebook/facebook-reels-copy-direct-link/",
    "/guides/general/open-vs-closed-captions/",
    "/guides/whatsapp/whatsapp-exported-video-vs-chat-link/",
    "/guides/general/chromebook-local-files/",
    "/guides/general/copy-video-to-usb/",
    "/guides/general/recover-recently-deleted-video/",
    "/guides/general/windows-n-media-feature-pack/",
    "/guides/youtube/youtube-studio-edit-version-retention/",
    "/guides/general/video-editing-proxy/",
    "/guides/general/archive-source-vs-edit/",
  ],
  method: "Agent source/copy review plus exact repeated body sentences of at least 15 words; not an independent human review or a grammar certification.",
  repeatedSentences: repeated,
  independentHumanReview: false,
  measuredSearchMetrics: false,
};
writeFileSync("docs/continuation-copy-review.json", JSON.stringify(copyReview, null, 2) + "\n");
const table = (values, label) => [`| ${label} | Pages |`, "|---|---:|", ...Object.entries(values).sort().map(([key, value]) => `| ${key} | ${value} |`)];
const summary = audit.summary;
const qualityFields = ["schemaErrors", "canonicalErrors", "duplicateTitles", "duplicateH1s", "duplicateDescriptions", "orphanIndexablePages", "brokenInternalLinks", "missingIndexable", "noindexInSitemap", "duplicateSitemapURLs", "brokenPublicURLs", "robotsMismatch", "cannibalizationConflictsBlocked", "unsupportedTopicsBlocked"];
const report = [
  "# SEO content checkpoint", "",
  "**PAUSED_FOR_LAUNCH.** Content expansion remains unfinished and is frozen until an explicit instruction to resume.", "",
  "## Current verified public site", "",
  "| Metric | Count |", "|---|---:|",
  `| Public 200 pages | ${summary.publicPages} |`,
  `| Indexable pages | ${summary.indexablePages} |`,
  `| Public noindex pages | ${summary.noindexPages} |`,
  `| Sitemap URLs | ${summary.sitemapURLs} |`,
  `| Published supporting articles | ${summary.publishedArticles} |`,
  `| Authored drafts | ${summary.draftArticles} |`,
  `| Unresolved recorded candidates | ${summary.plannedUnwrittenBriefs} |`, "",
  "## Two-stage inventory status", "",
  `Stage A contains ${stageA.length} raw candidates: ${stageADrafts.length} nonpublic draft hypotheses, ${stageA.filter(brief => brief.disposition.classification === "MERGE_WITH_EXISTING").length} scope consolidations and ${stageARejected.length} rejected proposals. No Stage A hypothesis has been approved or published. Draft owners of consolidated ideas remain nonpublic. The draft HTTP audit at ${draftRouteAudit.checkedAt} verified ${verifiedDraftExclusions} of ${draftRouteAudit.candidateCount} candidate URLs returned 404; ${Math.max(0, stageA.length - draftRouteAudit.candidateCount)} newly registered candidates have not yet received that HTTP check. The complete master inventory and factual/semantic review are not finished.`, "",
  "Raw registry records are not public SEO pages and do not imply observed demand. Preserve drafts and recorded decisions; do not generate or publish new content during launch readiness.", "",
  "## Continuation decisions", "",
  `Starting indexable count: **90**. New published articles: **${added.length}**. The saved 56-item queue was resolved as 50 published and six merged; subsequent source-led discovery continued across formats, captions, audio, delivery, devices, creator archives, copyright and truthful WhatsApp education.`, "",
  `Expansion registry: ${expansion.length} candidates; final decisions ${JSON.stringify(outcomes(expansion))}. Whole canonical registry: ${briefs.length} records; final decisions ${JSON.stringify(outcomes(briefs))}. Historical workflow classifications are retained; disposition outcomes identify published records.`, "",
  "No unsupported Snapchat Story tool, private-content bypass, production AI dubbing tool or WhatsApp URL downloader was added. The working download engine is unchanged. Reserved, merged and rejected URLs do not become public pages.", "",
  "## Indexable content families", "", ...table(familyCounts, "Family"), "",
  "### Requested subject breakdown", "", ...table(requestedFamilyCounts, "Subject"), "",
  "This non-overlapping view maps legacy format-labelled AV1/VP9 articles to Codecs and audio bitrate to Audio. The remaining format-labelled measurement/presentation articles belong to Video quality; MP4 versus MOV remains Formats. Individual source-link how-to articles join Platform help, while local FFprobe inspection joins Other. Core pages and use cases are also Other. Stored metadata families above remain unchanged.", "",
  "Browse directories and pagination remain noindex. Other public noindex pages include unsupported or incomplete core landings and legal/operator pages. About is the current indexable trust page.", "",
  "## Indexable platforms", "", ...table(platformCounts, "Platform"), "",
  "YouTube Shorts is partitioned by its dedicated tool/article paths; each indexable URL is counted once. WhatsApp counts educational articles, with no downloader CTA.", "",
  "## Quality evidence", "", "| Check | Errors found |", "|---|---:|",
  ...qualityFields.map(key => `| ${key} | ${summary[key]} |`), "",
  `All authored pages pass publication/inventory gates. Exact repeated body sentences of at least 15 words across the ${added.length} new articles: **${repeated.length}**. Sources and copy were reviewed by the agent; no independent human grammar audit, observed SERP equivalence or fabricated keyword volume is claimed.`, "",
  "## Validation", "",
  "Final production-readiness evidence is recorded in manual-deployment-readiness-report.md, launch-live-provider-results.json and the final HTTP/browser audit reports. Content generation is paused; historical content-checkpoint checks are not substitutes for the launch verification.", "",
  "The default Turbopack build cannot bind its processing port in this environment. The established `npm run build --workspace apps/web -- --webpack` production build succeeds; no build configuration was changed to conceal that limitation.", "",
  "Article content remains server-side, and browse listings are bounded at 24 articles. Content similarity caches are bounded and keyed by complete text and shingle size. These are local sanity checks, not a 5,000-page production load test or field Core Web Vitals evidence.", "",
  "## Progress and remaining work", "",
  `Indexable: **${summary.indexablePages}/5,000**. Remaining: **${summary.remaining}**. Progress: **${Number(summary.percentageComplete.toFixed(2))}%**.`, "",
  "PAUSED_FOR_LAUNCH: preserve the current semantic map, drafts and canonical registry. No further discovery, authoring or publication is authorized in this phase.", "",
  "Evidence: content-system-audit.json, content-quality-report.json, continuation-copy-review.json, existing-content-semantic-map.md, candidate-intent-screening.md and 5000-page-build-state.md.",
];
writeFileSync("docs/seo-quality-report.md", report.join("\n") + "\n");
writeFileSync("docs/final-5000-page-audit.md", "# 5,000-page audit status\n\n**This is an interim checkpoint, not a completed final audit.**\n\n" + report.slice(2).join("\n") + "\n");
const publicList = ["# Current public page inventory", "", `Verified HTTP 200 URLs: ${summary.publicPages}; indexable: ${summary.indexablePages}; noindex: ${summary.noindexPages}. Redirects, private routes, drafts and unrenderable content records are excluded.`, ""];
for (const indexable of [true, false]) {
  publicList.push(`## ${indexable ? "Public indexable" : "Public noindex"}`, "", ...audit.pages.filter(page => page.indexable === indexable).map(page => `- ${page.path}`), "");
}
writeFileSync("docs/current-page-inventory.md", publicList.join("\n") + "\n");
console.log(JSON.stringify({ indexable: eligible.length, newArticles: added.length, repeatedSentences: repeated.length, platformCounts, familyCounts, requestedFamilyCounts }, null, 2));
