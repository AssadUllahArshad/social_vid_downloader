import records from "../../../../content/pages/tools.json";
export const tools = records;
export const platforms = [
  "YouTube",
  "Instagram",
  "Facebook",
  "TikTok",
  "Snapchat",
  "WhatsApp",
];
export function platformName(value: string) {
  return platforms.find((name) => name.toLowerCase() === value.toLowerCase()) || value;
}
export const site =
  process.env.NEXT_PUBLIC_SITE_URL || "https://socialviddownloader.com";

