import type { NextConfig } from "next";
const config: NextConfig = {
  output: "standalone",
  // Keep a running development server independent of production rebuilds.
  distDir: process.env.NODE_ENV === "development" ? ".next-dev" : ".next",
  trailingSlash: true,
  async redirects() {
    return [{ source: "/snapchat/", destination: "/snapchat-downloader/", permanent: true }];
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Content-Security-Policy", value: `default-src 'self'; script-src 'self' 'unsafe-inline' https://analytics.ahrefs.com https://www.googletagmanager.com${process.env.NODE_ENV === 'development' ? " 'unsafe-eval'" : ''}; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https://www.googletagmanager.com https://*.google-analytics.com; media-src 'self' blob:; connect-src 'self' https://analytics.ahrefs.com https://www.googletagmanager.com https://*.google-analytics.com https://*.google.com; font-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'` },
          ...(process.env.ENABLE_HSTS === "1" ? [{ key: "Strict-Transport-Security", value: "max-age=31536000" }] : []),
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },
};
export default config;
