# Frontend styling regression — 12 October 2026

## Root cause

Port 3000 was an old standalone production process, not a development server. Its working directory was apps/web/.next/standalone/apps/web. Production rebuilds replaced that live directory while the process retained old rendered HTML referencing deleted hashed CSS and JavaScript. A fresh Chromium context reproduced default Times typography and unstyled links/cards. The old stylesheet 19a5f78b4b2b6639.css and several old chunks returned HTTP 500 with text/plain, triggering MIME rejection. This was server artifact mismatch, not stale browser CSS.

All 13 root layouts import globals.css. Tailwind's PostCSS plugin and compiled layers are intact. No assetPrefix/basePath issue, omitted multilingual stylesheet or video-tool layout override was found. No stylesheet or design changes were needed.

## Fix and files

- apps/web/next.config.ts: development output now uses .next-dev; production retains .next. Production builds cannot replace the running development artifact directory.
- apps/web/tsconfig.json: Next-generated includes for the separate development types.
- apps/web/eslint.config.mjs and .gitignore: exclude generated development artifacts.
- apps/web/e2e/styling.spec.ts: regression coverage for fonts, navigation, link styling, valid compiled CSS, asset failures, viewport bounds and RTL.
- README.md: correct local modes and immutable production release guidance.
- docs/styling-verification/: actual before/after screenshots and network evidence.

Stopped the stale standalone process and started a real development server on port 3000. Its local API_INTERNAL_URL points to the current verified API on port 8001, using its existing SQLite/state/media paths. This resolves the separate processing-capabilities 404 from the older port-8000 API. No backend/provider code, database reset, SEO pages or design changes.

## Verification

Development: 50 page/viewport combinations passed. Production: the same 50 combinations passed against a freshly built standalone bundle with matching public/static assets. Pages cover English homepage, YouTube downloader, Video Converter, an existing article, and Arabic/Urdu homes/downloaders/converters. Widths: 320, 390, 768, 1366 and 1920.

TypeScript: PASS. ESLint: PASS. Production Webpack build: PASS. Two focused browser tests passed, each containing 50 combinations. Production test server was stopped after verification to avoid rebuilding underneath it later. Development remains available at http://127.0.0.1:3000/.

CSS: 200, text/css; compiled Tailwind @layer and original global rules present. Repeated navigation/reload correctly revalidates with 304 and no-cache, must-revalidate. Zero service workers. Final screenshot capture: zero failed network responses and zero console errors; processing controls enabled. Real desktop/mobile/Arabic/Urdu screenshots were visually inspected. Existing fonts, green buttons, cards, backgrounds and spacing are restored.

Reload any already-open old tab once to obtain the current HTML and asset references. Clearing browser storage is not required.
