import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { STATES, published, fingerprint, transition, qualityGate, inventoryGate, publicationInventory, sitemapChunks, similarity } from "../src/lib/editorial/workflow.mjs";
import { collectionPages, PAGE_SIZE } from "../src/lib/editorial/collections.mjs";
const load = path => JSON.parse(readFileSync(new URL(path, import.meta.url), "utf8"));
const core = load("../../../content/pages/publication.json");
const allBriefs = load("../../../content/editorial/first-500-inventory.json");
const briefs = allBriefs.filter(brief => brief.batch === "first-500");
const articles = load("../../../content/editorial/articles.json");
describe("editorial publication", () => {
  it("gives every original brief a final disposition and a public answer owner", () => {
    assert.equal(briefs.length, 500);
    assert.equal(new Set(briefs.map(page => page.path)).size, 500);
    const paths = new Set(publicationInventory(core, articles).map(page => page.path));
    const approved = briefs.filter(page => page.disposition?.classification === "APPROVED_TO_WRITE");
    const merged = briefs.filter(page => page.disposition?.classification === "MERGE_WITH_EXISTING");
    assert.equal(approved.length, 66);
    assert.equal(merged.length, 434);
    assert.ok(briefs.every(page => page.disposition?.reason && page.disposition?.targetUser && page.disposition?.primaryQuestion && paths.has(page.disposition.destination)));
    assert.ok(approved.every(page => page.status === "PUBLISHED" && page.indexable && page.disposition.outcome === "PUBLISHED" && articles.some(article => article.path === page.path && published(article))));
    assert.ok(merged.every(page => page.status === "ARCHIVED" && !page.indexable && page.disposition.outcome === "CONSOLIDATED" && !paths.has(page.path)));
    assert.ok(briefs.every(page => !inventoryGate(page, briefs, core).length));
  });
  it("requires the full lifecycle and binds approval to content", () => {
    assert.deepEqual(STATES, ["IDEA", "PLANNED", "DRAFT", "REVIEW", "APPROVED", "PUBLISHED", "UPDATED", "ARCHIVED"]);
    const page = { ...articles[0], status: "DRAFT", indexable: false };
    assert.throws(() => transition(page, "PUBLISHED"));
    const review = transition(page, "REVIEW");
    assert.throws(() => transition(review, "APPROVED", { passed: false, digest: fingerprint(review) }));
    const approved = transition(review, "APPROVED", { passed: true, digest: fingerprint(review) });
    assert.throws(() => transition({ ...approved, intro: "Changed" }, "PUBLISHED", { passed: true, digest: fingerprint(approved) }));
    const live = transition(approved, "PUBLISHED", { passed: true, digest: fingerprint(approved) });
    assert.ok(published(live));
    assert.equal(transition(live, "UPDATED").indexable, false);
    assert.equal(transition(live, "ARCHIVED").indexable, false);
  });
  it("rejects duplicates, unsupported topics, placeholders, orphan and broken links", () => {
    const page = articles[0];
    assert.ok(inventoryGate(page, [page, { ...page }], core).includes("collision_path"));
    const twin = { ...page, path: "/guides/general/another-container-answer/", title: "Another container answer", h1: "Another container answer", intent: "different:intent", primaryKeyword: "another container", description: "A separately labelled description that still duplicates the same underlying answer and example." };
    const faq = [{question:"Which container should I choose?", answer:"Use the source codecs and your intended player to choose compatible packaging."}];
    assert.ok(qualityGate({...page,faq},[{...twin,faq}],core,1).errors.includes("near_duplicate_faq"));
    assert.ok(inventoryGate(page,[page,{...twin,primaryKeyword:page.primaryKeyword.split(" ").reverse().join(" ")}],core).includes("keyword_overlap"));
    assert.ok(qualityGate(twin, [...articles, twin], core, 1).errors.includes("near_duplicate_content"));
    assert.ok(qualityGate(page, articles, core, 0).errors.includes("orphan"));
    assert.ok(qualityGate({ ...page, related: ["/not-real/", page.path] }, articles, core, 1).errors.includes("broken_or_unpublished_internal_link"));
    assert.ok(qualityGate({ ...page, intro: "TODO" }, articles, core, 1).errors.includes("placeholder_content"));
    assert.ok(inventoryGate({ ...page, path: "/guides/snapchat/snapchat-story-viewer/" }, articles, core).includes("unsupported_topic"));
    assert.ok(qualityGate({ ...page, inventoryApproval: null }, articles, core, 1).errors.includes("inventory_approval_required"));
    assert.ok(qualityGate({ ...page, canonical: "/alias/" }, articles, core, 1).errors.includes("canonical_collision"));
  });
  it("only exposes current approved payloads and uses the same set for sitemap", () => {
    const pages = publicationInventory(core, articles);
    assert.equal(pages.filter(page => page.type === "tool").length, 10);
    const stale = { ...articles[0], intro: "Edited without approval" };
    assert.ok(!publicationInventory(core, [stale]).some(page => page.path === stale.path));
    const sitemap = sitemapChunks(pages).flat();
    assert.deepEqual(sitemap.map(page => page.path).sort(), pages.filter(published).map(page => page.path).sort());
    assert.ok(!sitemap.some(page => !page.indexable || page.canonical !== page.path));
    for (const state of STATES.filter(state => state !== "PUBLISHED")) {
      assert.ok(!publicationInventory(core, [{ ...articles[0], status: state }]).some(page => page.path === articles[0].path));
    }
  });
  it("splits at 1000, retains every canonical page, and excludes drafts", () => {
    const pages = Array.from({length:5000}, (_, i) => ({path:`/guide-${i}/`, canonical:`/guide-${i}/`, status:"PUBLISHED", indexable:true}));
    const chunks = sitemapChunks([...pages, {path:"/draft/",canonical:"/draft/",status:"DRAFT",indexable:true}]);
    assert.equal(chunks.length, 5);
    assert.equal(chunks.flat().length, 5000);
    assert.ok(chunks.every(chunk => chunk.length === 1000));
  });
  it("every published article passes critical checks and has incoming links", () => {
    assert.ok(articles.length);
    for (const page of articles) {
      assert.equal(page.approval.digest, fingerprint(page));
      assert.deepEqual(qualityGate(page, articles, core, 1).errors, []);
      assert.ok(publicationInventory(core, articles).some(other => other.path === `/guides/${page.platform}/`));
      assert.equal(page.canonical, page.path);
    }
  });
  it("keeps research briefs nonpublic and requires distinct-task review", () => {
    const pages = publicationInventory(core, articles);
    assert.equal(new Set(allBriefs.map(brief => brief.id)).size, allBriefs.length);
    const research = allBriefs.filter(brief => brief.disposition?.classification === "NEEDS_RESEARCH");
    assert.ok(research.every(brief => !pages.some(page => page.path === brief.path) && !brief.inventoryApproval?.approved));
    const article = articles.find(page => page.batch?.startsWith("expansion-"));
    assert.ok(article);
    const draft = {...article, path:"/guides/general/nonpublic-research-fixture/", canonical:"/guides/general/nonpublic-research-fixture/", status:"DRAFT", indexable:false};
    assert.ok(!publicationInventory(core,[...articles,draft]).some(page=>page.path===draft.path));
    assert.ok(qualityGate({...article,semanticReview:{state:"GAP_IDENTIFIED_RESEARCH_PENDING"}},articles,core,1).errors.includes("distinct_task_review_required"));
  });
  it("allows reviewed WhatsApp education without advertising a downloader", () => {
    const page = {...articles[0], platform:"whatsapp", contentRole:"education", targetDownloader:null, hub:"/guides/", path:"/guides/whatsapp/educational-fixture/", canonical:"/guides/whatsapp/educational-fixture/", title:"WhatsApp educational fixture", h1:"WhatsApp educational fixture", primaryKeyword:"whatsapp educational fixture", intent:"task:educational-fixture"};
    assert.ok(!inventoryGate(page,[page],core).includes("unsupported_target_downloader"));
    assert.ok(!inventoryGate(page,[page],core).includes("missing_intent_fields"));
    assert.ok(inventoryGate({...page,contentRole:undefined},[page],core).includes("unsupported_topic"));
    assert.ok(inventoryGate({...page,targetDownloader:"/whatsapp-status-downloader/"},[page],core).includes("unsupported_target_downloader"));
    assert.ok(inventoryGate({...page,path:"/guides/whatsapp/whatsapp-status-downloader/"},[page],core).includes("unsupported_topic"));
    page.approval={digest:fingerprint(page)};
    const visible=publicationInventory(core,[...articles,page]);
    assert.ok(visible.some(row=>row.path===page.path));
    assert.ok(visible.some(row=>row.path==="/guides/whatsapp/" && !row.indexable));
  });
  it("keeps cached similarity content-bound across edits and sizes", () => {
    const original = "one two three four five six seven";
    assert.equal(similarity(original, original),1);
    assert.equal(similarity(original,"unrelated words with different sequence altogether here"),0);
    assert.equal(similarity(original,"one two three four five six changed"),2/3);
    assert.equal(similarity("one two","one two",2),1);
    assert.equal(similarity("one two","one two",5),0);
  });
  it("scales collection pages without indexable pagination duplicates", () => {
    const samples = Array.from({length:5000},(_,i)=>({platform:"general",family:i%2 ? "captions" : "formats"}));
    const rows=collectionPages(samples);
    assert.equal(PAGE_SIZE,24);
    assert.equal(rows.filter(row=>row.path.startsWith('/guides/general/')).length,Math.ceil(5000/PAGE_SIZE));
    assert.equal(new Set(rows.map(row=>row.path)).size,rows.length);
    assert.ok(rows.every(row=>!row.indexable && row.canonical===row.path));
    assert.ok(!rows.some(row=>row.path.endsWith('/page/1/')));
    assert.deepEqual(collectionPages([]),[]);
  });
  it("prunes long dependency chains while retaining an independent approved article", () => {
    const chain = Array.from({length:1500},(_,i)=>{
      const page={...articles[0],type:"article",path:`/guides/general/chain-${i}/`,canonical:`/guides/general/chain-${i}/`,related:[`/guides/general/chain-${i+1}/`]};
      page.approval={...page.approval,digest:fingerprint(page)};
      return page;
    });
    const independent={...articles[0],related:[articles[0].targetDownloader]};
    independent.approval={...independent.approval,digest:fingerprint(independent)};
    const inventory=publicationInventory(core,[...chain,independent]);
    assert.ok(!inventory.some(page=>page.path.includes('/chain-')));
    assert.ok(inventory.some(page=>page.path===independent.path));
  });
});
