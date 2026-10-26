import { readFileSync, writeFileSync } from "node:fs";
import { publicationInventory, published, qualityGate } from "../apps/web/src/lib/editorial/workflow.mjs";
const load = path => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));
const core = load("../content/pages/publication.json"), articles = load("../content/editorial/articles.json"), briefs = load("../content/editorial/first-500-inventory.json");
const translationRecords = load("../content/translations/pages.json");
const { eligibleTranslation } = await import("../apps/web/src/lib/translation-policy.mjs");
const translated = translationRecords.filter(row => row.complete).map(row => {
 const dictionary = load(`../apps/web/src/locales/${row.locale}.json`);
 const processing = load("../content/processing/tools.json");
 const isProcessing = row.englishPath === "/video-tools/" || processing.some(tool=>`/${tool.slug}/` === row.englishPath);
 const messages = isProcessing ? {...dictionary,...load(`../apps/web/src/locales/processing/${row.locale}.json`)} : dictionary;
 const path = `/${row.locale}${row.englishPath}`;
 return { path, canonical:path, status:"PUBLISHED", indexable:row.englishPath!=="/faq/" && eligibleTranslation(row,messages), platform:"general", family:"translation" };
});
const pages = [...publicationInventory(core, articles), ...translated];
const origin = process.env.AUDIT_ORIGIN || "http://127.0.0.1:3000";
const site = process.env.NEXT_PUBLIC_SITE_URL || "https://socialviddownloader.com";
const htmlRows = [];
const articleByPath = new Map(articles.map(article => [article.path, article]));
for (const page of pages) {
  const response = await fetch(`${origin}${page.path}`, { redirect: "manual" });
  const html = await response.text();
  const schemaErrors = [];
  const article = articleByPath.get(page.path);
  if (article) {
    let schemas = [];
    try { schemas = [...html.matchAll(/<script\b[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/g)].map(match => JSON.parse(match[1])); }
    catch { schemaErrors.push("invalid_jsonld"); }
    const item = schemas.find(row => row["@type"] === "Article");
    const breadcrumb = schemas.find(row => row["@type"] === "BreadcrumbList");
    if (!item || item.headline !== article.h1 || item.mainEntityOfPage !== site + page.path || item.description !== article.description || item.dateModified !== article.lastUpdated) schemaErrors.push("article_schema_mismatch");
    if (!breadcrumb || breadcrumb.itemListElement?.at(-1)?.item !== site + page.path || breadcrumb.itemListElement?.some(row => !pages.some(target => site + target.path === row.item))) schemaErrors.push("breadcrumb_schema_mismatch");
  }
  const links = [...html.matchAll(/<a\b[^>]*href="([^"]+)"/g)].map(match => match[1].replaceAll("&amp;", "&")).filter(href => href.startsWith("/") && !href.startsWith("//")).map(href => new URL(href, site).pathname);
  htmlRows.push({schemaErrors,path:page.path,status:response.status,indexable:page.indexable,robots:html.match(/<meta name="robots" content="([^"]+)"/)?.[1],title:html.match(/<title>(.*?)<\/title>/)?.[1],h1:html.match(/<h1(?:\s[^>]*)?>(.*?)<\/h1>/)?.[1],description:html.match(/<meta name="description" content="([^"]+)"/)?.[1],canonical:html.match(/<link rel="canonical" href="([^"]+)"/)?.[1],xRobotsTag:response.headers.get("x-robots-tag"),links:[...new Set(links)],platform:page.platform || (page.path.startsWith('/guides/') ? (page.path.split('/')[2] || 'general') : ['youtube','instagram','facebook','tiktok','snapchat','whatsapp'].find(platform=>page.path.startsWith('/'+platform)) || 'general'),family:page.family || page.type});
}
const sitemap = await (await fetch(`${origin}/sitemap.xml`)).text();
let sitemapURLs=[...sitemap.matchAll(/<loc>(.*?)<\/loc>/g)].map(match=>match[1]);
if(sitemap.includes('<sitemapindex')) {
 const shards=await Promise.all(sitemapURLs.map(url=>fetch(origin+new URL(url).pathname).then(response=>response.text())));
 sitemapURLs=shards.flatMap(xml=>[...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map(match=>match[1]));
}
const paths = new Set(pages.map(page=>page.path)), reachable = new Set(['/']);
let previous;
do {
 previous=reachable.size;
 for(const row of htmlRows.filter(row=>reachable.has(row.path))) for(const path of row.links) if(paths.has(path)) reachable.add(path);
} while(previous!==reachable.size);
const expected = pages.filter(published).map(page=>`${site}${page.path}`);
const broken = htmlRows.flatMap(row=>row.links.filter(path=>!paths.has(path)).map(path=>({from:row.path,to:path})));
const quality=articles.map(page=>({path:page.path,...qualityGate(page,articles,core,reachable.has(page.path)?1:0)}));
const grouped = field => htmlRows.reduce((counts,row)=>({...counts,[row[field]]:(counts[row[field]]||0)+1}),{});
const duplicateMetadata = field => htmlRows.filter(row=>row.indexable).length - new Set(htmlRows.filter(row=>row.indexable).map(row=>row[field])).size;
const dispositions = briefs.reduce((counts, brief) => ({...counts, [brief.disposition?.classification || 'UNDISPOSED']: (counts[brief.disposition?.classification || 'UNDISPOSED'] || 0) + 1}), {});
const summary={schemaErrors:htmlRows.reduce((count,row)=>count+row.schemaErrors.length,0),publicPages:pages.length,indexablePages:expected.length,noindexPages:pages.length-expected.length,draftArticles:articles.filter(page=>page.status==='DRAFT').length,plannedUnwrittenBriefs:briefs.filter(brief=>!brief.disposition || brief.disposition.classification==='NEEDS_RESEARCH' || (brief.disposition.classification==='APPROVED_TO_WRITE'&&!articles.some(page=>page.path===brief.path&&published(page)))).length,dispositions,brokenDispositionDestinations:briefs.filter(brief=>['PUBLISHED','CONSOLIDATED'].includes(brief.disposition?.outcome)&&!paths.has(brief.disposition?.destination)).length,publishedArticles:articles.filter(published).length,publishedPublicPages:pages.length,sitemapURLs:sitemapURLs.length,duplicateTitles:duplicateMetadata("title"),duplicateH1s:duplicateMetadata("h1"),duplicateDescriptions:duplicateMetadata("description"),canonicalErrors:htmlRows.filter(row=>row.canonical!==site+row.path).length,noindexInSitemap:sitemapURLs.filter(url=>!expected.includes(url)).length,missingIndexable:expected.filter(url=>!sitemapURLs.includes(url)).length,duplicateSitemapURLs:sitemapURLs.length-new Set(sitemapURLs).size,brokenPublicURLs:htmlRows.filter(row=>row.status!==200).length,orphanIndexablePages:htmlRows.filter(row=>row.indexable&&!reachable.has(row.path)).length,brokenInternalLinks:broken.length,robotsMismatch:htmlRows.filter(row=>row.robots!==`${row.indexable?'index':'noindex'}, follow`||row.xRobotsTag).length,duplicatePagesBlocked:quality.filter(row=>row.errors.some(error=>/duplicate|collision/.test(error))).length,cannibalizationConflictsBlocked:quality.filter(row=>row.errors.includes('cannibalization_risk')).length,unsupportedTopicsBlocked:quality.filter(row=>row.errors.includes('unsupported_topic')).length,platforms:grouped('platform'),families:grouped('family'),target:5000,remaining:5000-expected.length,percentageComplete:expected.length/5000*100};
const report={summary,pages:htmlRows,sitemapURLs,brokenInternalLinks:broken,quality};
writeFileSync(new URL('../docs/content-system-audit.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(summary,null,2));
if(summary.schemaErrors||summary.canonicalErrors||summary.noindexInSitemap||summary.missingIndexable||summary.duplicateSitemapURLs||summary.brokenPublicURLs||summary.orphanIndexablePages||summary.brokenInternalLinks||summary.robotsMismatch||summary.duplicateTitles||summary.duplicateH1s||summary.duplicateDescriptions||summary.brokenDispositionDestinations||quality.some(row=>!row.passed)) process.exitCode=1;

if (process.argv.includes("--require-complete") && summary.plannedUnwrittenBriefs) { console.error("Expansion is unfinished: research/write candidates remain."); process.exitCode = 1; }
