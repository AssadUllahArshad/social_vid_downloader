# Domain launch

Canonical frontend: `https://socialviddownloader.com`. Set `NEXT_PUBLIC_SITE_URL` before building. Prefer the same-origin Next `/api/v1/` proxy; an additional public API subdomain is unnecessary and would require a separate CORS/access review.

For a VM deployment, add an apex A record for the allocated IPv4 address and an AAAA record only if IPv6 is configured and reachable. Add `www` as a CNAME to the apex and configure a single permanent redirect to HTTPS apex. For a managed frontend, use the exact records issued by that host instead. Do not create DNS records pointing to localhost or example IP addresses.

Add the DNS TXT value issued by Search Console. Configure the real mail provider's MX, SPF, DKIM and DMARC records for `support@socialviddownloader.com` and `copyright@socialviddownloader.com`; prove both inboxes can receive external messages before launch. Operator: Hammad Hassan. No DNS, mailbox, or account changes were made automatically.

Issue a certificate for apex and www, verify renewal and redirects, then enable HSTS. Keep database, Redis, worker and internal API addresses absent from public DNS unless a private DNS zone is used.

Before switching traffic: verify backups, migration compatibility, production credentials, FFmpeg, health/readiness, tool samples, public routes, robots/sitemap, contact inboxes and rollback. Use a staging hostname with global noindex and access protection for rehearsal; do not point the production canonical at staging.
