import { localizedPages } from "@/lib/localized-publication";
import { site } from "@/lib/content";
import { publicPages } from "@/lib/publication";
import { sitemapChunks } from "./workflow.mjs";
export const chunks = () => sitemapChunks([...publicPages, ...localizedPages()], 1000);
const escapeXml = (value: string) => value.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
export function urlset(pages: { path: string }[]) {
  return `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${pages.map(page => `<url><loc>${escapeXml(`${site}${page.path}`)}</loc></url>`).join("")}</urlset>`;
}
export function sitemapIndex(count: number) {
  return `<?xml version="1.0" encoding="UTF-8"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${Array.from({ length: count }, (_, i) => `<sitemap><loc>${escapeXml(`${site}/sitemaps/${i}.xml`)}</loc></sitemap>`).join("")}</sitemapindex>`;
}
