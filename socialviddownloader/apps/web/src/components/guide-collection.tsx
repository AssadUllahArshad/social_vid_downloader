import Link from "next/link";
import { notFound } from "next/navigation";
import { publishedArticles, pageMetadata } from "@/lib/publication";
import { PAGE_SIZE, familyLabels, platformLabels } from "@/lib/editorial/collections.mjs";

type Kind = "platform" | "family";
export function collectionPaths(kind: Kind) {
  const groups = new Map<string, number>();
  for (const article of publishedArticles) {
    const key = kind === "platform" ? article.platform : article.family;
    groups.set(key, (groups.get(key) || 0) + 1);
  }
  return [...groups].flatMap(([key, count]) => Array.from({ length: Math.ceil(count / PAGE_SIZE) }, (_, i) => ({ key, number: String(i + 1) })));
}
export function collectionMetadata(kind: Kind, group: string, number = "1", paged = false) {
  if (!collectionPaths(kind).some(row => row.key === group && row.number === number) || (paged && number === "1")) notFound();
  return pageMetadata(`/${kind === "platform" ? "guides" : "topics"}/${group}/${number === "1" ? "" : `page/${number}/`}`);
}
export function GuideCollection({ kind, group, number = 1 }: { kind: Kind; group: string; number?: number }) {
  const all = publishedArticles.filter(page => (kind === "platform" ? page.platform : page.family) === group).sort((a, b) => a.title.localeCompare(b.title));
  const count = Math.ceil(all.length / PAGE_SIZE);
  if (!Number.isInteger(number) || number < 1 || number > count) notFound();
  const pages = all.slice((number - 1) * PAGE_SIZE, number * PAGE_SIZE);
  const root = `/${kind === "platform" ? "guides" : "topics"}/${group}/`;
  const label = kind === "platform" ? platformLabels[group] : familyLabels[group] || group;
  return <main className="container content-page">
    <nav className="breadcrumb" aria-label="Breadcrumb"><Link href="/">Home</Link> / <Link href="/guides/">Guides</Link> / <Link href="/topics/">Subjects</Link> / {label}</nav>
    <h1>{label} guidance{number > 1 ? ` — page ${number}` : ""}</h1>
    <p>Choose a reviewed answer for your problem. These guides explain available workflows and limitations; they do not grant access to restricted source content.</p>
    <p>Showing {(number - 1) * PAGE_SIZE + 1}–{Math.min(number * PAGE_SIZE, all.length)} of {all.length} guides.</p>
    {kind === "platform" && <nav aria-label="Guide subjects"><ul>{[...new Set(all.map(page => page.family))].map(family => <li key={family}><Link href={`/topics/${family}/`}>{familyLabels[family] || family}</Link></li>)}</ul></nav>}
    <ul>{pages.map(page => <li key={page.path}><Link href={page.path}>{page.title}</Link><p>{page.description}</p></li>)}</ul>
    <nav aria-label="Guide pages"><p>{number > 1 && <Link href={number === 2 ? root : `${root}page/${number - 1}/`}>Previous page</Link>} {number < count && <Link href={`${root}page/${number + 1}/`}>Next page</Link>}</p><p>Page {number} of {count}</p></nav>
  </main>;
}
