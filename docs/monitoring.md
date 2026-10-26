# Monitoring and analytics

Monitor private API `/health` every 30–60 seconds for liveness and `/ready` for Redis, FFmpeg and the migrated PostgreSQL table. A failed readiness probe should remove the instance from new work without publishing internal diagnostics. Alert on sustained failures, available temporary disk, job saturation, repeated 5xx/429, backup failures and certificate expiry. Test alert delivery with the operator before launch.

Internal `/internal/provider-status` requires the server-side random bearer token; leave disabled if no protected operator tooling is used. It exposes sanitized stage observations, not raw logs or source URLs. Keep it private/VPN-protected. The production browser admin inventory is disabled; repository publication remains the reviewed workflow.

Application logs contain event, status, provider and processing duration/error category without submitted URLs, cookies or access tokens. API container access logs are disabled. Configure host/edge log retention, rotate logs and avoid recording token-bearing paths. Structured observations are not proof of worldwide provider uptime.

`SENTRY_DSN`, `NEXT_PUBLIC_GA_ID` and `NEXT_PUBLIC_CLARITY_ID` are reserved configuration, not active integrations. Tracking remains disabled for launch. Do not enable external scripts merely by setting these values. A future integration needs explicit implementation, CSP changes, a privacy/consent decision for the actual audience and verification that media URLs/tokens are not sent as telemetry. Search Console requires no analytics script.

Current live evidence is in `launch-live-provider-results.json`. Re-test from the actual production egress network before public launch. Keep TikTok/Spotlight Beta even when individual samples pass. YouTube public samples currently require account access from this environment; report this as degradation, not universal private-content support or permission to bypass authentication.

## Video-processing release

The shared upload workflow supports 22 verified operations, with translated controls in all 13 languages. Deploy the current release and matching content together. Configure the bounded Nginx processing location, private MEDIA_ROOT and PROCESSING_ENABLED. Check runtime capabilities, a small upload, an actual downloadable output, cancellation and expiry after deployment. No separate worker service or durable queue is required. Monitor storage, rejected uploads, timeouts and rate limits; retain no user media backups. Rollback disables processing with PROCESSING_ENABLED=0 while restoring a matching application/content release; do not destructively roll back database data. Deferred guide records are nonpublic and must not be indexed without review.
