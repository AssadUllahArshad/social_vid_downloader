# Google Search Console after deployment

Use [search-console-launch.md](search-console-launch.md) for detailed indexing guidance.

1. Verify a Domain property for socialviddownloader.com with the DNS TXT value supplied to your own Google account.
2. Open `https://socialviddownloader.com/robots.txt` and confirm public pages/assets are crawlable and private routes excluded.
3. Open `https://socialviddownloader.com/sitemap.xml`, check shard URLs and submit this sitemap index.
4. Inspect the homepage and key working downloader URLs, then representative reviewed articles. Confirm Google sees the apex canonical, HTTP 200 and index/follow.
5. Monitor indexing, sitemap errors, canonical selection and unsupported/noindex exclusion. Do not request indexing for drafts or unsupported tools.
6. Monitor field Core Web Vitals when sufficient traffic is available. Local lab observations are not field results.

You perform ownership verification and submission manually. No Search Console integration or account changes were performed locally.
