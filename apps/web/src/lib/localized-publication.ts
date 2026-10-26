import { processingPaths, processingTools } from "./processing-tools";
import { processingMessages } from "./processing-messages";
import records from '../../../../content/translations/pages.json';
import { dictionaries, locales, languageTag, type Locale } from './i18n';
import { corePaths as originalCorePaths, eligibleTranslation } from './translation-policy.mjs';
export const corePaths = [...originalCorePaths, ...processingPaths];
export function translation(locale: Locale, englishPath: string) { return records.find(row => row.locale === locale && row.englishPath === englishPath); }
export function translatedIndexable(locale: Locale, englishPath: string) { const row = translation(locale, englishPath); return !!row && englishPath !== '/faq/' && eligibleTranslation(row, processingPaths.includes(englishPath) ? {...dictionaries[locale],...processingMessages[locale]} : dictionaries[locale]) && (!processingPaths.includes(englishPath) || (englishPath === "/video-tools/" ? processingTools.some(tool=>tool.publicEnabled) : processingTools.some(tool=>`/${tool.slug}/`===englishPath && tool.publicEnabled && tool.indexable))); }
export function equivalentLanguages(englishPath: string) {
 const languages: Record<string,string> = { en: englishPath, 'x-default': englishPath };
 for (const locale of locales.filter(code=>code!=='en')) if (translatedIndexable(locale,englishPath)) languages[languageTag(locale)] = `/${locale}${englishPath}`;
 return languages;
}
export function localizedPages() { return records.filter(row=>translatedIndexable(row.locale as Locale,row.englishPath)).map(row=>({path:`/${row.locale}${row.englishPath}`,status:'PUBLISHED',indexable:true,canonical:`/${row.locale}${row.englishPath}`})); }
