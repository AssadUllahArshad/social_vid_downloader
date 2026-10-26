export const PAGE_SIZE = 24;
export const familyLabels = Object.fromEntries([
  ["how-to", "Source link guides"], ["troubleshooting", "Troubleshooting"],
  ["device", "Devices and storage"], ["browser", "Browser downloads"],
  ["formats", "Formats and quality"], ["platform-help", "Platform help"],
  ["comparison", "Comparisons"], ["glossary", "Video concepts"],
  ["audio", "Audio and languages"], ["faq", "Questions and answers"],
  ["use-case", "Archive use cases"], ["captions", "Captions and subtitles"],
  ["codecs", "Codec compatibility"], ["copyright", "Privacy and permission"],
  ["creator", "Creator and editing workflows"],
]);
export const platformLabels = Object.fromEntries([
  ["general", "Cross-platform video"], ["youtube", "YouTube"],
  ["facebook", "Facebook"], ["instagram", "Instagram"],
  ["tiktok", "TikTok"], ["snapchat", "Snapchat Spotlight"],
  ["whatsapp", "WhatsApp media and privacy"],
]);
export function collectionPages(articles) {
  if (!articles.length) return [];
  const records = [{ path: "/topics/", title: "Browse video help by subject", description: "Choose a subject to find reviewed video, audio, browser and storage guidance." }];
  const groups = new Map();
  for (const article of articles) {
    for (const [key, prefix, label] of [[article.platform, "guides", platformLabels[article.platform]], [article.family, "topics", familyLabels[article.family] || article.family]]) {
      const path = `/${prefix}/${key}/`;
      const group = groups.get(path) || { label, count: 0 };
      group.count++;
      groups.set(path, group);
    }
  }
  for (const [root, group] of groups) {
    for (let number = 1; number <= Math.ceil(group.count / PAGE_SIZE); number++) {
      records.push({ path: number === 1 ? root : `${root}page/${number}/`, title: `${group.label} guidance${number > 1 ? ` — page ${number}` : ""}`, description: `Browse reviewed ${group.label.toLowerCase()} answers${number > 1 ? ` on page ${number}` : ""}. Choose the problem or decision relevant to your video workflow.` });
    }
  }
  return records.map(page => ({ ...page, canonical: page.path, type: "directory", status: "PUBLISHED", indexable: false }));
}
