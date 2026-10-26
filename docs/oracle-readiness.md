# Deployment audit, 23 October 2026

## Decision

Oracle Always Free A1, one Ubuntu ARM64 VM, existing Compose stack, host Nginx,
Let's Encrypt and Cloudflare DNS-only. Follow [the launch checklist](oracle-zero-cost-launch.md).
Expected hosting cost is $0 within verified account allowances, not a guarantee.
If free capacity is unavailable, pause rather than purchase infrastructure.

## Verified from source

- Next 16.3.8, locked React 19.3.1, TypeScript 5.9.3, Tailwind 4.3.3.
- FastAPI 0.128.8, Python 3.12 container, yt-dlp 2026.8.19, PostgreSQL 17, Redis 7.
- Standalone Next server required; dynamic Node proxies prevent unchanged static export.
- Redis holds ephemeral sessions/jobs/rate counters, not a durable queue.
- One API process runs bounded background tasks and subprocesses. Crashed jobs
  expire and require resubmission; durable resumption is not implemented.
- URL/CDN allowlists, pinned public-IP connections, redirect checks, file/time
  bounds, rate limits, private media delivery and periodic expiry cleanup exist.
- Database migrations and private dependency bindings exist; public CMS auth/editing
  is not implemented. Production admin pages are deliberately disabled.
- ARM execution is plausible but native images/wheels/codecs remain unverified.

## Changes prepared

- Container log rotation, PostgreSQL/Redis memory/PID limits, non-evicting bounded
  ephemeral Redis, API readiness/web health checks, healthy API startup dependency.
- Five-minute API stop grace and conservative one-job production example.
- Nginx access logs disabled per server to avoid logging media capability tokens.
- Windows-aware Python selection in existing editorial ownership tests.
- Detailed account, cost, DNS, TLS, backup, restore, rollback and launch checklist.

## Executed checks and limitations

- Old release archive checksum and 433 internal hashes passed; current source differs.
- Differences reviewed: Windows extraction compatibility, generated Next types,
  React patch update. Existing work preserved. Old archive is not today's release.
- Production Compose YAML parsed with installed js-yaml; actual Docker merge/build
  and runtime checks are pending because Docker is absent.
- ESLint passed. Packaging tests: four passed. Focused ownership tests: three passed
  with a project-local temporary directory.
- Frontend build compiled, but the interrupted command did not yield a complete
  successful production build result. Do not report the whole build as passing.
- TypeScript `tsc --noEmit --incremental false` passed after the interruption.
- Full frontend test suite passed: 29 tests, zero failures.
- C: is nearly full; D: has approximately 19 GiB free. Tests use a temporary folder
  under `.verification/runtime-tmp`; no user data was deleted.
- Existing Python virtualenv references another machine's missing Python 3.12.
  Global Python 3.13 lacks backend dependencies. Backend/media tests not executed.
- No Git metadata in workspace: remote, branch, commit and user diffs unavailable.
- No server, DNS, certificate, external database, provider download or backup restore
  has been tested or provisioned this session.

## Remaining launch gates

Owner must create Oracle account and verify free A1 availability/zero-cost estimate,
identify the authoritative GitHub repository, and choose an encrypted off-host
backup destination. Verify native container build, actual PostgreSQL/Redis, all
media codecs, authorized provider downloads, upload processing, cancel/expiry,
restart semantics, disk/memory limits, private-port/SSRF/proxy trust boundaries,
certificate renewal and backup restoration on the actual VM before traffic.

No paid fallback is authorized. No account credentials should be sent in chat.
