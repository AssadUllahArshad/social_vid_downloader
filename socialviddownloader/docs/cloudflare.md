# Cloudflare manual setup

Follow [cloudflare-production.md](cloudflare-production.md) for the full configuration. You make the changes after deployment.

1. Set A/AAAA only to assigned working origin addresses and configure www to canonicalize to the apex.
2. Use Full (strict) TLS with a valid origin certificate. Enable HTTPS redirect after origin TLS works; avoid contradictory origin/edge redirects.
3. Cache immutable Next static assets; enable available compression. Never cache `/api/`, job/file/thumbnail responses, admin, errors or personalized token URLs. Do not apply Cache Everything to the whole site.
4. Configure bot protection and edge rate limits cautiously; API/media streaming must remain functional. Keep application rate limiting enabled.
5. Trust CF-Connecting-IP only from Cloudflare's exact current network ranges. Restrict origin access and preserve verified client identity through Nginx; never trust arbitrary forwarded headers.
6. Test redirects, download Range responses, expiration, robots/sitemap and mobile tools after enabling the edge. No Cloudflare settings were changed during local preparation.
