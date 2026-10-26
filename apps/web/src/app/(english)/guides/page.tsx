import Link from "next/link";
import { pageMetadata, publishedArticles } from "@/lib/publication";
export const metadata = pageMetadata("/guides/");
export default function Guides() {
  const platforms = [...new Set(publishedArticles.map(page => page.platform))];
  return <main className="container content-page"><nav className="breadcrumb" aria-label="Breadcrumb"><Link href="/">Home</Link> / Guides</nav><h1>Guides</h1><p>Find practical answers about public video links, actual file formats, browser saving, and source audio. Start with the problem you are trying to solve; these guides do not bypass source permissions or promise unavailable qualities.</p>{platforms.length ? <ul>{platforms.map(platform => <li key={platform}><Link href={`/guides/${platform}/`}>{platform === "general" ? "General video and file help" : `${platform} guides`}</Link></li>)}</ul> : <p>No reviewed guides are published yet.</p>}<p><Link href="/topics/">Browse by subject</Link> for troubleshooting, formats, storage, audio and captions.</p><p><Link href="/">Choose a downloader</Link> to inspect formats for an authorized public link.</p></main>;
}
