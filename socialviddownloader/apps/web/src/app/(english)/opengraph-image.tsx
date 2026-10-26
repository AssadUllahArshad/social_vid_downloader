import { ImageResponse } from "next/og";

export const alt = "SocialVidDownloader — social video tools and practical guides";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function Image() {
  return new ImageResponse(
    <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", width: "100%", height: "100%", padding: 80, background: "#101b33", color: "#ffffff" }}>
      <div style={{ fontSize: 64, fontWeight: 700 }}>SocialVidDownloader</div>
      <div style={{ marginTop: 28, fontSize: 34, color: "#b8c9e6" }}>Social video tools and practical guides</div>
      <div style={{ marginTop: 70, fontSize: 24, color: "#b8c9e6" }}>Download only content you own or have permission to save.</div>
    </div>,
    size,
  );
}
