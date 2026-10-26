import { equivalentLanguages } from "./localized-publication";
import "server-only";
import type { Metadata } from "next";
import core from "../../../../content/pages/publication.json";
import articleData from "../../../../content/editorial/articles.json";
import briefData from "../../../../content/editorial/first-500-inventory.json";
import type { Article, Brief } from "./editorial/types";
import { publicationInventory, fingerprint } from "./editorial/workflow.mjs";
export const articles = articleData as Article[];
export const briefs = briefData as Brief[];
export const publicPages = publicationInventory(core, articles);
const pageByPath = new Map(publicPages.map(page => [page.path, page]));
export const publishedArticles = articles.filter(article => pageByPath.has(article.path));
const publishedByPath = new Map(publishedArticles.map(article => [article.path, article]));
const articleByPath = new Map(articles.map(article => [article.path, article]));
const incomingByPath = new Map<string, number>();
for (const article of publishedArticles) for (const path of article.related) incomingByPath.set(path, (incomingByPath.get(path) || 0) + 1);
export function getArticle(path: string) { return publishedByPath.get(path); }
export function pageMetadata(path: string): Metadata {
  const page = pageByPath.get(path);
  if (!page) throw new Error(`No publicly eligible publication record for ${path}`);
  return { title: page.title, description: page.description, alternates: { canonical: page.path, languages: equivalentLanguages(page.path) }, robots: { index: page.indexable, follow: true } };
}
export function editorialInventory() {
  return briefs.map(brief => {
    const article = articleByPath.get(brief.path);
    const inbound = (incomingByPath.get(brief.path) || 0) + (getArticle(brief.path) ? 1 : 0);
    const quality = article && article.approval?.digest === fingerprint(article) ? article.quality : null;
    return { ...brief, status: article?.status || brief.status, indexable: !!getArticle(brief.path), qualityScore: quality?.score ?? 0, duplicateRisk: quality?.errors.some(error => /duplicate|collision|cannibalization/.test(error)) ? "Blocked" : article ? "Reviewed" : brief.disposition?.classification === "MERGE_WITH_EXISTING" ? "Consolidated" : "Requires review", incoming: inbound, outgoing: article ? article.related.length + 3 : 0, lastUpdated: article?.lastUpdated || brief.disposition?.reviewedAt || null, errors: quality?.errors || [brief.disposition?.reason || "Unwritten brief; not a public page"] };
  });
}
