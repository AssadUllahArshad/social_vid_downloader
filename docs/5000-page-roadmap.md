# Roadmap to 5,000 useful indexable pages

The target remains **5,000 total useful indexable public pages**, including the reviewed core pages. Counts are capacity allocations, not instructions to multiply keywords or guarantee publication. The first 500 supporting-page briefs are in `content/editorial/first-500-inventory.json`; they are not 500 published pages.

## Current remaining-opportunity allocation

Planning starts from 90 indexable pages and 4,910 remaining opportunities. These are research targets, not validated page briefs or publication quotas.

| Platform | Planning allocation |
|---|---:|
| YouTube and Shorts | 1,050 |
| Instagram | 850 |
| Facebook | 800 |
| TikTok | 700 |
| Snapchat Spotlight | 300 |
| General/cross-platform | 1,000 |
| WhatsApp truthful education | 210 |
| **Total** | **4,910** |

| Content family | Planning allocation |
|---|---:|
| Troubleshooting | 1,050 |
| FAQ/Q&A | 850 |
| Device/browser/OS | 650 |
| Platform help/workflow | 600 |
| Formats/codecs/quality | 500 |
| Comparisons/use cases | 350 |
| Audio/captions | 250 |
| Glossary/education | 250 |
| Privacy/permission | 150 |
| Creator/archive/editing | 210 |
| **Named family allocations** | **4,860** |
| Unallocated research opportunity | 50 |
| **Total opportunity framework** | **4,910** |

The requested named family targets sum to 4,860, leaving 50 unspecified opportunities within the 4,910 framework. This arithmetic does not create 50 candidate records. Platform and family allocations describe the same opportunity, not additive counts. Do not force either distribution. Snapchat means Spotlight only; WhatsApp means education without a supported public URL downloader. No Story tool or commercial AI capability is allocated.

## URLs and route ownership

- Existing product URLs remain unchanged and product-first.
- Supporting articles: `/guides/{youtube|instagram|facebook|tiktok|snapchat|whatsapp|general}/{intent-slug}/`.
- Browse directories: `/guides/{platform}/`; intentionally noindex utilities, not alternative keyword landing pages.
- No URL is created for PLANNED/DRAFT/REVIEW/APPROVED/UPDATED/ARCHIVED content. A draft returns 404 rather than an indexable preview. IDEA through ARCHIVED remain administrative records.
- No parameter, device-name permutation, pagination alias, language preference, or translated-title record automatically creates a canonical page.

## Publication phases

1. Reviewed core foundation: 16 indexable pages, including the completed Guides landing.
2. First batch review is complete: all 500 candidates have final decisions; 66 distinct supporting articles are published and 434 variants are consolidated. No unresolved briefs remain. This is not 500 published articles; the numerical ambition was subordinated to distinct useful answers. See `first-500-inventory.md` for every decision.
3. Expand to 1,500 total indexable pages after reviewing source evidence, intent ownership and existing article usefulness.
4. Expand to 3,000 after diagnosing actual search/user demand and pruning failed or overlapping pages.
5. Expand to 5,000, keeping provider limitations, canonical ownership, links and provenance current.

The phases define review checkpoints within the autonomous continuation. Completing a checkpoint is not a stop condition. Publication does not guarantee Google indexing.

## Intent, duplication and cannibalization

One page owns one problem and its answer. Keyword variants belong in the same record. Distinct user benefit is mandatory. A platform/device variant must demonstrate a different workflow or diagnostic outcome; swapping a name is insufficient. General file-format and browser-storage problems should normally have a general canonical owner.

The gate checks normalized URL/title/H1/description/keyword/intent collisions, URL and heading similarity, intro/body/FAQ shingle similarity, and intent similarity. Similarity is a screening tool, not proof of unique user benefit. Editorial distinct-value review remains mandatory. Merge overlapping answers, redirect only previously public URLs when appropriate, and repair incoming links before removing a public record.

## Linking and sitemap

Keep main navigation small. Home links to Guides and platform hubs; Guides links to platform directories; directories link to eligible articles. Every article links to its relevant tool and platform hub plus two to five related eligible guides. Related links must be selected for the reader's next problem rather than added solely for anchor coverage. Categories supply an incoming crawlable link, and graph tests check reachability from Home.

Only the shared publication inventory controls visible article routes, metadata, canonical URLs, directory links and sitemaps. At 1,001 indexable URLs, `/sitemap.xml` automatically becomes an index of 1,000-URL shards under `/sitemaps/{number}.xml`. Shards exclude noindex, unpublished and noncanonical content. There is no second CMS sitemap source.

## Review, noindex and pruning

New authored payloads are DRAFT/noindex. REVIEW requires actual source-specific evidence, a useful worked example and substantive original prose. APPROVED requires passing gates and recorded review provenance. PUBLISHED requires the same content digest as the approval. Editing public content moves it to UPDATED, removing eligibility until re-reviewed. ARCHIVED records do not render or enter internal links.

Keep unsupported functionality, empty landings, incomplete legal/operator details, admin pages and browse utilities noindex. Never convert drafts to index to hit a quota. Quarterly review should consolidate competing intents, fix broken sources, update changed workflows, archive unsafe/unsupported claims, and prune pages that fail to provide a distinct useful answer. An automated score alone cannot authorize publication.

## Storage and CMS boundary

Current editorial content is versioned JSON, loaded only by server-side publication code. CLI review is the publication write path; the admin table is a read-only inventory. This provides one working publication source without pretending that the unavailable PostgreSQL service is live.

The existing PostgreSQL schema is an eventual persistence adapter, not a separate live page authority. Before adding database-driven editing, preserve the same resolver/gates/transitions, import stable paths and intent ownership, migrate approved content with its review evidence, and ensure only one storage adapter supplies public records. Database authentication/editor permissions, revision storage, preview authorization and persistence remain a separate infrastructure prerequisite. Do not enable both JSON and independently seeded CMS pages for the same canonical URL.

## Historical first expansion checkpoint

Baseline is 82 indexable pages. The expansion checkpoint has 90 indexable pages (eight new caption articles), 65 discovered candidates, one merge and 56 candidates awaiting research/writing. This is not completion and not evidence that distinct intents are exhausted. Stable IDs, gap rationales, primary-topic ownership and progress live in the existing canonical brief store; the required master inventory and build-state documents are generated views. The earlier first-500 review remains historical and complete.

Historical remaining-family planning allocations: troubleshooting 1,000; FAQ 900; device/browser/OS 700; platform workflows 600; format/codec/quality 500; comparisons/use cases 350; audio/captions 250; glossary 250; privacy/permission 150; creator/archive workflows 218. Total 4,918. These are planning targets, not validated topics or an instruction to multiply platform names.

Remaining-platform allocations: YouTube 1,000; Instagram 850; Facebook 800; TikTok 700; Snapchat Spotlight 350; general 1,000; truthful WhatsApp information 218. Total 4,918. WhatsApp research must not become a fake public Status-download workflow.

Historical next action at that checkpoint was HDR/SDR research, followed by the saved queue; both are now resolved. Before authoring, compare task, answer coverage, questions and expected intent against the immutable baseline and candidate peers. SERP similarity remains a hypothesis unless actually researched. Seek additional distinct gaps after processing the queue. Stop only at approximately 5,000 useful indexable URLs or after defensible discovery exhaustion; neither condition is currently satisfied.

Browse architecture uses /topics/{family}/ and /guides/{platform}/, with 24-item numbered pages. All listings are noindex, canonical to themselves and excluded from sitemap. Their content stays server-side. No pagination alias for page 1 is created. Active article changes still require content-bound review and approval. Checkpoint publication permits unrelated research records to remain safely nonpublic; the final audit with --require-complete must fail until all candidates are resolved.

## Historical October 7 continuation: 157 indexable pages

The verified continuation starts from 90 indexable URLs and adds 67, reaching 157 indexable, 193 public HTTP 200 and 36 noindex pages. All 584 registered briefs have final decisions: 141 published, 442 consolidated and one rejected duplicate. Nineteen new candidates were discovered during this continuation. The saved 56 pending candidates yielded 50 articles and six consolidations; further discovery yielded 17 articles, one consolidation and one duplicate rejection.

The semantic map is refreshed from actual production-rendered pages. The preserved 90-page snapshot records this request's starting state. Intent discovery remains open; neither the 5,000-page target nor a defensible maximum has been reached. Do not rerun historical first-batch planning/disposition tools.

Remaining-opportunity planning allocations at the 90-page starting state: troubleshooting 1,050; FAQ 850; device/browser 650; platform help 600; formats/codecs 500; comparisons 350; audio/captions 250; glossary 250; privacy/permission 150; creator workflows 210. Named family allocations total 4,860, with 50 unallocated opportunities in the 4,910 framework. These are allocations, not quotas or validated page counts. The current numerical remainder is 4,843.

Platform allocations: YouTube/Shorts 1,050; Instagram 850; Facebook 800; TikTok 700; Snapchat Spotlight 300; general 1,000; WhatsApp education 210. Total 4,910 at the starting state. WhatsApp has an explicit educational publishing role, noindex browse directory and no downloader CTA; its URL-download capability remains unsupported.

Continue source-led discovery across platform help, devices/browsers, language/captions, playback and creator workflows. Compare full existing answers and peer briefs before drafting. Do not regenerate a resolution alias, HD handoff alias or a platform permutation of a general storage answer. Potential frontier areas need actual scope/source review; they are not pre-approved topics. All current recorded candidates are resolved, which does not mean the broader opportunity inventory is complete.

At each checkpoint run the review gate, production build, full HTTP audit and refreshed semantic map, then generate the master/build-state views with report-content-build.mjs and the matching SEO/page inventory with report-seo-checkpoint.mjs. The latter fails if the HTTP audit's public URL set is stale. Preserve provider behavior and content-bound approval digests.

## October 8 continuation checkpoint

The latest checkpoint has 268 indexable pages, 311 public HTTP 200 pages, 43 noindex pages and 268 sitemap URLs. The original 90-page baseline is preserved; 178 indexable pages have been added, leaving 4,732 to the target (5.36%). There are 2589 canonical candidate records: 252 published articles, 1094 consolidations and 15 rejection. The 2089 expansion records include 1875 raw Stage A hypotheses and 1228 nonpublic draft page records; they are not a completed or approved 5,000-page inventory.

The October 8 continuation began at 157 indexable pages and has added 111 net indexable pages. 638 candidate overlaps were consolidated, including a Windows N duplicate identified by full-answer re-review. Source-specific publishing, caption and retention updates were reviewed again. Candidate screening now excludes self-comparisons, duplicate comparison URLs and archived aliases. A metadata copy review replaced 145 word-truncated descriptions with complete sentences through fresh digest-bound approval. The drafting helper now uses complete answer sentences. A reproduced narrow-screen header overflow was repaired with CSS wrapping and covered at 320px and 390px. Downloader and provider behavior were not changed.

Continue the two-stage bulk inventory workflow. Scope decisions and raw hypotheses are registered before full article writing; primary research and complete peer review remain prerequisites for writing approval. No target or intent-exhaustion stop condition has been reached. Generated build-state and SEO reports provide current counts and validation, superseding historical checkpoints above.
