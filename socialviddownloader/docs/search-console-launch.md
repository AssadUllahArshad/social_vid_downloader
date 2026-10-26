# Search Console launch

1. Serve `https://socialviddownloader.com/` through working HTTPS and confirm the production origin, not the local development server.
2. Add a Domain property for `socialviddownloader.com` in Google Search Console. Copy Google's issued DNS TXT verification value into DNS; do not invent a token or expose an internal environment secret. This step requires the domain owner's account.
3. Verify the property after DNS propagation. Add an optional public HTML/meta verification method only if the operator chooses a URL-prefix property instead.
4. Open `https://socialviddownloader.com/robots.txt` and `https://socialviddownloader.com/sitemap.xml`. The latter is the sitemap index and points to canonical `/sitemaps/1/` shards. Submit the index URL in Search Console's Sitemaps screen.
5. Inspect the homepage, each primary supported downloader, a platform hub and a published guide. Confirm a live HTTP 200, indexing allowed, the HTTPS self-canonical, and the rendered content. Unsupported tools and unfinished drafts must not be submitted.
6. Request indexing only for a small selection of important complete pages if needed. Let normal links and the sitemap drive broader discovery; do not submit thousands of indexing requests.
7. Monitor Page indexing, crawl errors, selected canonicals, sitemap processing and real-user Core Web Vitals. Google determines indexing; a successful local audit is not an indexing guarantee.

The launch freeze preserves draft records without public routes. Keep drafts, previews, admin routes, API routes, aliases and unsupported Snapchat Story URLs out of sitemaps. Re-run `node scripts/audit-publication.mjs` against production using `AUDIT_ORIGIN=https://socialviddownloader.com` after deployment. The `--require-complete` option is inappropriate during the intentionally frozen expansion because saved drafts remain unfinished.

References: [Google verification](https://support.google.com/webmasters/answer/9008080), [sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview). Account verification and sitemap submission have not been performed by this agent.
