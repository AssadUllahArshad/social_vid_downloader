import processingTools from "../../../../content/processing/tools.json";
export const languageNames = {"tr": "Türkçe", "bn": "বাংলা", "de": "Deutsch", "ur": "اردو", "en": "English", "fr": "Français", "hi": "हिन्दी", "pt-br": "Português (Brasil)", "vi": "Tiếng Việt", "id": "Bahasa Indonesia", "th": "ไทย", "es": "Español", "ar": "العربية"} as const;
export type Locale = keyof typeof languageNames;
export const locales: Locale[] = ["en", "hi", "ur", "ar", "bn", "id", "vi", "th", "pt-br", "es", "fr", "de", "tr"];
export function isLocale(value: string): value is Locale { return Object.hasOwn(languageNames, value); }
export function languageTag(locale: Locale) { return locale === "pt-br" ? "pt-BR" : locale; }
export function direction(locale: Locale) { return locale === "ar" || locale === "ur" ? "rtl" : "ltr"; }
export function splitLocale(path: string) {
  const first = path.split("/")[1];
  const locale: Locale = isLocale(first) ? first : "en";
  return { locale, englishPath: isLocale(first) ? path.slice(first.length + 1) || "/" : path };
}
// Untranslated equivalents fall back to the localized home, never an English
// page misleadingly presented as a translated, indexable document.
export function localeDestination(locale: Locale, englishPath: string, available: string[] = ["/", "/facebook/", "/facebook-video-downloader/", "/facebook-reels-downloader/", "/instagram/", "/instagram-video-downloader/", "/instagram-reels-downloader/", "/youtube/", "/youtube-video-downloader/", "/youtube-shorts-downloader/", "/tiktok/", "/tiktok-video-downloader/", "/snapchat-downloader/", "/snapchat-spotlight-downloader/", "/guides/", "/faq/"]) {
  if (locale === "en") return englishPath === "/faq/" ? "/#faq" : englishPath;
  return `/${locale}${available.includes(englishPath) || englishPath === "/video-tools/" || processingTools.some(tool => `/${tool.slug}/`===englishPath) ? englishPath : "/"}`;
}
