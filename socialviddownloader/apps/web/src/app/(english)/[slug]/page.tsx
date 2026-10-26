import toolGuideLinks from "../../../../../../content/editorial/tool-guide-links.json";
import { processingTools } from "@/lib/processing-tools";
import { ProcessingPage } from "@/components/processing-page";
import { getArticle, pageMetadata, publicPages, publishedArticles } from "@/lib/publication";
import Link from "next/link";
import { notFound } from "next/navigation";
import { tools, platforms, site } from "@/lib/content";
import { Downloader } from "@/components/downloader";
import { JsonLd } from "@/components/json-ld";
export function generateStaticParams() {
  return [
    ...processingTools.map(tool=>({slug:tool.slug})),
    {slug:"video-tools"},
    ...tools.map((t) => ({ slug: t.slug })),
    ...platforms.filter((p) => p !== "Snapchat").map((p) => ({ slug: p.toLowerCase() })),
  ];
}
export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  if(slug === "video-tools" || processingTools.some(tool=>tool.slug===slug)) return pageMetadata(`/${slug}/`);
  const t = tools.find((t) => t.slug === slug);
  if (!t && !platforms.some((p) => p.toLowerCase() === slug)) notFound();
  if (slug === "snapchat") return { robots: { index: false, follow: true } };
  return pageMetadata(`/${slug}/`);
}
export default async function Tool({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  if(slug === "video-tools" || processingTools.some(tool=>tool.slug===slug)) return <ProcessingPage slug={slug}/>;
  const t = tools.find((t) => t.slug === slug);
  if (slug === "snapchat") notFound(); // The legacy alias redirects before route rendering.
  const platform = slug === "snapchat-downloader" ? "Snapchat" : platforms.find((p) => p.toLowerCase() === slug);
  if (!t && !platform) notFound();
  if (platform)
    return (
      <main className="container content-page">
        <div className="breadcrumb">
          <Link href="/">Home</Link> / {platform}
        </div>
        <h1>{platform === "Snapchat" ? "Snapchat Downloader" : `${platform} video tools`}</h1>
        <p>{publicPages.find((page) => page.path === `/${slug}/`)?.introduction}</p>
        <h2>Choose the matching content type</h2>
        <div className="related">
          {tools
            .filter((x) => x.platform === platform && x.status !== "hub")
            .map((x) => (
              <Link href={`/${x.slug}/`} key={x.slug}>
                {x.name} · {x.capabilityState === "BETA" ? "Beta" : x.capabilityState === "AVAILABLE" ? "Available" : "Unsupported"}
              </Link>
            ))}
        </div>
        <h2>What to expect after checking a link</h2>
        <p>Enabled tools validate the link, inspect source-provided formats, and show available quality and audio choices. Resolution, language options and file size depend on the actual source. Beta providers can fail when platform access changes.</p>
        {publishedArticles.some(page => page.platform === platform.toLowerCase()) && <section><h2>Help with links and files</h2><ul>{publishedArticles.filter(page => page.platform === platform.toLowerCase()).slice(0, 5).map(page => <li key={page.path}><Link href={page.path}>{page.title}</Link></li>)}</ul><p><Link href={`/guides/${platform.toLowerCase()}/`}>Browse this platform’s guides</Link></p></section>}
        <h2>Permissions and access</h2>
        <p>Download only content you own or have permission to save. We do not bypass private accounts, authentication or DRM and never request passwords or session cookies.</p>
        <p><Link href="/about/">How this service works</Link> · <Link href="/">Browse other platforms</Link></p>
        <JsonLd data={{ "@context": "https://schema.org", "@type": "BreadcrumbList", itemListElement: [
          { "@type": "ListItem", position: 1, name: "Home", item: `${site}/` },
          { "@type": "ListItem", position: 2, name: platform, item: `${site}/${slug}/` },
        ] }} />
      </main>
    );
  if (!t) notFound();
  const guides = toolGuideLinks.filter(link => link.source === `/${slug}/` && getArticle(link.target)?.indexable);
  const active = t.status === "integrated" || t.status === "beta";
  const related = tools.filter(
    (x) => x.platform === t.platform && x.slug !== t.slug,
  );
  return (
    <main className="container content-page">
      <div className="breadcrumb">
        <Link href="/">Home</Link> /{" "}
        <Link href={t.platform === "Snapchat" ? "/snapchat-downloader/" : `/${t.platform.toLowerCase()}/`}>{t.platform}</Link> /{" "}
        {t.name}
      </div>
      <h1>{t.name}</h1>
      <p>{t.intro}</p>
      <Downloader
        example={t.example}
        platform={t.platform}
        contentType={t.kind.toLowerCase() || undefined}
        enabled={active}
        capabilityState={t.capabilityState as "AVAILABLE" | "BETA" | "TEMPORARILY_UNAVAILABLE" | "UNSUPPORTED"}
      />
      <div className="notice">
        {active
          ? `Paste a public ${t.platform} link to check available video qualities. Platform restrictions may prevent a download.`
          : `This ${t.platform} content type is not currently supported.`}{" "}
        We never ask for account passwords, verification codes, or session cookies.
      </div>
      <h2>
        How to save content from {t.platform}
      </h2>
      <ol>
        <li>{t.step}</li>
        <li>Confirm you own the content or have permission to save it.</li>
        <li>
          {active
            ? "Paste the video link above to see the available qualities."
            : "Downloading with this tool is currently unavailable."}
        </li>
        <li>Choose an available quality if the video can be processed.</li>
      </ol>
      <h2>Which links does this tool recognize?</h2>
      <p>{t.domains}</p>
      {t.example && (
        <p>
          URL pattern: <code>{t.example}</code>. This is a format example, not a
          sample video.
        </p>
      )}
      <h2>Quality and device compatibility</h2>
      <p>
        No resolutions or file sizes are shown until a supported provider
        supplies them. A source may offer fewer formats than expected. The
        interface works in current mobile and desktop browsers; file saving
        behavior depends on your device.
      </p>
      <h2>Why might a link from {t.platform} fail?</h2>
      <p>
        Deleted media, platform restrictions, login requirements, expired share
        links, or unavailable integrations can prevent processing. Do not submit
        private account credentials to fix an error. Use the platform’s own save
        or export controls when available.
      </p>
      {guides.length > 0 && <ul aria-label="Related guidance">{guides.map(guide => <li key={guide.target}><Link href={guide.target}>{guide.anchor}</Link></li>)}</ul>}
      <h2>Related tools</h2>
      <div className="related">
        {(related.length
          ? related
          : tools.filter(
              (x) =>
                x.slug === "youtube-shorts-downloader" ||
                x.slug === "instagram-video-downloader",
            )
        ).map((x) => (
          <Link key={x.slug} href={`/${x.slug}/`}>
            {x.name}
          </Link>
        ))}
      </div>
      <h2>Frequently asked questions</h2>
      <details>
        <summary>Does the {t.name} work today?</summary>
        <p>
          {active
            ? "Yes, for supported public videos. Availability depends on the source video and current platform restrictions. You can choose only from the formats available for that video."
            : "No. Downloading this content type is currently unavailable."}
        </p>
      </details>
      <details>
        <summary>Can this tool access private {t.platform} content?</summary>
        <p>
          No. It cannot bypass authentication, permissions, DRM, or platform
          access controls.
        </p>
      </details>
      <details>
        <summary>What should I do instead?</summary>
        <p>
          {t.step} If downloading is not offered, request the original file from
          its owner.
        </p>
      </details>
      <p className="notice">
        Download only content you own or have permission to save.
      </p>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: [
            { "@type": "ListItem", position: 1, name: "Home", item: site },
            {
              "@type": "ListItem",
              position: 2,
              name: t.platform,
              item: `${site}/${t.platform === "Snapchat" ? "snapchat-downloader" : t.platform.toLowerCase()}/`,
            },
            {
              "@type": "ListItem",
              position: 3,
              name: t.name,
              item: `${site}/${t.slug}/`,
            },
          ],
        }}
      />
    </main>
  );
}
