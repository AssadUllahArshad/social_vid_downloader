import { pageMetadata } from "@/lib/publication";
import Link from "next/link";
import { operator } from "@/lib/operator";
export const metadata = pageMetadata("/about/");
export default function Page() {
  return (
    <main className="container content-page">
      <div className="breadcrumb"><Link href="/">Home</Link> / About</div>
      <h1>About SocialVidDownloader</h1>
      <p>
        SocialVidDownloader is operated by {operator.name} and helps people save authorized social video
        content. The shared downloader processes public links from YouTube,
        Facebook, and Instagram, plus TikTok and Snapchat Spotlight in beta, when
        the source permits access.
      </p>
      <h2>What a download contains</h2>
      <p>Video quality and audio choices come from the submitted source. When separate streams are required, the service combines them and checks the resulting file before offering it. Multiple audio languages are available only when the source supplies compatible tracks; we do not translate or dub videos.</p>
      <h2>Choose a supported platform</h2>
      <p>Start with <Link href="/youtube/">YouTube videos and Shorts</Link>, <Link href="/facebook/">Facebook videos and Reels</Link>, or <Link href="/instagram/">Instagram videos and Reels</Link>. <Link href="/tiktok/">TikTok</Link> and <Link href="/snapchat-downloader/">Snapchat Spotlight</Link> are beta integrations. Instagram Stories, Snapchat Stories and WhatsApp Status downloading are unsupported.</p>
      <h2>Your responsibility</h2>
      <p>A public link does not grant a license to reuse its content. Check the owner’s permission and the source platform’s rules. Download links and analysis sessions expire; this service is not a permanent media library. SocialVidDownloader is independent of the supported platforms.</p>
      <h2>How we work</h2>
      <p>
        The workflow validates a public media link, inspects available
        formats, and offers only the files the source actually provides. We do
        not bypass DRM, platform authentication, or private account permissions.
      </p>
    </main>
  );
}
