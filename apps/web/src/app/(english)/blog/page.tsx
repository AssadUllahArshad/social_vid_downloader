import { pageMetadata } from "@/lib/publication";
import Link from "next/link";
export const metadata = pageMetadata("/blog/");
export default function Page() {
  return (
    <main className="container content-page">
      <h1>Resources</h1>
      <p>
        Find practical help for source formats, audio choices, playback and authorized video backups in our <Link href="/guides/">published guides</Link>.
      </p>
      <h2>Find the right guide</h2>
      <p>
        <Link href="/topics/">Browse topics</Link> to compare formats, diagnose playback problems or plan a creator workflow. Choose the guide that matches your actual source and receiving device.
      </p>
      <h2>Platform help</h2>
      <p><Link href="/youtube/">YouTube</Link>, <Link href="/facebook/">Facebook</Link>, <Link href="/instagram/">Instagram</Link>, <Link href="/tiktok/">TikTok</Link> and <Link href="/snapchat-downloader/">Snapchat Spotlight</Link> hubs explain the available tools and their limits.</p>
    </main>
  );
}
