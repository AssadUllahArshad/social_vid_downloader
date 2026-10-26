# Cloudflare production

Use the apex domain as canonical. Point its A/AAAA records to the chosen ingress, or use the host's supported CNAME arrangement; no server address is assumed here. Proxy only the intended public frontend. PostgreSQL, Redis and the internal API must remain private.

Use Full (strict) TLS with a valid origin certificate. Redirect HTTP to HTTPS, redirect `www` once to the apex, and enable HSTS only after verifying origin HTTPS. Never use Flexible TLS. Review DNSSEC and account MFA with the domain owner.

Cache hashed `/_next/static/` assets. Bypass shared cache for `/api/`, `/admin/`, `/internal/`, previews, temporary/download files and any personalized response. Honor `Cache-Control: no-store` and do not cache errors or signed file links. Do not enable "Cache Everything" across the whole site. Public SEO pages may use ordinary Next revalidation; sitemap changes require a fresh deployment of the versioned content.

Apply edge request-rate limits and body-size limits. Keep challenges off API file streams and source-analysis responses. Bot controls must still allow legitimate search crawlers and assets. Put administrative operations behind an allowlist/VPN; the browser admin shell is disabled in production.

Trust client identity only through a controlled chain. Restrict origin access to Cloudflare (or use a tunnel), then configure the ingress to validate trusted Cloudflare addresses before using CF-Connecting-IP. Always overwrite the frontend's configured `TRUSTED_CLIENT_IP_HEADER`. The Next proxy forwards only a validated IP from that configured header; FastAPI accepts it only from exact `TRUSTED_PROXY_IPS`. Never pass arbitrary client X-Forwarded-For unchanged.

Cloudflare account/DNS/TLS configuration is an external launch step, not a completed local test. Validate redirects, cache bypass, client-specific limiting, TLS and final public headers from outside the origin after configuration.

References: [Cloudflare Full (strict) TLS](https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/), [Cloudflare forwarded headers](https://developers.cloudflare.com/fundamentals/reference/http-headers/).
