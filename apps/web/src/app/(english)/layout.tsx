import type { Metadata } from "next";
import { site } from "@/lib/content";
import { SiteShell } from "@/components/site-shell";
import "../globals.css";
export const metadata: Metadata = {
  metadataBase: new URL(site),
  verification: {
    google: ["8ElT4TSYUCfL74tNmQVNwZtIsmcO50zQztzCpcREaPA", "nZGKtrCudfVIUamVCQqmvJPfpdDHXtntJ0wbelNaEdA"],
    other: {
      "msvalidate.01": "4CBA24802AF5D42BEA67CED85396296C",
    },
  },
  title: {
    default: "SocialVidDownloader - Download Social Media Videos Online",
    template: "%s | SocialVidDownloader",
  },
  description:
    "A simple place to find social video tools, understand supported links, and save content you have permission to download.",
  openGraph: { type: "website", siteName: "SocialVidDownloader" },
  twitter: { card: "summary" },
  icons: { icon: "/favicon.svg" },
};
export default function Layout({children}:{children:React.ReactNode}) { return <html lang="en" dir="ltr"><body><SiteShell locale="en">{children}</SiteShell></body></html>; }
