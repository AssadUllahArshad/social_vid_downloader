import Link from "next/link";
import { ProviderStatus } from "@/components/provider-status";
export const metadata = {
  title: "Administration",
  robots: { index: false, follow: false },
};
export default function Admin() {
  return (
    <main className="container content-page">
      <h1>Administration</h1>
      <p>
        A versioned editorial workflow manages article publication. The content inventory is read-only; no browser content-editing endpoints are exposed.
      </p>
      <p><Link href="/admin/content/">Open the editorial inventory</Link></p>
      <ProviderStatus />
      <div className="notice">
        Browser-based content editing and authentication are not enabled. Publication changes require the reviewed repository workflow.
      </div>
    </main>
  );
}
