# Manual launch checklist — 14 October 2026

Follow [manual-deployment.md](manual-deployment.md) in order. Evidence: [processing/sitemap repair](processing-repair-final-report.md), [Snapchat repair](snapchat-share-repair.md), [frozen release inventory](launch-freeze.json). These are local verification records, not a claim of external deployment. Leave the host-specific checkboxes unchecked until you perform them.

- [x] Feature development, WhatsApp research, experimental work and SEO authoring frozen; candidates preserved
- [x] Source publication gates retain 1,020 approved URLs, 22 public processing utilities and 13 languages
- [x] WhatsApp Status downloading remains unsupported; no QR/session/status retrieval or app download advertised
- [x] Existing full HTTP/media/security evidence reused; no unnecessary new full audit/build
- [ ] Source archive checksum and individual file manifest verified after transfer
- [ ] Production `.env` restricted to owner; independent random PostgreSQL/IP secrets set
- [ ] Fixed private web peer matches `TRUSTED_PROXY_IPS`; subnet does not conflict; Nginx overwrites identity
- [ ] Only SSH/80/443 exposed; unknown hosts rejected; database/cache/API/web ports private
- [ ] Docker production images built with Webpack and matching source/content/lockfiles
- [ ] PostgreSQL and Redis healthy; migration passes without seed/reset; persistent DB volume retained
- [ ] API/web running; FFmpeg/FFprobe/fonts and expected processing capabilities available
- [ ] Private `/health` and `/ready` pass; no additional worker service required
- [ ] DNS apex/www set to actual host; certificates obtained before TLS config is loaded
- [ ] Nginx config validated; HTTPS/apex redirects and renewal dry-run pass; HSTS enabled afterward
- [ ] `smoke-production.mjs` passes on final HTTPS origin
- [ ] `smoke-sitemap.mjs` matches all 1,020 frozen canonical URLs; no extra/missing/duplicate paths
- [ ] Representative canonical/hreflang/robots/noindex/404 checks pass; drafts/Story remain nonpublic
- [ ] Desktop/mobile and Arabic/Urdu navigation/RTL checks pass
- [ ] Real upload, preview, downloaded output, cancellation and expiry verified on host; 200 MiB bounded ingress retained
- [ ] Authorized public downloader smoke performed; Beta/degraded labels retained
- [ ] Separate visitor rate identity confirmed without weakening production limits
- [ ] Daily encrypted off-host DB/release backups scheduled and monitored; isolated restore rehearsed
- [ ] Prior release/images retained; rollback preserves database volumes and content correspondence
- [ ] Support/copyright mailboxes, operator policies and private monitoring checked by owner
- [ ] Search Console ownership verified manually; sitemap index submitted; index/noindex exclusions reviewed
- [ ] Final host smoke passes before traffic opens

No public CMS login, analytics SDK, WhatsApp retrieval or Android companion app is part of this release. Do not resume feature/content work during launch. Host setup and owner-operated services are deployment tasks, not newly discovered website errors.
