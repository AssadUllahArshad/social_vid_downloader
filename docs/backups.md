# Production backups

PostgreSQL holds the seeded relational inventory; published web content and approvals currently come from the versioned `content/` files. Back up both. The database records are not an alternative public CMS renderer.

Use daily encrypted PostgreSQL custom-format backups (`pg_dump --format=custom`) from a private administration host, with a separate least-privilege backup credential. Retain 7 daily and 4 weekly copies off-host. Monitor failed jobs and rehearse `pg_restore` into an isolated database before launch and quarterly thereafter. Verify schema, row counts, and a representative read before declaring restoration successful. A backup that has never been restored is unverified.

Archive each deployed release, lockfiles, migrations, and the complete `content/` directory including approval digests, draft records, merge decisions and the launch freeze. Store production environment configuration in an encrypted secret manager with restricted access and an offline recovery method. Never place secrets in a source-code or public artifact backup.

Do not back up temporary downloaded media. Redis contains ephemeral sessions, counters, jobs, and provider observations; application readiness requires it, but it is not a permanent media archive. Restoring old Redis state can revive unusable links, so use a fresh instance during disaster recovery. Old links should expire clearly.

Recovery order: secrets and private networking → PostgreSQL restore → matching application/migration version → clean Redis → private health checks → public smoke test. Keep the old deployment isolated until the recovered release is verified.
