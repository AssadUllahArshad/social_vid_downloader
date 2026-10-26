import Link from "next/link";
import { pageMetadata, publishedArticles } from "@/lib/publication";
import { familyLabels } from "@/lib/editorial/collections.mjs";
export const metadata = pageMetadata("/topics/");
export default function Topics() {
  return <main className="container content-page"><nav className="breadcrumb" aria-label="Breadcrumb"><Link href="/">Home</Link> / <Link href="/guides/">Guides</Link> / Subjects</nav><h1>Browse video help by subject</h1><p>Find reviewed help for the task you are trying to complete. Source links, playback, captions, formats and storage require different checks.</p><ul>{[...new Set(publishedArticles.map(page => page.family))].map(family => <li key={family}><Link href={`/topics/${family}/`}>{familyLabels[family] || family}</Link></li>)}</ul></main>;
}
