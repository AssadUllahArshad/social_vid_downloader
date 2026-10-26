// Deployment smoke only: compare sitemap shards with the frozen release inventory.
// This does not replace the existing full HTTP page audit.
import {readFileSync} from 'node:fs';
const origin = new URL(process.argv[2] || 'https://socialviddownloader.com');
if (!['http:', 'https:'].includes(origin.protocol)) throw Error('HTTP/HTTPS required');
const release = JSON.parse(readFileSync(new URL('../docs/launch-freeze.json', import.meta.url),'utf8'));
const canonical = 'https://socialviddownloader.com';
async function xml(path) {
  const res = await fetch(new URL(path, origin), {redirect:'manual',signal:AbortSignal.timeout(15000)});
  if (res.status !== 200 || !/xml/i.test(res.headers.get('content-type') || '')) throw Error(`Invalid sitemap response: ${path} HTTP ${res.status}`);
  return res.text();
}
const locs = text => [...text.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match=>match[1]);
const root = await xml('/sitemap.xml');
let urls;
if (root.includes('<sitemapindex')) {
  urls = [];
  for (const shard of locs(root)) {
    const target = new URL(shard);
    if (target.origin !== canonical || !target.pathname.startsWith('/sitemaps/') || target.search || target.hash) throw Error('Unexpected sitemap shard');
    urls.push(...locs(await xml(target.pathname)));
  }
} else if (root.includes('<urlset')) urls=locs(root);
else throw Error('Invalid sitemap XML');
const expected = new Set(release.indexablePaths.map(path=>canonical+path));
const actual = new Set(urls);
const missing = [...expected].filter(url=>!actual.has(url));
const extra = urls.filter(url=>!expected.has(url));
const duplicates = urls.length-actual.size;
console.log(JSON.stringify({expected:expected.size,actual:urls.length,duplicates,missing,extra},null,2));
if(missing.length || extra.length || duplicates) process.exitCode=1;
