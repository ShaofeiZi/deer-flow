---
name: frontend-internationalization
description: >
  Internationalization (i18n) system for the DeerFlow frontend — covers locale detection,
  React context-based translation provider, cookie persistence, server-side locale resolution,
  and the translations type system. Navigate here when adding new translation keys, modifying
  locale detection logic, or working with bilingual (en-US/zh-CN) content.
covers:
  - frontend/src/core/i18n/
  - frontend/src/content/
navigate-when:
  - adding new translation keys or modifying existing translations
  - debugging locale not persisting across page reloads
  - understanding how server-side and client-side locale detection interact
  - adding a new supported locale beyond en-US and zh-CN
  - working with locale-specific content or blog posts
excludes:
  - settings persistence (settings-system domain)
  - API integration (api-integration domain)
  - UI components (workspace-interface domain)
keywords:
  - i18n
  - internationalization
  - locale
  - translations
  - en-US
  - zh-CN
  - cookie persistence
  - I18nProvider
  - useI18n
  - server-side locale
---

## Module Structure

```
frontend/src/core/i18n/
├── index.ts           # Barrel exports: enUS, zhCN, Translations type, locale utilities
├── locale.ts          # Locale type, SUPPORTED_LOCALES, DEFAULT_LOCALE, normalizeLocale(), detectLocale()
├── context.tsx        # I18nProvider (React context) with cookie persistence
├── hooks.ts           # useI18n() — client hook combining context + cookie sync + browser detection
├── server.ts          # detectLocaleServer(), setLocale(), getI18n() — server-side utilities
├── cookies.ts         # getLocaleFromCookie(), setLocaleInCookie(), getLocaleFromCookieServer()
├── translations.ts    # translations: Record<Locale, Translations> — maps locale to translation object
└── locales/
    ├── index.ts       # Re-exports enUS, zhCN, Translations type
    ├── types.ts       # Translations interface — the single source of truth for all translation keys
    ├── en-US.ts       # English (US) translations
    └── zh-CN.ts       # Chinese (Simplified) translations
```

Key entry points:
- `useI18n()` in `hooks.ts` — the main client hook; returns `{ locale, t, changeLocale }`
- `getI18n()` in `server.ts` — server-side equivalent; returns `{ locale, t }` for server components
- `I18nProvider` in `context.tsx` — wraps the app; accepts `initialLocale` from SSR
- `Translations` interface in `locales/types.ts` — defines all translation key paths

## Gotchas

- The `Translations` interface in `types.ts` is the single source of truth — adding a key to `en-US.ts` without adding it to the interface will cause a TypeScript error; adding it to the interface without adding it to `zh-CN.ts` will also cause a TypeScript error (frontend/src/core/i18n/locales/types.ts)
- `useI18n()` calls `setLocale()` in a `useEffect` on mount — this means the first render always uses the `initialLocale` from SSR; the client-detected locale only takes effect on the second render (frontend/src/core/i18n/hooks.ts:27-41)
- The locale cookie is set with `max-age=31536000` (1 year) and `SameSite=Lax` — changing the cookie attributes requires updating both `context.tsx` (client-side `document.cookie`) and `server.ts` (server-side `cookieStore.set`) (frontend/src/core/i18n/context.tsx:25, frontend/src/core/i18n/server.ts:23-27)
- `normalizeLocale()` maps any `zh*` prefix to `zh-CN` and everything else to `en-US` — this means `zh-TW`, `zh-HK`, and other Chinese variants all resolve to `zh-CN` (Simplified Chinese) (frontend/src/core/i18n/locale.ts:27-41)
- `detectLocale()` reads `navigator.language` with a fallback to `navigator.userLanguage` (IE-specific) — if neither is available, it returns `en-US`; there is no user preference UI for locale selection beyond the browser setting (frontend/src/core/i18n/locale.ts:44-54)
- Server-side locale detection uses `next/headers` `cookies()` which requires `await` — calling `detectLocaleServer()` without `await` will return a Promise, not a Locale (frontend/src/core/i18n/server.ts:6-17)

## Architecture

- Dual-path locale resolution: server components use `detectLocaleServer()` (reads cookie via `next/headers`), client components use `useI18n()` (reads cookie via `document.cookie`, falls back to `navigator.language`, then browser detection) — both paths normalize through the same `normalizeLocale()` function (frontend/src/core/i18n/server.ts:6-17, frontend/src/core/i18n/hooks.ts:27-41)
- React context with cookie persistence: `I18nProvider` holds locale in React state and writes changes to a cookie — the cookie serves as the persistence layer across page reloads, while React state provides reactivity within the session (frontend/src/core/i18n/context.tsx:14-33)
- Translation object as typed record: `translations` is a `Record<Locale, Translations>` — `useI18n()` selects `translations[locale] ?? translations[DEFAULT_LOCALE]`, so missing locale data falls back to English (frontend/src/core/i18n/translations.ts:4-7, frontend/src/core/i18n/hooks.ts:19)
- Client-side initialization cascade: on mount, `useI18n` checks cookie → normalizes → if no cookie, detects from browser → normalizes → saves to cookie — this ensures the cookie always reflects the resolved locale after the first client render (frontend/src/core/i18n/hooks.ts:27-41)

## Patterns

- Typed translation keys: the `Translations` interface uses nested objects (e.g., `settings.sections.account`, `home.docs`, `uploads.uploadingFiles`) — TypeScript enforces that all keys exist in both locale files (frontend/src/core/i18n/locales/types.ts)
- SSR-safe cookie utilities: `getLocaleFromCookie()` returns `null` when `document` is undefined, and `getLocaleFromCookieServer()` wraps `next/headers` in a try/catch — both are safe to import in any environment (frontend/src/core/i18n/cookies.ts:11-52)
- Locale normalization as pure function: `normalizeLocale()` is a pure function with no side effects — it handles `null`, `undefined`, valid locales, and prefix matching, always returning a valid `Locale` (frontend/src/core/i18n/locale.ts:27-41)
- Barrel export structure: `index.ts` re-exports from `locales/`, `locale.ts`, and `translations.ts` — consumers import from `@/core/i18n` without needing to know the internal file structure (frontend/src/core/i18n/index.ts)

## Dependencies

- `react` — `createContext`, `useContext`, `useState`, `useEffect` for context provider and hooks (frontend/src/core/i18n/context.tsx:3, frontend/src/core/i18n/hooks.ts:3)
- `next/headers` — `cookies()` for server-side cookie access (frontend/src/core/i18n/server.ts:1, frontend/src/core/i18n/cookies.ts:45)
- No external i18n libraries — the system is built entirely on React context and custom utilities, with no dependency on `next-intl`, `react-i18next`, or similar packages
