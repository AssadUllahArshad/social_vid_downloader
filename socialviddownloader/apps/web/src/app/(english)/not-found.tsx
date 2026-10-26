import Link from "next/link";
export default function NotFound() {
  return (
    <main className="container content-page">
      <h1>That page isn’t here.</h1>
      <p>Find a downloader or return to the home page.</p>
      <Link href="/">Back to SocialVidDownloader</Link>
      <p><Link href="/#tools">Browse downloaders</Link> · <Link href="/guides/">Read the guides</Link></p>
    </main>
  );
}
