# Two-stage content architecture

This is an in-progress system and inventory checkpoint, not a completed 5,000-page site.

The current canonical stores are `content/pages/publication.json` (core),
`content/editorial/first-500-inventory.json` (stable candidate records and
scope decisions), and `content/editorial/articles.json` (authored payloads).
There is no new writable duplicate CMS. The TSV seed collection describes raw
intent hypotheses; its idempotent importer writes only to the existing registry.

## Stage A: bulk inventory

`build-stage-a-inventory.py` registers independently described task hypotheses
with stable IDs, candidate URLs, platform, family, primary topic/intent,
secondary queries, user, problem, benefit, existing-answer gap, tool, hub,
suggested links, metadata, priority and a nonpublic status. It does not author,
review, approve or publish a page. Generated candidates are not measured demand.

`consolidate-stage-a-intents.py` records explicit task ownership. Changing an
application or platform name alone does not earn a second URL. A canonical
owner can itself be a draft: both its route and its consolidated variants remain
nonpublic. Consolidation into a draft does not claim a working public redirect.
Mechanistically different tasks must remain separate pending review even when
lexical similarity is high.

`audit-stage-a-inventory.mjs` checks all new records for required planning
fields, unique stable IDs and paths, canonical consistency, supported tool
scope, existing suggested peers and draft isolation. Its comparison shortlist
covers all current authored answers and active candidate tasks. Scores are
review aids; neither observed SERP equivalence nor semantic approval is claimed.
`--http` verifies all current Stage A candidate URLs return 404.

Both shortlist scripts use `intent-screening.mjs`. Its exact native-index
hypothesis matcher removes shared research instructions from comparison text
while retaining the named operation, application and media resource terms.
The auditor labels these records `NATIVE_TOPIC_ONLY_SCOPE_RESEARCH_REQUIRED`:
their documentation topic is still weaker evidence than a defined user problem.
Token overlap does not understand operation direction or establish a semantic
duplicate. Tests cover unrelated operations sharing boilerplate, distinct audio
and picture resources, ordinary descriptions and absent evidence. Scores never
change a candidate's disposition or publication eligibility.

Bulk source discovery also records official documentation references in `stage-a-source-opportunities.json`. These have source IDs rather than page IDs, reserve no route and do not count toward the page target. `link-stage-a-evidence.py` associates native-workflow hypotheses with provider-matched reference leads; the individual primary bodies still need review before authoring.

`discover-native-workflow-intents.py` additionally collects media-operation
hypotheses from the saved official Premiere and Final Cut navigation indexes.
It excludes basic navigation, keyboard/UI, version and unrelated source topics,
coalesces exact operation aliases and appends only discovery seeds. Each native
proposal receives its exact originating documentation lead, marked unreviewed.
These proposals still require answer-scope consolidation and body review;
having an official documentation URL is not evidence of a separate SEO intent.
The consolidation pass resolves every archived alias to one active draft or
published owner and rejects cycles before writing. The isolation audit also
rejects archived owners and mismatched ownership/link destinations.
When an active owner is later published, the consolidation pass synchronizes
the alias decision without publishing the alias. Regression tests cover owner
publication, chained draft ownership, idempotence and rejecting a cycle before
the registry is modified. Source-ID/URL uniqueness and every candidate's
source-lead association are also checked; reference navigation duplicates do
not inflate source or page counts.

The full master inventory is still incomplete. Do not describe the number of raw
registry records, merged aliases or unresolved hypotheses as indexable pages.

## Stage B: complete, review and publish

After inventory scope review, complete page-specific content in larger batches
of approximately 250–500 where defensible. Primary evidence and complete peer
review remain prerequisites to writing approval. Each authored payload follows
DRAFT → REVIEW → APPROVED → PUBLISHED with fresh content-bound approval.
Existing content edits require a fresh review and approval digest.

The reusable server-rendered guide route consumes structured intros, sections,
optional steps, examples, FAQs, source records and related guides. Families
control classification and subject directories. Family-specific content should
express its actual task: diagnosis and causes for troubleshooting, native steps
for device/browser help, real differences for comparisons, timing/resources for
captions, stream roles for audio, and resource/version scope for creator work.
Do not hand-code thousands of React files or populate shared paragraphs through
keyword substitutions. More specialized structured blocks can be added during
the renderer phase if a reviewed batch needs them.

## Public eligibility and scale

`publicationInventory` accepts authored PUBLISHED + indexable + self-canonical
records only with matching approval fingerprints and valid dependencies. Briefs
alone cannot resolve through `getArticle`. Unfinished routes return 404, which
avoids public placeholder content and preview discovery. Any future preview
must require its intended access and use noindex/nofollow.

All public links, category counts, static guide parameters and sitemap shards
use the same eligible article set. Browse pages contain at most 24 articles;
sitemap shards contain at most 1,000 URLs. Drafts are excluded from related
links, public counts, browse navigation and XML. Article data is server-only;
main navigation remains compact and downloader pages remain product-first.

At larger checkpoints: run static gates, publication tests, TypeScript, lint,
production build, programmatic public-route audits and representative browser
checks. Validate all candidate route exclusions without browser-testing every
draft individually. Save the source-registry and actual HTTP counts separately
when a build has not yet incorporated approved content.

The downloader engine and provider logic are unchanged by this inventory work.
