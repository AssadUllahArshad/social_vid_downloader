> Historical checkpoint; current upload-tool release counts and verification are in [video-tools-final-report.md](video-tools-final-report.md).

# Multilingual production system

English URLs remain unchanged. The 13 supported languages are English, Hindi, Urdu, Arabic, Bengali, Indonesian, Vietnamese, Thai, Brazilian Portuguese, Spanish, French, German and Turkish. Prefixes use lowercase pt-br, while HTML/hreflang uses pt-BR. There are no IP redirects or preference-driven overrides of explicit URLs.

## Routing and rendering

English pages use `(english)` with a static English root layout. Twelve explicit locale directories use static root layouts and prerendered catch-all core pages. Request-header locale detection and the Next proxy have been removed. All 192 localized core pages are prerendered; unknown locale paths and unsupported Story paths return 404. Navigation between root layouts performs an ordinary full load, preserving correct HTML lang/dir. API routes remain shared and dynamic; no backend/provider code is duplicated.

## Product content

Each locale covers home, five platform hubs, eight active download tools, Guides and FAQ/help: 16 pages. Copy includes authorization, source-dependent qualities, processing instructions, audio behavior and known limitations. The common downloader uses a selected-locale context and dictionary for controls, help, validation, statuses and safe categorized backend errors. The browser receives its selected dictionary plus a small language-name/routing catalog, not the entire article or candidate corpus.

UI dictionaries are separate from translation lifecycle records: `apps/web/src/locales/*.json` and `content/translations/pages.json`. No article topics were generated or translated. Guides clearly identify detailed articles as English until reviewed translations exist. Legal navigation labels are localized; the actual legal/contact pages remain the existing English documents and links declare English.

## Selector and RTL

The selector uses accessible native details/summary with ordinary crawlable language links, a bounded scrollable menu, current-language highlighting, native names, keyboard focus and Escape support. Selection stores a lightweight local preference when storage is available but does not force redirects. Existing equivalent pages are preserved; untranslated articles fall back to the selected language's homepage. English switching returns to the original English path; localized FAQ returns to the existing English home FAQ section.

Arabic and Urdu have server-rendered `dir=rtl`. URL entry stays LTR. Technical source names, media format codes and resolutions remain recognizable. RTL quality, dual-audio and prepared-preview behavior are covered with real local media fixtures and the existing shared request contract.

## Publication and SEO

Lifecycle states remain DRAFT_TRANSLATION, REVIEW_TRANSLATION, APPROVED_TRANSLATION and PUBLISHED_TRANSLATION. Publication additionally requires complete=true, reviewApproved=true and an approval digest matching the current dictionary. Changing a dictionary invalidates indexability and sitemap/hreflang membership until re-reviewed. Production review records describe implementation review, not independent native-speaker certification.

180 core translations self-canonicalize and are indexable, with reciprocal English/self/other-approved hreflang and x-default pointing to the original English equivalent. Twelve localized FAQ pages are complete public noindex utilities because English has an FAQ section rather than a standalone equivalent page. They are excluded from hreflang and sitemap. Unapproved/stale translations fail closed. Sitemaps include only eligible translations; English publication eligibility remains unchanged.

No Snapchat Story or unsupported WhatsApp downloader page was created. YouTube access remains variable; TikTok and Spotlight are experimental. Localized errors never expose raw provider diagnostic messages.

## Validation

See multilingual-launch-report.md for fresh counts and final test results. The complete HTTP audit includes English and localized pages; publication tests cover dictionary completeness and digest revocation; browser tests cover all locales, equivalent/fallback switching, hreflang, canonicals, unknown routes, keyboard access, RTL controls and both English/localized audio workflows. Deployment remains manual, with PostgreSQL/Redis/Docker runtime checks on the target host.
