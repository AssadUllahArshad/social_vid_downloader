import { readFileSync, writeFileSync } from "node:fs";
import { intentTokens, tokenSimilarity } from './intent-screening.mjs';
const path = "content/editorial/first-500-inventory.json";
const briefs = JSON.parse(readFileSync(path, "utf8"));
const baseline = JSON.parse(readFileSync("docs/existing-content-semantic-map.json", "utf8")).pages;
const expansion = briefs.filter(brief => brief.batch?.startsWith("expansion-"));
const score = (a, b) => tokenSimilarity(intentTokens(a), intentTokens(b));
const entries = [...baseline.map(page=>({path:page.path,title:page.title,intent:page.primaryIntent,problem:page.primaryQuery})),...expansion.filter(other=>other.status!=="ARCHIVED").map(other=>({path:other.path,title:other.title,intent:other.intent,problem:other.userProblem}))];
const comparisonPool = [...new Map(entries.reverse().map(other=>[other.path,other])).values()];
for (const brief of expansion) {
  // Compare real canonical answers and active candidate tasks. A candidate's
  // own published page must not consume a comparison slot, and archived
  // aliases are decisions rather than independently existing answers.
  const pool = comparisonPool.filter(other=>other.path!==brief.path);
  const comparisons=pool.map(other=>({path:other.path,titleScore:score(brief.title,other.title),taskScore:score(brief.userProblem,other.problem),intentScore:score(brief.intent,other.intent)})).sort((a,b)=>Math.max(b.titleScore,b.taskScore,b.intentScore)-Math.max(a.titleScore,a.taskScore,a.intentScore)).slice(0,5);
  brief.semanticReview.comparisonEvidence=comparisons;
  brief.semanticReview.screeningMethod="Normalized token shortlist with download/save and caption/subtitle synonym grouping; fixed native discovery instructions are excluded. Resource terms are retained. Token order and editorial task scope still require review; SERP similarity is unmeasured.";
}
writeFileSync(path,JSON.stringify(briefs,null,2)+"\n");
// Article approval is content-bound. Screening updates briefs, not already
// reviewed article payloads; a later edit must use the existing re-review path.
const lines=["# Candidate intent screening", "", `Compare against the current ${baseline.length}-page baseline and all curated new tasks before authoring. Scores are screening evidence, not semantic certainty or measured search demand. Reviewers must assess the stated gap and actual answer.`, ""];
for(const brief of expansion) lines.push(`## ${brief.id}: ${brief.title}`,"",`Decision: ${brief.disposition.classification}. ${brief.disposition.reason}`,"",...brief.semanticReview.comparisonEvidence.map(row=>`- ${row.path}: title ${row.titleScore.toFixed(2)}, task ${row.taskScore.toFixed(2)}, intent ${row.intentScore.toFixed(2)}`),"");
writeFileSync("docs/candidate-intent-screening.md",lines.join("\n")+"\n");
console.log(`Screened ${expansion.length} candidates against existing pages and peers; no automatic publication.`);
