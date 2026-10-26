# Rollback

Retain the previous release/image identifiers and its complete content files. Take and verify a database backup before migrations. Do not run a destructive reset or replace existing content with initial seed records.

If the new release fails, stop admitting new download jobs at ingress, let bounded jobs finish where possible, and switch web/API traffic to the previous compatible images. Restore that release's content files together so publication approvals, URLs and sitemap stay consistent. Keep temporary media private; expiry should handle stale links.

Do not automatically run Alembic downgrade on a populated production database. First establish whether the previous release can use the migrated schema. If a database restore is necessary, restore the pre-deployment backup into a separate database, verify it, then change the private connection configuration. This can lose writes after the backup; record the loss window and get operator authorization before discarding data.

Restart with fresh Redis after a full disaster restore rather than restoring expired jobs. Verify `/health`, `/ready`, homepage, one supported downloader, a guide, admin isolation, robots and sitemap. Re-run the full HTTP publication audit. Reopen traffic only after those checks pass. Record incident cause and the exact restored versions.

## Video-processing release

The shared upload workflow supports 22 verified operations, with translated controls in all 13 languages. Deploy the current release and matching content together. Configure the bounded Nginx processing location, private MEDIA_ROOT and PROCESSING_ENABLED. Check runtime capabilities, a small upload, an actual downloadable output, cancellation and expiry after deployment. No separate worker service or durable queue is required. Monitor storage, rejected uploads, timeouts and rate limits; retain no user media backups. Rollback disables processing with PROCESSING_ENABLED=0 while restoring a matching application/content release; do not destructively roll back database data. Deferred guide records are nonpublic and must not be indexed without review.
