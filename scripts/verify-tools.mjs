// Exercise the actual desktop/mobile UI with operation-specific inputs and settings.
// The former one-file/all-defaults loop did not test images, subtitles, merging,
// ZIP or JSON outputs correctly, exhausted retained storage, and exited 0 on failure.
import { execFileSync, spawnSync } from 'node:child_process';
import { mkdtempSync, rmSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { toolResults } from './processing-verification-results.mjs';

const origin = process.env.AUDIT_ORIGIN;
const source = process.env.PROCESSING_REAL_INPUT || process.env.PROCESSING_TRAILER_INPUT;
if (!origin || !source) throw new Error('Set AUDIT_ORIGIN to the running standalone server and PROCESSING_REAL_INPUT or PROCESSING_TRAILER_INPUT to authorized media.');
if (!['127.0.0.1', 'localhost'].includes(new URL(origin).hostname)) throw new Error('Verification requires an isolated loopback server.');
const folder = mkdtempSync(join(tmpdir(), 'svd-tool-verification-'));
const root = fileURLToPath(new URL('../', import.meta.url));
const tools = JSON.parse(readFileSync(new URL('../content/processing/tools.json', import.meta.url)));
try {
  // Bound the multi-operation fixture. Full-length tests are separately covered
  // by processing-realistic.spec.ts; a two-minute GIF is not a typical GIF task.
  const input = process.env.PROCESSING_REAL_INPUT || join(folder, 'scene.mp4');
  if (!process.env.PROCESSING_REAL_INPUT) execFileSync('ffmpeg', ['-v', 'error', '-y', '-i', source, '-t', '8', '-map', '0:v:0', '-map', '0:a:0', '-c', 'copy', input]);
  const report = join(root, 'docs', 'processing-browser-results.json');
  const run = spawnSync('npx', ['playwright', 'test', 'e2e/processing-real.spec.ts', '--workers=1', '--reporter=line,json'], {
    cwd: join(root, 'apps/web'), stdio: 'inherit', env: {...process.env,
      PLAYWRIGHT_BASE_URL: origin, PLAYWRIGHT_EXTERNAL_SERVER: '1', PROCESSING_REAL_E2E: '1',
      PROCESSING_REAL_INPUT: input, PLAYWRIGHT_JSON_OUTPUT_NAME: report}
  });
  const results = toolResults(tools, JSON.parse(readFileSync(report, 'utf8')));
  writeFileSync(new URL('../docs/video-tools-execution-state-run.json', import.meta.url), JSON.stringify({origin, verifiedAt: new Date().toISOString(), results}, null, 2) + '\n');
  process.exitCode = run.status === 0 && results.every(row => row.status === 'VERIFIED') ? 0 : 1;
} finally { rmSync(folder, {recursive: true, force: true}); }
