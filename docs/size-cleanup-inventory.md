# Cleanup inventory — before deletion, 15 October 2026

Measured project: 3.677 GB allocated; user baseline 3.68 GB.

No Git metadata exists. Protected-file SHA-256 snapshot saved before cleanup; no active app/build/media jobs found. No dependencies, user media, secrets, published records or SEO checkpoints will be deleted.

| Path | Class | Decision |
|---|---|---|
| `.ruff_cache` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/api/.pytest_cache` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/api/.ruff_cache` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/api/app/__pycache__` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/api/app/processing/__pycache__` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/api/app/providers/__pycache__` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/api/tests/__pycache__` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/web/.next-dev` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/web/.next/cache` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/web/test-results` | UNUSED TEST ARTIFACT | remove: No active app/build/test processes; regeneratable cache or output. |
| `apps/web/tsconfig.tsbuildinfo` | REGENERATABLE | remove: No active app/build/test processes; regeneratable cache or output. |
| `node_modules` | ESSENTIAL | preserve: Active installed dependency environment; no reinstall needed. |
| `apps/api/.venv` | ESSENTIAL | preserve: Current backend dependency environment. |
| `apps/api/.venv-phase1` | UNCERTAIN | preserve: Older environment; keep without verified reproducibility/use history. |
| `apps/web/.next` | REGENERATABLE | preserve: Retain runtime build until the single requested rebuild; remove only cache now. |
| `content` | ESSENTIAL | preserve: All published/draft records, approvals and translation records. |
| `docs` | ESSENTIAL | preserve: SEO history, checkpoints and retained verification evidence; no duplicate deletion. |
| `apps/android-status-saver` | UNCERTAIN | preserve: Frozen unfinished source; preserve locally, exclude from releases. |
| `releases` | ESSENTIAL | preserve: Current validated deployment archive and receipt; no old redundant archive found. |
| `.verification` | UNCERTAIN | preserve: Saved verification metadata; preserve. |
| `**/.env*` | USER FILE | preserve: Never inspect values, delete or modify credentials. |
| `apps/web/public` | ESSENTIAL | preserve: Required frontend assets. |

Media, recursive largest-file/directory inventory and duplicate hash groups: `size-cleanup-inventory.json`.
Source MOV and small optional test fixtures are retained. No original media will be deleted. Duplicate SEO inventories and installed dependency copies remain protected.
The one requested production build may refresh generated Next type references; restore only verified generated changes to preserve source byte-for-byte.
