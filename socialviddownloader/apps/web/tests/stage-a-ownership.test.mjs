import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const script = fileURLToPath(new URL('../../../scripts/consolidate-stage-a-intents.py', import.meta.url));
const batch = 'expansion-stage-a-2026-10-08';
const ownerPath = '/guides/general/account-video-bookmark-vs-retained-file/';
function row(path, status, destination = path) {
  return { path, batch, status, indexable: false, inventoryApproval: null,
    semanticReview: { state: status === 'ARCHIVED' ? 'MERGED_DRAFT_TASK' : 'GAP_IDENTIFIED_RESEARCH_PENDING', rationale: 'Fixture task ownership', comparisons: [destination] },
    disposition: { classification: status === 'ARCHIVED' ? 'MERGE_WITH_EXISTING' : 'NEEDS_RESEARCH', destination, internalLinkDestination: destination, outcome: 'RESEARCH_REQUIRED', reason: 'Fixture task ownership' }, related: [] };
}
function fixture(rows, articles, run) {
  const folder = mkdtempSync(join(tmpdir(), 'svd-stage-a-ownership-'));
  const editorial = join(folder, 'content/editorial');
  mkdirSync(editorial, { recursive: true });
  const registry = join(editorial, 'first-500-inventory.json');
  writeFileSync(registry, JSON.stringify(rows));
  writeFileSync(join(editorial, 'articles.json'), JSON.stringify(articles));
  const execute = () => spawnSync('python3', [script], { cwd: folder, encoding: 'utf8' });
  try { run({ execute, registry }); } finally { rmSync(folder, { recursive: true, force: true }); }
}

test('a merged alias follows its newly published owner without becoming public', () => {
  const alias = row('/guides/tiktok/tiktok-favorites-vs-downloads/', 'ARCHIVED', ownerPath);
  fixture([alias, row(ownerPath, 'PUBLISHED')], [{ path: ownerPath, status: 'PUBLISHED', indexable: true }], ({ execute, registry }) => {
    const result = execute();
    assert.equal(result.status, 0, result.stderr);
    const [saved] = JSON.parse(readFileSync(registry, 'utf8'));
    assert.equal(saved.semanticReview.state, 'MERGED_EXISTING_TASK');
    assert.equal(saved.disposition.outcome, 'CONSOLIDATED');
    assert.equal(saved.status, 'ARCHIVED');
    assert.equal(saved.indexable, false);
    assert.equal(saved.inventoryApproval, null);
    const first = readFileSync(registry, 'utf8');
    assert.equal(execute().status, 0);
    assert.equal(readFileSync(registry, 'utf8'), first);
  });
});

test('a draft ownership chain resolves to one active owner and stays unresolved', () => {
  const middle = '/guides/general/bookmark-alias/';
  fixture([row('/guides/general/older-alias/', 'ARCHIVED', middle), row(middle, 'ARCHIVED', ownerPath), row(ownerPath, 'DRAFT')], [], ({ execute, registry }) => {
    const result = execute();
    assert.equal(result.status, 0, result.stderr);
    const saved = JSON.parse(readFileSync(registry, 'utf8'));
    for (const alias of saved.slice(0, 2)) {
      assert.equal(alias.disposition.destination, ownerPath);
      assert.equal(alias.disposition.internalLinkDestination, ownerPath);
      assert.equal(alias.disposition.outcome, 'RESEARCH_REQUIRED');
      assert.equal(alias.indexable, false);
    }
  });
});

test('cyclic answer ownership fails before modifying the registry', () => {
  const a = '/guides/general/cycle-a/', b = '/guides/general/cycle-b/';
  fixture([row(a, 'ARCHIVED', b), row(b, 'ARCHIVED', a)], [], ({ execute, registry }) => {
    const before = readFileSync(registry, 'utf8');
    const result = execute();
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Cyclic task ownership/);
    assert.equal(readFileSync(registry, 'utf8'), before);
  });
});
