import { chunks, urlset } from "@/lib/editorial/sitemap";
export const dynamic = "force-static";
export function generateStaticParams() { return chunks().map((_, index) => ({ shard: `${index}.xml` })); }
export async function GET(_request: Request, { params }: { params: Promise<{ shard: string }> }) {
  const { shard } = await params;
  if (!/^(0|[1-9]\d*)\.xml$/.test(shard)) return new Response("Not found", { status: 404 });
  const group = chunks()[Number(shard.slice(0, -4))];
  return group ? new Response(urlset(group), { headers: { "Content-Type": "application/xml; charset=utf-8" } }) : new Response("Not found", { status: 404 });
}
