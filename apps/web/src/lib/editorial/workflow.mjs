import { createHash } from "node:crypto";
import { collectionPages } from "./collections.mjs";

export const STATES = ["IDEA", "PLANNED", "DRAFT", "REVIEW", "APPROVED", "PUBLISHED", "UPDATED", "ARCHIVED"];
const transitions = { IDEA: ["PLANNED", "ARCHIVED"], PLANNED: ["DRAFT", "ARCHIVED"], DRAFT: ["REVIEW", "ARCHIVED"], REVIEW: ["DRAFT", "APPROVED", "ARCHIVED"], APPROVED: ["DRAFT", "PUBLISHED", "ARCHIVED"], PUBLISHED: ["UPDATED", "ARCHIVED"], UPDATED: ["REVIEW", "ARCHIVED"], ARCHIVED: ["DRAFT"] };
export const published = (page) => page.status === "PUBLISHED" && page.indexable === true && page.canonical === page.path;
const normalize = (text) => String(text || "").toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
export function fingerprint(page) {
  const { status, indexable, approval, quality, ...content } = page;
  void status; void indexable; void approval; void quality;
  return createHash("sha256").update(JSON.stringify(content)).digest("hex");
}
// Key by complete text and shingle size, so edited content never reuses an
// earlier review representation. The bound limits long-lived process memory.
const shingleCaches = new Map();
function shingles(text, size = 5) {
  const value = String(text || "");
  let cache = shingleCaches.get(size);
  if (!cache) { cache = new Map(); shingleCaches.set(size, cache); }
  const cached = cache.get(value);
  if (cached) return cached;
  const words = normalize(value).split(" ");
  const result = new Set(words.slice(0, -size + 1).map((_, i) => words.slice(i, i + size).join(" ")));
  if (cache.size >= 32768) cache.delete(cache.keys().next().value);
  cache.set(value, result);
  return result;
}
export function similarity(a, b, size = 5) {
  const x = shingles(a, size), y = shingles(b, size);
  if (!x.size || !y.size) return 0;
  const common = [...x].filter(word => y.has(word)).length;
  return common / Math.min(x.size, y.size);
}
export function bodyText(page) {
  return [page.intro, page.example, ...(page.sections || []).flatMap(s => [s.heading, ...(s.paragraphs || []), ...(s.steps || [])]), ...(page.faq || []).flatMap(f => [f.question, f.answer])].join(" ");
}
export function inventoryGate(page, peers, core) {
  const errors = [];
  const educationOnly = page.platform === "whatsapp" && page.contentRole === "education" && page.targetDownloader === null;
  if (page.platform === "whatsapp" && !educationOnly) errors.push("unsupported_topic");
  if (!/^\/guides\/(youtube|instagram|facebook|tiktok|snapchat|whatsapp|general)\/[a-z0-9]+(?:-[a-z0-9]+)*\/$/.test(page.path || "")) errors.push("invalid_url");
  if (!page.userBenefit || page.userBenefit.length < 35) errors.push("missing_user_benefit");
  if (!page.intent || !page.primaryKeyword || !page.family || !page.platform || (!page.targetDownloader && !educationOnly)) errors.push("missing_intent_fields");
  if (/snapchat.*stor(y|ies)|whatsapp.*(downloader|viewer)|ai.*dubbing.*downloader|private.*(bypass|viewer)/i.test(`${page.path} ${page.intent}`)) errors.push("unsupported_topic");
  const target = core.find(p => p.path === page.targetDownloader);
  if (!educationOnly && (!target?.indexable || target.type !== "tool")) errors.push("unsupported_target_downloader");
  const others = [...core, ...peers.filter(p => p !== page)];
  for (const field of ["path", "title", "h1", "description", "intent", "primaryKeyword"]) {
    if (page[field] && others.some(other => normalize(other[field]) === normalize(page[field]))) errors.push(`collision_${field}`);
  }
  const keywordWords = new Set(normalize(page.primaryKeyword).split(" "));
  for (const other of peers.filter(other => other !== page)) {
    const otherWords = new Set(normalize(other.primaryKeyword).split(" "));
    const overlap = [...keywordWords].filter(word => otherWords.has(word)).length;
    const union = new Set([...keywordWords, ...otherWords]).size;
    if (union > 2 && overlap / union > 0.92) errors.push("keyword_overlap");
  }
  return [...new Set(errors)];
}
export function qualityGate(page, peers, core, incoming = 0) {
  const errors = inventoryGate(page, peers, core);
  if (page.batch?.startsWith("expansion-") && ((page.whyExistingContentDoesNotSatisfy || "").length < 80 || page.semanticReview?.state !== "APPROVED_DISTINCT_TASK" || !page.semanticReview?.reviewer)) errors.push("distinct_task_review_required");
  if (!page.inventoryApproval?.approved || page.inventoryApproval.intent !== page.intent || page.inventoryApproval.path !== page.path || (page.inventoryApproval.rationale || "").length < 50) errors.push("inventory_approval_required");
  if (page.canonical !== page.path) errors.push("canonical_collision");
  if (!page.title || !page.h1 || !page.description || page.description.length < 65 || page.description.length > 200) errors.push("missing_seo_metadata");
  if (!page.intro || page.intro.split(/\s+/).length < 35) errors.push("missing_answer_first_intro");
  const text = bodyText(page);
  if (text.split(/\s+/).length < 350 || (page.sections || []).length < 3) errors.push("insufficient_substantive_content");
  if (/\b(lorem ipsum|TODO|TBD|coming soon|insert text)\b/i.test(text)) errors.push("placeholder_content");
  if (!page.example || page.example.length < 50) errors.push("missing_worked_example");
  if (!(page.sections || []).some(s => /check|troubleshoot|fail|problem|verify/i.test(s.heading))) errors.push("missing_troubleshooting");
  if (!page.sources?.length || page.sources.some(s => !/^https:\/\//.test(s.url))) errors.push("missing_sources");
  if (!page.review?.accuracy || !page.review?.distinctValue || !page.review?.answerFirst || !page.review?.supportedClaims || !page.review?.examples || !page.review?.specificity) errors.push("editorial_review_required");
  if (!page.lastUpdated || !page.review?.reviewedAt || !page.review?.reviewer) errors.push("missing_review_provenance");
  if (incoming < 1) errors.push("orphan");
  const eligible = new Set([...core.filter(p => p.indexable), ...peers.filter(p => published(p) || ["REVIEW", "APPROVED"].includes(p.status)), page].map(p => p.path));
  if (!eligible.has(page.hub)) errors.push("invalid_platform_hub");
  if ((page.processingLinks || []).some(path=>!core.some(tool=>tool.path===path && tool.indexable))) errors.push("broken_or_unpublished_processing_tool");
  const related = page.related || [];
  if (related.length < 2 || related.length > 5 || new Set(related).size !== related.length) errors.push("invalid_related_guides");
  if (related.some(path => path === page.path || !eligible.has(path))) errors.push("broken_or_unpublished_internal_link");
  const body = (page.sections || []).flatMap(s => [s.heading, ...(s.paragraphs || []), ...(s.steps || [])]).join(" ");
  for (const other of peers.filter(other => other.path !== page.path && other.sections?.length)) {
    if (similarity(page.intro, other.intro) > 0.7 || similarity(body, (other.sections || []).flatMap(s => [s.heading, ...(s.paragraphs || []), ...(s.steps || [])]).join(" ")) > 0.55) errors.push("near_duplicate_content");
    if (page.faq?.length && other.faq?.length && similarity(JSON.stringify(page.faq), JSON.stringify(other.faq)) > 0.7) errors.push("near_duplicate_faq");
    if (similarity(page.title, other.title, 2) > 0.8 || similarity(page.h1, other.h1, 2) > 0.8) errors.push("near_duplicate_heading");
    if (similarity(page.intent, other.intent, 2) > 0.8) errors.push("cannibalization_risk");
    if (similarity(page.path.replaceAll("/", " "), other.path.replaceAll("/", " "), 2) > 0.85) errors.push("near_duplicate_url");
  }
  return { passed: errors.length === 0, score: Math.max(0, 100 - [...new Set(errors)].length * 10), errors: [...new Set(errors)] };
}
export function transition(page, next, evidence) {
  if (!transitions[page.status]?.includes(next)) throw new Error(`Invalid transition ${page.status} → ${next}`);
  if (["APPROVED", "PUBLISHED"].includes(next) && (!evidence?.passed || evidence.digest !== fingerprint(page))) throw new Error("Fresh passing quality evidence is required");
  if (next === "PUBLISHED" && page.approval?.digest !== fingerprint(page)) throw new Error("Content changed after approval");
  return { ...page, status: next, indexable: next === "PUBLISHED", approval: next === "APPROVED" ? { digest: evidence.digest, reviewedAt: page.review.reviewedAt, reviewer: page.review.reviewer } : page.approval };
}
export function publicationInventory(core, articles) {
  // Fail closed if a published payload was edited after approval.
  let visible = articles.filter(page => published(page) && page.approval?.digest === fingerprint(page));
  // Prune dependent articles with a reverse graph instead of rescanning the
  // whole inventory for every missing link in a long chain.
  const paths = new Set([...core.filter(page => page.indexable).map(page => page.path), ...visible.map(page => page.path)]);
  const dependents = new Map();
  const missing = [];
  for (const page of visible) {
    const dependencies = [...(page.related || []), page.targetDownloader, page.hub].filter(Boolean);
    if (dependencies.some(path => !paths.has(path))) missing.push(page.path);
    for (const path of dependencies) {
      if (!dependents.has(path)) dependents.set(path, []);
      dependents.get(path).push(page.path);
    }
  }
  for (let index = 0; index < missing.length; index++) {
    const path = missing[index];
    if (!paths.delete(path)) continue;
    missing.push(...(dependents.get(path) || []));
  }
  visible = visible.filter(page => paths.has(page.path));
  const directories = collectionPages(visible);
  return [...core.map(page => ({ ...page, status: "PUBLISHED", canonical: page.path, indexable: page.indexable && (page.path !== "/guides/" || visible.length > 0) })), ...visible, ...directories];
}
export function sitemapChunks(pages, size = 1000) {
  const eligible = pages.filter(page => published(page));
  const result = [];
  for (let offset = 0; offset < eligible.length; offset += size) result.push(eligible.slice(offset, offset + size));
  return result;
}
