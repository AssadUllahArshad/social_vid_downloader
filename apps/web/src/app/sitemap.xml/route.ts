import { chunks, sitemapIndex, urlset } from "@/lib/editorial/sitemap";
export const dynamic = "force-static";
export function GET() {
  const groups = chunks();
  return new Response(groups.length > 1 ? sitemapIndex(groups.length) : urlset(groups[0] || []), { headers: { "Content-Type": "application/xml; charset=utf-8" } });
}
