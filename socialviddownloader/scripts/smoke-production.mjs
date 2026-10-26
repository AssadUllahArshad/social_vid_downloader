import { readFileSync } from 'node:fs';
const site = new URL(process.argv[2] || 'https://socialviddownloader.com');
const api = new URL(process.env.SMOKE_API_ORIGIN || 'http://127.0.0.1:8000');
if (!['https:', 'http:'].includes(site.protocol) || !['https:', 'http:'].includes(api.protocol)) throw new Error('Use HTTP/HTTPS origins');
const article = JSON.parse(readFileSync(new URL('../content/editorial/articles.json', import.meta.url), 'utf8')).find(row => row.status === 'PUBLISHED' && row.indexable);
if (!article) throw new Error('No published indexable article');
let failures = 0;
const paths = ['/', '/robots.txt', '/sitemap.xml', article.path, '/youtube-video-downloader/', '/youtube-shorts-downloader/', '/facebook-video-downloader/', '/facebook-reels-downloader/', '/instagram-video-downloader/', '/instagram-reels-downloader/', '/tiktok-video-downloader/', '/snapchat-spotlight-downloader/'];
for (const [origin, path] of [...paths.map(path => [site, path]), ...['/health', '/ready'].map(path => [api, path])]) {
  try {
    const response = await fetch(new URL(path, origin), { redirect: 'manual', signal: AbortSignal.timeout(15000) });
    const body = await response.text();
    let pass = response.status === 200;
    if (path === '/robots.txt') pass &&= body.includes('https://socialviddownloader.com/sitemap.xml');
    if (path === '/sitemap.xml') pass &&= /<sitemapindex|<urlset/.test(body) && !/localhost|127\.0\.0\.1/.test(body);
    if (path === article.path) pass &&= body.includes('index, follow') && body.includes(`https://socialviddownloader.com${path}`);
    console.log(`${pass ? 'PASS' : 'FAIL'} ${origin.origin}${path} HTTP ${response.status}`);
    if (!pass) failures++;
  } catch { failures++; console.log(`FAIL ${origin.origin}${path} transport_or_timeout`); }
}
process.exitCode = failures ? 1 : 0;
