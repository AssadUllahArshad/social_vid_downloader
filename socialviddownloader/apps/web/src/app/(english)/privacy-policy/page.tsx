import { pageMetadata } from "@/lib/publication";
import { operator } from "@/lib/operator";
export const metadata = pageMetadata("/privacy-policy/");
export default function Page() {
  return (
    <main className="container content-page">
      <h1>Privacy policy</h1>
      <p>
        {operator.name} operates SocialVidDownloader. The service uses submitted public links to prepare authorized downloads. It does not offer user accounts, permanent download history, or advertising profiles. Analytics and AI dubbing are not enabled in this release.
      </p>
      <h2>Submitted links</h2>
      <p>
        Submitted links are checked and temporarily cached to process the
        download. Analysis sessions and download links expire after 10 minutes.
        Temporary files are removed periodically after they expire. We do not request social account
        passwords, verification codes, or session cookies. Operational logs should contain error
        categories and processing times rather than full submitted links.
        Source platforms and their delivery networks receive requests from the service to retrieve the selected public media. Their own privacy policies apply to those requests.
      </p>
      <h2>Abuse prevention and operational information</h2>
      <p>The API uses a keyed hash of the requesting IP address for short-lived rate-limit counters. It does not put submitted links, passwords, or download tokens in application logs. Hosting and network providers may process connection information to deliver and protect the service. Provider-health observations contain processing outcomes, not a personal viewing history.</p>
      <h2>Temporary files and browser storage</h2>
      <p>Metadata caches are short-lived. Prepared files remain available only during their download window, then scheduled cleanup removes stale media. Closing a browser does not immediately erase a server-side temporary file. A file you save to your own device remains there until you remove it; the service cannot delete your local copy.</p>
      <h2>Support and privacy requests</h2>
      <p>Email <a href={`mailto:${operator.support}`}>{operator.support}</a> with privacy questions. Information you choose to send in email is handled to respond to your request; avoid attaching private media or account credentials. No social account password or browser-cookie upload is required or accepted by the downloader.</p>
    </main>
  );
}
