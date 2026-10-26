import { pageMetadata } from "@/lib/publication";
import { operator } from "@/lib/operator";
export const metadata = pageMetadata("/copyright/");
export default function Page() {
  return (
    <main className="container content-page">
      <h1>Copyright and takedown policy</h1>
      <p>
        Download only content you own or have permission to save. Respect
        creator permissions, platform terms, and applicable copyright rules.
      </p>
      <h2>Report a concern</h2>
      <p>
        The service does not host a permanent library of downloaded videos. A
        copyright concern can be reported to <a href={`mailto:${operator.copyright}`}>{operator.copyright}</a>. Include the affected source link, a description of the work and your rights, your contact details, and the action you are requesting. Do not attach account credentials or private download tokens.
      </p>
      <h2>How reports are handled</h2>
      <p>{operator.name} reviews reports and may restrict processing of an affected source when appropriate. Reports are not a guarantee that a third-party platform will remove its original upload. Contact the source platform separately when you need action on content it hosts.</p>
      <h2>Permission and access limits</h2>
      <p>A public link is not a license to copy or redistribute its content. Use the service only where you have the necessary permission. The service does not bypass private-account access, paywalls, or content protections. This reporting channel does not claim registration as a statutory DMCA agent or replace formal notices required by applicable law.</p>
    </main>
  );
}
