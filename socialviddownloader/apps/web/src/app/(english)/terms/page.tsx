import Link from "next/link";
import { pageMetadata } from "@/lib/publication";
export const metadata = pageMetadata("/terms/");
export default function Page() {
  return (
    <main className="container content-page">
      <h1>Terms of use</h1>
      <p>
        Use SocialVidDownloader only for content you own or have permission to
        save. Access to a video does not automatically grant permission to
        download, copy, or redistribute it.
      </p>
      <h2>Your responsibilities</h2>
      <p>Check that your intended saving, editing, sharing, or reuse is permitted. Do not submit private account credentials, attempt to access another person&apos;s private media, evade service limits, or use the service to harm others. You remain responsible for files you save and how you use them.</p>
      <h2>Files and temporary access</h2>
      <p>Only formats actually supplied by the source are offered. Available quality, audio languages, and file properties can differ between videos. Prepared download links expire, and temporary files are cleaned up. Keep your own authorized backup; this service is not permanent media storage.</p>
      <h2>Beta and unsupported tools</h2>
      <p>TikTok and Snapchat Spotlight are Beta and may fail for some public links. Snapchat Story downloading and public-link WhatsApp Status downloading are unsupported. Source audio selection does not generate a translation or an AI dub.</p>
      <h2>Questions and reports</h2>
      <p>Use our <Link href="/contact/">contact page</Link> for support and our <Link href="/copyright/">copyright policy</Link> to report a rights concern. Our <Link href="/privacy-policy/">privacy policy</Link> explains request processing and temporary storage.</p>
      <h2>Service availability</h2>
      <p>
        Platform integrations can change or become unavailable. Downloads depend
        on the source video and current platform restrictions. Do not use the service to
        circumvent authentication, copyright protections, or access
        restrictions.
      </p>
    </main>
  );
}
