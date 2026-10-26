import Link from "next/link";
import { pageMetadata } from "@/lib/publication";
import { operator } from "@/lib/operator";
export const metadata = pageMetadata("/contact/");
export default function Page() {
  return (
    <main className="container content-page">
      <h1>Contact</h1>
      <p>
        SocialVidDownloader is operated by {operator.name}. For help, email <a href={`mailto:${operator.support}`}>{operator.support}</a>.
      </p>
      <h2>Getting help</h2>
      <p>
        Include the tool you used, your browser, and the message you saw. Share a public source link only if you are comfortable including it in email. Do not send account passwords, verification codes, session cookies, or temporary download tokens.
      </p>
      <h2>Copyright reports</h2>
      <p>Email <a href={`mailto:${operator.copyright}`}>{operator.copyright}</a> with the affected source link and an explanation of your rights. See our <Link href="/copyright/">copyright and takedown policy</Link>.</p>
    </main>
  );
}
