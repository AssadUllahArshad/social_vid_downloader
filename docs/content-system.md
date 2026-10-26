# Editorial publication system — implementation and current limits

## Completed first-batch review

The target remains 5,000 useful indexable public pages. All 500 original briefs have final dispositions: **66 published articles, 434 consolidated variants, zero unresolved**. This turn added 46 articles to the prior 20. This is not a claim of 500 published articles: platform-name permutations and overlapping facets were consolidated under the user-benefit rule. Each decision, original intent and answer owner appears in `first-500-inventory.md` and the canonical brief store.

Coverage now includes nine device/storage guides, seven browser guides, fourteen troubleshooting guides, eight source-link how-tos, five platform-help guides, five format guides, four comparisons, four glossary guides, seven audio guides, two use cases and one standalone question. Each body is individually authored. Examples distinguish illustrations from historical live evidence. Source audio and AI-generated dubbing remain separate; no production AI landing or new downloader capability was added.

## One publication authority

- `content/pages/publication.json`: reviewed existing core routes; completed Guides landing is now indexable.
- `content/editorial/first-500-inventory.json`: the original briefs, benefit, priorities, keyword ownership, per-intent approval and final disposition; archived candidates do not create routes.
- `content/editorial/articles.json`: authored content, canonical path, state, review evidence, content-bound approval, related guides and saved gate results.
- `apps/web/src/lib/publication.ts`: server-only resolver combines current eligible records into the publication inventory. Metadata, rendering, links and sitemaps read it. Draft prose is not imported into public client components.

Published brief records reflect publication; consolidated records are ARCHIVED/nonindexable. The admin inventory overlays current authored eligibility and shows each disposition, answer owner and rationale. There are no writable browser CMS endpoints. `/admin/content/` is a noindex, read-only planning table, not a claim of an authenticated CMS. It contains no private media or credentials.

## Review lifecycle

IDEA → PLANNED → DRAFT → REVIEW → APPROVED → PUBLISHED. PUBLISHED can move to UPDATED or ARCHIVED; UPDATED requires REVIEW again. Approved and draft content remains nonpublic and noindex. Invalid status jumps are rejected.

An intent must have recorded approval before its article passes the quality gate. Passing publication also requires metadata/canonical validity, an answer-first intro, substantive content, a worked example, troubleshooting, sources, explicit editorial checks, compatible tool/hub links, two to five related eligible guides and an incoming directory link. Collision and similarity checks cover URL, title, H1, description, intent ownership, keyword overlap, intro, body and FAQs.

The score reports automated checks, not an assertion of ranking value. Human/agent editorial distinct-value and accuracy review is still required. Every candidate was reviewed for additional value beyond existing answers. Approved articles passed source/copy review; overlapping variants were consolidated with explicit public answer owners. Automated similarity remains a screening aid rather than proof of search demand.

Approvals store a SHA-256 digest of the reviewed payload. Changing content after approval removes runtime eligibility. Related unpublished dependencies also remove eligibility until repaired, preventing broken public links. This conservative rule can temporarily withhold dependent guides during pruning. The publish CLI validates the batch, then atomically replaces the article file; failed checks leave existing publication unchanged.

Commands:

```sh
node scripts/review-content.mjs            # Reports gates, never publishes
node scripts/review-content.mjs --publish  # Only after documented editorial review
node scripts/audit-publication.mjs         # Rendered URL, canonical, sitemap and link audit
```

The two `write-*-guides.py` files contain the first authored drafts; running them intentionally returns their owned records to DRAFT and requires re-review. They preserve unrelated authored records. They are not a general mass-content generator. `plan-content-batch.py` creates the initial inventory; rerunning it resets brief approvals and should not be used as an editing workflow.

## Routing, linking and sitemap

Eligible articles render at `/guides/{platform}/{intent}/`. Unwritten/draft/unapproved/archived URLs return 404, not public preview pages. Six noindex platform browse directories group guides by content family with collapsible sections and subject links. Every article link remains in server-rendered HTML and provides a meaningful incoming directory link. Home → Guides → directory → article provides crawlable reachability. Platform hubs additionally expose their relevant link guides. Articles link to the selected enabled tool, platform hub and related problems. Tools remain product-first and extraction logic is unchanged.

`/sitemap.xml` lists the same eligible indexable records used by metadata. At more than 1,000 entries it becomes a sitemap index; shards are `/sitemaps/{number}.xml`. Tests cover a 5,000-entry split with no draft leakage. Invalid shards return 404. Noindex browse directories are excluded. Robots still protects admin/API/internal/preview/temp/search paths and permits rendering assets.

## Database boundary

The project still lacks a running PostgreSQL service and Docker/PostgreSQL executables. This implementation does not pretend database publishing is available and does not reset or alter the existing database schema or seed data. Versioned JSON is the active editorial storage adapter. A future database adapter must use the same lifecycle, intent ownership, canonical mapping and publication resolver; independently published duplicate seed records must not become a second route authority. Authentication, persistence and authorized previews remain infrastructure work before database-backed editing.

## Current audit

- 119 public content/browse pages return 200 in the production HTTP audit.
- 90 indexable; 29 intentional noindex, including bounded subject/platform browse and pagination utilities.
- 74 published articles; 435 consolidated candidates across the historic and expansion inventories; 56 expansion candidates await research/writing. Zero authored drafts. The new expansion remains IN_PROGRESS.
- 90 sitemap URLs; zero canonical, robots, sitemap, internal-link, reachability or public-status errors.
- No published-content duplicate or cannibalization conflicts; all answer-owner destinations resolve.
- 90 / 5,000 = 1.80%; 4,910 indexable pages remain.

Evidence: `content-system-audit.json`, `content-quality-report.json`, `first-batch-copy-review.json`, `first-batch-completion.md`. Historical phase reports retain their original counts.

## Validation

166 API tests, 34 desktop/mobile browser tests and thirteen content/publication tests pass. TypeScript, ESLint and the Next.js Webpack production build pass. The production audit checks every public page, canonical, robots value, sitemap URL and internal link. No downloader engine files changed, and no fresh external-provider success is claimed by these regressions. The historic first queue is processed. The ongoing expansion is recorded in 5000-page-build-state.md; it is not complete.
