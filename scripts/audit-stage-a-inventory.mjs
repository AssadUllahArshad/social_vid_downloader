import { readFileSync, writeFileSync } from 'node:fs';
import { intentTokens as tokens, tokenSimilarity as score, nativeTopicOnly } from './intent-screening.mjs';
import { publicationInventory, sitemapChunks, fingerprint } from '../apps/web/src/lib/editorial/workflow.mjs';
const load = path => JSON.parse(readFileSync(path, 'utf8'));
const registry = load('content/editorial/first-500-inventory.json');
const articles = load('content/editorial/articles.json');
const core = load('content/pages/publication.json');
const sourceLeads = load('content/editorial/stage-a-source-opportunities.json');
const sourceByID = new Map(sourceLeads.map(row => [row.sourceID, row]));
const candidates = registry.filter(row => row.batch === 'expansion-stage-a-2026-10-08');
const publicPages = publicationInventory(core, articles);
const publicPaths = new Set(publicPages.map(row => row.path));
const sitemapPaths = new Set(sitemapChunks(publicPages).flat().map(row => row.path));
const publishedPaths = new Set(articles.filter(row => publicPaths.has(row.path)).map(row => row.path));
const errors = [];
const registryByPath = new Map(registry.map(row => [row.path, row]));
if (sourceByID.size !== sourceLeads.length) errors.push('Duplicate discovery source ID');
if (new Set(sourceLeads.map(row => row.sourceURL)).size !== sourceLeads.length) errors.push('Duplicate discovery source URL');
const unique = field => {
  const seen = new Set();
  for (const row of registry) {
    if (!row[field]) errors.push(`${row.path}: missing ${field}`);
    else if (seen.has(row[field])) errors.push(`${row.path}: duplicate ${field}`);
    seen.add(row[field]);
  }
};
unique('id'); unique('path');
const required = ['intent', 'primaryKeyword', 'primaryTopic', 'targetUser', 'userProblem', 'userBenefit', 'whyExistingContentDoesNotSatisfy', 'hub', 'internalLinkParent', 'title', 'h1', 'description', 'family', 'platform', 'qualityResult'];
for (const row of candidates) {
  if (row.status === "PUBLISHED" && publishedPaths.has(row.path)) continue;
  for (const field of required) if (typeof row[field] !== 'string' || !row[field].trim()) errors.push(`${row.path}: missing ${field}`);
  if (row.canonical !== row.path || !/^\/guides\/(general|youtube|facebook|instagram|tiktok|snapchat|whatsapp)\/[a-z0-9-]+\/$/.test(row.path)) errors.push(`${row.path}: invalid canonical/path`);
  if (row.indexable !== false || row.inventoryApproval !== null || !['DRAFT', 'ARCHIVED', 'DEFERRED_FEATURE_NOT_READY'].includes(row.status)) errors.push(`${row.path}: unfinished publication eligibility`);
  if (publicPaths.has(row.path) || sitemapPaths.has(row.path)) errors.push(`${row.path}: draft leaked into public inventory`);
  if (publicPages.some(page => page.related?.includes(row.path))) errors.push(`${row.path}: public related-link leak`);
  if (row.whyExistingContentDoesNotSatisfy.length < 80 || row.related.length < 2 || row.related.length > 5 || row.related.some(path => !publishedPaths.has(path))) errors.push(`${row.path}: missing gap or invalid suggested published peers`);
  if (row.platform === 'whatsapp' && (row.contentRole !== 'education' || row.targetDownloader !== null)) errors.push(`${row.path}: unsupported WhatsApp capability`);
  if (row.platform !== 'whatsapp' && !core.some(page => page.path === row.targetDownloader && page.type === 'tool' && page.indexable)) errors.push(`${row.path}: invalid or unsupported suggested tool`);
  if (!publicPaths.has(row.hub) || !publicPaths.has(row.internalLinkParent)) errors.push(`${row.path}: invalid suggested hub/category parent`);
  if (/snapchat.*stor(y|ies)|whatsapp.*downloader|private.*bypass/i.test(row.path + ' ' + row.intent)) errors.push(`${row.path}: forbidden capability`);
  if (row.disposition.classification === 'MERGE_WITH_EXISTING' && !registry.some(peer => peer.path === row.disposition.destination) && !publicPaths.has(row.disposition.destination)) errors.push(`${row.path}: missing merge owner`);
  if (row.disposition.classification === 'MERGE_WITH_EXISTING') {
    const owner = registryByPath.get(row.disposition.destination);
    if (row.disposition.destination === row.path || (!publicPaths.has(row.disposition.destination) && !['DRAFT','DEFERRED_FEATURE_NOT_READY'].includes(owner?.status))) errors.push(`${row.path}: inactive or cyclic merge owner`);
    if (row.disposition.internalLinkDestination !== row.disposition.destination) errors.push(`${row.path}: inconsistent merge link owner`);
    const publicOwner = publicPaths.has(row.disposition.destination);
    if (row.semanticReview.state !== (publicOwner ? 'MERGED_EXISTING_TASK' : 'MERGED_DRAFT_TASK') || row.disposition.outcome !== (publicOwner ? 'CONSOLIDATED' : 'RESEARCH_REQUIRED')) errors.push(`${row.path}: stale owner lifecycle state`);
  }
  for (const lead of row.primarySourceLeads || []) {
    if (sourceByID.get(lead.sourceID)?.sourceURL !== lead.url) errors.push(`${row.path}: unmatched primary discovery lead`);
    if (lead.matchIsHypothesis !== true) errors.push(`${row.path}: discovery association incorrectly claims factual approval`);
    if (row.platform === 'youtube' && new URL(lead.url).hostname !== 'support.google.com') errors.push(`${row.path}: wrong native provider source`);
  }
}
for (const article of articles.filter(row => row.status === 'PUBLISHED')) if (article.approval?.digest !== fingerprint(article)) errors.push(`${article.path}: changed approved article`);
// Evaluate draft hypotheses against actual current authored answers and every
// active candidate. Lexical scores are a shortlist, never semantic approval.
const entries = [...articles.map(row => ({ path: row.path, title: row.title, task: row.userBenefit, kind: 'authored' })), ...registry.filter(row => row.status !== 'ARCHIVED' && !articles.some(article => article.path === row.path)).map(row => ({ path: row.path, title: row.title, task: row.userBenefit, kind: 'candidate' }))];
for (const row of entries) { row.titleTokens = tokens(row.title); row.taskTokens = tokens(row.task); }
const shortlist = candidates.filter(row => row.status === 'DRAFT').map(row => {
  const title = tokens(row.title), task = tokens(row.userBenefit);
  const peers = entries.filter(peer => peer.path !== row.path).map(peer => ({ path: peer.path, kind: peer.kind, titleSimilarity: score(title, peer.titleTokens), taskSimilarity: score(task, peer.taskTokens) })).sort((a,b) => Math.max(b.titleSimilarity,b.taskSimilarity)-Math.max(a.titleSimilarity,a.taskSimilarity)).slice(0,5);
  return { id: row.id, path: row.path, title: row.title, taskEvidence: nativeTopicOnly(row.userBenefit) ? 'NATIVE_TOPIC_ONLY_SCOPE_RESEARCH_REQUIRED' : 'CURATED_TASK_HYPOTHESIS_REVIEW_REQUIRED', peers };
});
const routeChecks = [];
if (process.argv.includes('--http')) {
  const nonpublicCandidates = candidates.filter(row => !publishedPaths.has(row.path));
  let next = 0;
  await Promise.all(Array.from({length: 8}, async () => {
    while (next < nonpublicCandidates.length) {
      const row = nonpublicCandidates[next++];
      const response = await fetch(`${process.env.AUDIT_ORIGIN||'http://127.0.0.1:3000'}${row.path}`, {redirect:'manual'});
      routeChecks.push({path:row.path,status:response.status});
      await response.arrayBuffer();
      if (response.status !== 404) errors.push(`${row.path}: expected nonpublic 404, got ${response.status}`);
    }
  }));
}
const report = { status: errors.length ? 'FAILED' : 'INVENTORY_IN_PROGRESS', target: 5000, currentIndexableRecords: publicPages.filter(row => row.indexable).length, verifiedHTTPIndexable: load('docs/content-system-audit.json').summary.indexablePages, canonicalRegistryRecords: registry.length, stageARawCandidates: candidates.length, draftHypotheses: candidates.filter(row => row.status === 'DRAFT').length, merged: candidates.filter(row => row.disposition.classification === 'MERGE_WITH_EXISTING').length, rejectedLowValue: candidates.filter(row => row.disposition.classification === 'REJECTED_LOW_VALUE').length, approvedStageAPages: candidates.filter(row => publishedPaths.has(row.path)).length, rawCandidatesAreNotApprovedPages: true, nativeTopicOnlyDrafts: candidates.filter(row => row.status === 'DRAFT' && nativeTopicOnly(row.userBenefit)).length, semanticReviewComplete: false, targetInventoryComplete: false, routeChecks, errors, shortlist };
if (process.argv.includes('--http')) writeFileSync('docs/stage-a-draft-route-audit.json', JSON.stringify({ checkedAt: new Date().toISOString(), registryRecords: registry.length, candidateCount: candidates.length, routeChecks, errors: errors.filter(error => error.includes('expected nonpublic')) },null,2)+'\n');
writeFileSync('docs/stage-a-inventory-audit.json', JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report, shortlist: undefined, routeChecks: routeChecks.length},null,2));
if (errors.length) process.exitCode = 1;
