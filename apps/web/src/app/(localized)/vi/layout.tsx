import { site } from "@/lib/content";
export const metadata = { metadataBase: new URL(site), icons: { icon: "/favicon.svg" }, openGraph: {siteName:"SocialVidDownloader",type:"website",images:["/opengraph-image"]},twitter:{card:"summary"} };
import { SiteShell } from "@/components/site-shell";
import "../../globals.css";
export default function Layout({children}:{children:React.ReactNode}) { return <html lang="vi" dir="ltr"><body><SiteShell locale="vi">{children}</SiteShell></body></html>; }
