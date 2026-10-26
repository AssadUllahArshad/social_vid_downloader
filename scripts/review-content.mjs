import { readFileSync, writeFileSync, renameSync } from "node:fs";
import { qualityGate, inventoryGate, transition, fingerprint, published, bodyText } from "../apps/web/src/lib/editorial/workflow.mjs";
const load = path => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));
const core = load("../content/pages/publication.json");
const briefs = load("../content/editorial/first-500-inventory.json");
const publish = process.argv.includes("--publish");
const articles = load("../content/editorial/articles.json").map(page => publish && page.status === "DRAFT" ? transition(page, "REVIEW") : page);
const activeBriefs = briefs.filter(brief => brief.inventoryApproval?.approved);
const inventory = activeBriefs.map(brief => ({ path: brief.path, errors: inventoryGate(brief, activeBriefs, core), status: brief.status }));
const reports = articles.map(article => ({ path: article.path, ...qualityGate(article, articles, core, 1) }));
const articlePaths = new Set(articles.map(article => article.path));
const dispositions = briefs.reduce((counts, brief) => {
  const classification = brief.disposition?.classification || "UNDISPOSED";
  counts[classification] = (counts[classification] || 0) + 1;
  return counts;
}, {});
const unfinished = briefs.filter(brief => !brief.disposition || brief.disposition.classification === "NEEDS_RESEARCH" || (brief.disposition.classification === "APPROVED_TO_WRITE" && !articlePaths.has(brief.path)));
const report = { inventoryCount: briefs.length, dispositions, approvedIntentCount: briefs.filter(brief => brief.inventoryApproval?.approved).length, unwrittenBriefCount: unfinished.length, writtenCount: articles.length, inventoryIssues: inventory.filter(row => row.errors.length), quality: reports, published: articles.filter(published).length };
if (publish) {
  // Batch publication is atomic: no unresolved links to partially approved peers.
  const finalPaths = new Set([...core.filter(page => page.indexable).map(page => page.path), ...articlePaths]);
  // A checkpoint may publish reviewed authored pages while unrelated research
  // remains nonpublic. Pending briefs never become routes or receive approval.
  const brokenOwners = briefs.some(brief => brief.disposition?.classification === "MERGE_WITH_EXISTING" && !finalPaths.has(brief.disposition.destination));
  const unapprovedAuthored = articles.some(article => !activeBriefs.some(brief => brief.path === article.path));
  if (brokenOwners || unapprovedAuthored || report.inventoryIssues.length || reports.some(row => !row.passed)) throw new Error("Quality or disposition gates failed; publication cancelled");
  const next = articles.map(article => {
    if (published(article)) {
      if (article.approval?.digest !== fingerprint(article)) throw new Error("Published content changed without re-review");
      return article;
    }
    let page = article;
    if (page.status === "DRAFT") page = transition(page, "REVIEW");
    const evidence = { passed: true, digest: fingerprint(page) };
    if (page.status === "REVIEW") page = transition(page, "APPROVED", evidence);
    return transition(page, "PUBLISHED", { passed: true, digest: fingerprint(page) });
  });
  next.forEach(page => { page.quality = reports.find(report => report.path === page.path); });
  const destination = new URL("../content/editorial/articles.json", import.meta.url);
  const temporary = new URL("../content/editorial/articles.json.tmp", import.meta.url);
  writeFileSync(temporary, JSON.stringify(next, null, 2)+"\n");
  renameSync(temporary, destination);
  const nextBriefs = briefs.map(brief => articlePaths.has(brief.path) ? { ...brief, status: "PUBLISHED", indexable: true, disposition: { ...brief.disposition, outcome: "PUBLISHED" } } : brief);
  const briefDestination = new URL("../content/editorial/first-500-inventory.json", import.meta.url);
  const briefTemporary = new URL("../content/editorial/first-500-inventory.json.tmp", import.meta.url);
  writeFileSync(briefTemporary, JSON.stringify(nextBriefs, null, 2)+"\n");
  renameSync(briefTemporary, briefDestination);
  report.published = next.filter(published).length;
}
writeFileSync(new URL("../docs/content-quality-report.json", import.meta.url), JSON.stringify(report, null, 2)+"\n");
console.log(JSON.stringify({ ...report, quality: reports.map(row => ({path:row.path,passed:row.passed,errors:row.errors})) },null,2));
void bodyText;
