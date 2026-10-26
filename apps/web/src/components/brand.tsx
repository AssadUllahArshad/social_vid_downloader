import { Download } from "lucide-react";
import Link from "next/link";
export function Brand({ href = "/", homeLabel = "home" }: { href?: string; homeLabel?: string }) {
  return (
    <Link href={href} className="brand" aria-label={`SocialVidDownloader ${homeLabel}`}>
      <span className="brand-icon">
        <Download size={22} />
      </span>
      <span>
        SocialVid<span className="brand-light">Downloader</span>
        <span className="brand-period">.</span>
      </span>
    </Link>
  );
}
