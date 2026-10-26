import type { MetadataRoute } from "next";
import { site } from "@/lib/content";
export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: ["/admin", "/api/", "/internal/", "/search/", "/temp/", "/preview/", "/_not-found", "/_global-error"],
    },
    sitemap: `${site}/sitemap.xml`,
  };
}
