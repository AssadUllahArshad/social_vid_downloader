import { processingTools } from "@/lib/processing-tools";
import Link from "next/link";
import type { ReactNode } from "react";
import { notFound } from "next/navigation";
import { getArticle, pageMetadata, publishedArticles } from "@/lib/publication";
import { site } from "@/lib/content";
import { JsonLd } from "@/components/json-ld";
type Props = { params: Promise<{ platform: string; slug: string }> };
function renderParagraphLinks(paragraph: string): ReactNode {
  const parts: ReactNode[] = [];
  let cursor = 0;
  // Only canonical, currently approved guide paths can become links. Everything
  // else remains escaped React text, including HTML and external URL markup.
  const pattern = /\[([^\[\]\r\n]+)\]\((\/guides\/(?:general|youtube|facebook|instagram|tiktok|snapchat|whatsapp)\/[a-z0-9]+(?:-[a-z0-9]+)*\/)\)/g;
  for (const match of paragraph.matchAll(pattern)) {
    const [markup, label, path] = match;
    if (!getArticle(path)) continue;
    parts.push(paragraph.slice(cursor, match.index));
    parts.push(<Link key={match.index} href={path}>{label}</Link>);
    cursor = match.index + markup.length;
  }
  if (!cursor) return paragraph;
  parts.push(paragraph.slice(cursor));
  return parts;
}
export function generateStaticParams() {
  return publishedArticles.map(page => { const [, , platform, slug] = page.path.split("/"); return { platform, slug }; });
}
export async function generateMetadata({ params }: Props) {
  const { platform, slug } = await params;
  const path = `/guides/${platform}/${slug}/`;
  if (!getArticle(path)) notFound();
  return pageMetadata(path);
}
export default async function Guide({ params }: Props) {
  const { platform, slug } = await params;
  const page = getArticle(`/guides/${platform}/${slug}/`);
  if (!page) notFound();
  const related = page.related.map(getArticle).filter(other => other !== undefined);
  return <main className="container content-page">
    <nav className="breadcrumb" aria-label="Breadcrumb"><Link href="/">Home</Link> / <Link href="/guides/">Guides</Link> / <Link href={`/guides/${platform}/`}>{platform === "general" ? "Video help" : platform}</Link> / {page.h1}</nav>
    <h1>{page.h1}</h1><p>{page.intro}</p><p><Link href={`/topics/${page.family}/`}>More help on this subject</Link></p>
    <p>{page.targetDownloader ? <><Link href={page.targetDownloader}>Open the relevant downloader</Link> · <Link href={page.hub}>Platform tools and access limits</Link></> : <Link href={page.hub}>More media and privacy guidance</Link>}</p>
    {page.processingLinks?.length && <p>{page.processingLinks.map(path=><Link key={path} href={path}>{processingTools.find(tool=>`/${tool.slug}/`===path)?.name || "Video tool"}</Link>)}</p>}
    {page.sections.map(section => <section key={section.heading}><h2>{section.heading}</h2>{section.paragraphs.map(paragraph => <p key={paragraph}>{renderParagraphLinks(paragraph)}</p>)}{section.steps && <ol>{section.steps.map(step => <li key={step}>{step}</li>)}</ol>}</section>)}
    <section><h2>Worked example</h2><p>{page.example}</p></section>
    {page.faq.length > 0 && <section><h2>Questions about this problem</h2>{page.faq.map(faq => <details key={faq.question}><summary>{faq.question}</summary><p>{faq.answer}</p></details>)}</section>}
    <section><h2>Related guidance</h2><ul>{related.map(other => <li key={other.path}><Link href={other.path}>{other.title}</Link></li>)}</ul></section>
    <section><h2>Sources and verification</h2><ul>{page.sources.map(source => <li key={source.url}><a href={source.url} rel="noreferrer">{source.title}</a></li>)}</ul><p>Reviewed {page.lastUpdated}. {page.contentRole === "education" ? "Follow the official app controls and the owner’s permission. This guidance does not provide a WhatsApp URL downloader or private-content access." : "Product behavior is limited to available source formats and provider access; it is not a promise that every public link works."}</p></section>
    <JsonLd data={{ "@context": "https://schema.org", "@type": "Article", headline: page.h1, description: page.description, mainEntityOfPage: `${site}${page.path}`, dateModified: page.lastUpdated }} />
    <JsonLd data={{ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: `${site}/` }, { "@type": "ListItem", position: 2, name: "Guides", item: `${site}/guides/` },
      { "@type": "ListItem", position: 3, name: platform, item: `${site}/guides/${platform}/` }, { "@type": "ListItem", position: 4, name: page.h1, item: `${site}${page.path}` },
    ] }} />
  </main>;
}
