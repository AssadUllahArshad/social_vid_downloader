import { pageMetadata } from "@/lib/publication";
import Link from "next/link";
import {
  Download,
  Play,
  Smartphone,
  ShieldCheck,
  SlidersHorizontal,
  Globe,
  Link2,
  ArrowUpRight,
  Check,
} from "lucide-react";
import { Downloader } from "@/components/downloader";
import { tools, platforms, site } from "@/lib/content";
export const metadata = pageMetadata("/");
const initials: Record<string, string> = {
  YouTube: "▶",
  Instagram: "◎",
  Facebook: "f",
  TikTok: "♪",
  Snapchat: "S",
  WhatsApp: "W",
};
export default function Home() {
  return (
    <main>
      <section className="hero container" id="download">
        <div className="eyebrow">
          <span className="tiny-mark">
            <Download size={13} />
          </span>{" "}
          ONE PLACE. ALL YOUR VIDEO TOOLS.
        </div>
        <h1>
          Download social media
          <br />
          videos <span>without the hassle.</span>
        </h1>
        <p className="hero-copy">
          A simpler way to save the videos that matter to you.
          <br className="desktop-break" /> Find your platform, paste a link, and
          check available qualities.
        </p>
        <Downloader />
        <div className="platform-strip">
          <span>Made for your favorite platforms</span>
          <div>
            {platforms.map((p) => (
              <Link
                aria-label={`${p} tools`}
                href={p === "Snapchat" ? "/snapchat-downloader/" : `/${p.toLowerCase()}/`}
                key={p}
                className={`platform-mini ${p.toLowerCase()}`}
              >
                {initials[p]}
              </Link>
            ))}
          </div>
        </div>
        <p className="release-note">
          Public links only. Availability depends on the source platform.
        </p>
      </section>
      <section className="tools-section" id="tools">
        <div className="container">
          <div className="section-heading">
            <div className="eyebrow">FIND YOUR TOOL</div>
            <h2>One link. The right downloader.</h2>
            <p>Dedicated tools for each platform and the way you use it.</p>
          </div>
          <div className="tool-grid">
            {platforms.map((p) => (
              <article className="platform-card" key={p}>
                <div className="platform-card-heading">
                  <span className={`platform-logo ${p.toLowerCase()}`}>
                    {initials[p]}
                  </span>
                  <span className="status-tag">
                    {p === "WhatsApp" ? "Unsupported" : ["Snapchat", "TikTok"].includes(p) ? "Beta" : "Public links"}
                  </span>
                </div>
                <h3>{p} downloaders</h3>
                <p>
                  {
                    (
                      {
                        YouTube:
                          "From long-form videos to your favorite Shorts.",
                        Instagram:
                          "Save public videos and Reels; Story downloads are unavailable.",
                        Facebook:
                          "Keep videos and Reels you have permission to save.",
                        TikTok: "Find the tool for your next shareable clip.",
                        Snapchat:
                          "Save supported public clips with the Snapchat Spotlight beta tool.",
                        WhatsApp:
                          "Learn about options for saving your own WhatsApp Status.",
                      } as Record<string, string>
                    )[p]
                  }
                </p>
                <div className="tool-links">
                  {tools
                    .filter((t) => t.platform === p)
                    .map((t) => (
                      <Link key={t.slug} href={`/${t.slug}/`}>
                        {t.kind || "Snapchat tools"} {t.kind ? "downloader" : ""}
                        <ArrowUpRight size={15} />
                      </Link>
                    ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
      <section className="container how-section">
        <div className="section-heading">
          <div className="eyebrow">KEEP IT SIMPLE</div>
          <h2>A few clicks from link to file.</h2>
          <p>Analyze the source, choose a real format, and save your file.</p>
        </div>
        <div className="steps">
          {[
            {
              icon: Link2,
              title: "Copy your video link",
              text: "Open the video on its platform and copy the share link.",
            },
            {
              icon: ClipboardIcon,
              title: "Paste it here",
              text: "Choose your tool and add the link to the URL field.",
            },
            {
              icon: SlidersHorizontal,
              title: "Choose a quality",
              text: "Select from the formats actually available for your video.",
            },
            {
              icon: Download,
              title: "Save your video",
              text: "Download the file to your phone, tablet, or computer.",
            },
          ].map((s, i) => (
            <article key={s.title}>
              <div className="step-icon">
                <s.icon size={23} />
                <span>{i + 1}</span>
              </div>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="benefits-section">
        <div className="container benefits-grid">
          <div>
            <div className="eyebrow">LESS FRICTION. MORE CONTROL.</div>
            <h2>
              Built around
              <br />
              the way you save.
            </h2>
            <p>
              A focused utility, with clear choices and no confusing buttons.
            </p>
            <div className="permission-note">
              <ShieldCheck size={19} />
              <span>
                Your permission matters.
                <br />
                Save only what you’re allowed to keep.
              </span>
            </div>
          </div>
          <div className="benefit-items">
            {[
              {
                icon: Smartphone,
                title: "At home on any screen",
                text: "A comfortable experience on phones, tablets, and desktops.",
              },
              {
                icon: SlidersHorizontal,
                title: "Real quality choices",
                text: "Available resolutions come from the source video.",
              },
              {
                icon: Globe,
                title: "No software to install",
                text: "Use your browser. Keep your device free of extra apps.",
              },
              {
                icon: ShieldCheck,
                title: "No passwords. Ever.",
                text: "We never ask for social account passwords or verification codes.",
              },
            ].map((s) => (
              <div className="benefit" key={s.title}>
                <s.icon size={21} />
                <div>
                  <h3>{s.title}</h3>
                  <p>{s.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
      <section className="container faq-section" id="faq">
        <div className="section-heading">
          <div className="eyebrow">GOOD TO KNOW</div>
          <h2>A little clarity before you download.</h2>
        </div>
        <div className="faq-list">
          {[
            [
              "Can I download videos right now?",
              "You can process public YouTube, Facebook, and Instagram links, with TikTok and Snapchat Spotlight in beta. Availability depends on the source. Instagram Stories, Snapchat Stories, and WhatsApp Status downloads remain unsupported.",
            ],
            [
              "What content can I save?",
              "Only content you own or have permission to download. A publicly visible video is not automatically licensed for reuse.",
            ],
            [
              "Will I need an account or an app?",
              "You can use the public-link tools in your browser without an account or an app. We never ask for your social account passwords or verification codes.",
            ],
            [
              "Can I download private Stories or WhatsApp Status?",
              "Private content is not supported. Snapchat Spotlight is in beta; Snapchat Stories and WhatsApp Status downloads remain unsupported.",
            ],
          ].map(([q, a]) => (
            <details key={q}>
              <summary>
                {q}
                <span>+</span>
              </summary>
              <p>{a}</p>
            </details>
          ))}
        </div>
      </section>
      <section className="container final-note">
        <span>
          <Check size={18} /> Clear links. Honest support. Your choice.
        </span>
        <Link href="/#tools">
          Explore all tools <ArrowUpRight size={16} />
        </Link>
      </section>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebSite",
            name: "SocialVidDownloader",
            url: site,
          }).replace(/</g, "\u003c"),
        }}
      />
    </main>
  );
}
function ClipboardIcon(props: { size?: number }) {
  return <Play {...props} />;
}
