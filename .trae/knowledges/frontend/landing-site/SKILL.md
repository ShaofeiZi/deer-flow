---
name: frontend-landing-site
description: >
  Landing site and authentication pages for the DeerFlow frontend — covers the marketing
  homepage with animated hero, feature sections, blog, login/register page, and first-boot
  setup flow. Navigate here when working on the public-facing website, authentication UI,
  or static/demo mode landing page behavior.
covers:
  - frontend/src/components/landing/
  - frontend/src/app/(auth)/
  - frontend/src/app/blog/
  - frontend/src/content/
navigate-when:
  - modifying the landing page hero, header, footer, or feature sections
  - working on the login/register page UI or form validation
  - debugging open redirect vulnerabilities in login flow
  - adding or modifying blog posts or content pages
  - changing static/demo mode landing page behavior
  - working with the first-boot setup wizard
excludes:
  - workspace UI (workspace-interface domain)
  - core services (core-services domain)
  - settings (settings-system domain)
  - i18n (internationalization domain)
keywords:
  - landing page
  - hero
  - login
  - register
  - setup wizard
  - blog
  - marketing
  - Galaxy
  - FlickeringGrid
  - WordRotate
  - open redirect
  - static website
---

## Module Structure

```
frontend/src/components/landing/
├── hero.tsx                        # Hero section with Galaxy, FlickeringGrid, WordRotate animations
├── header.tsx                      # Site header with nav links, GitHub star counter, i18n support
├── footer.tsx                      # Site footer
├── section.tsx                     # Reusable section wrapper component
├── post-list.tsx                   # Blog post list component
├── progressive-skills-animation.tsx # Animated skills demonstration
└── sections/
    ├── skills-section.tsx          # Agent Skills feature section
    ├── sandbox-section.tsx         # Sandbox feature section
    ├── case-study-section.tsx      # Case study section
    ├── community-section.tsx       # Community section
    └── whats-new-section.tsx       # What's New section

frontend/src/app/(auth)/
├── layout.tsx                      # Auth pages layout
├── login/
│   └── page.tsx                    # Login/register page with open redirect prevention
└── setup/
    └── page.tsx                    # First-boot setup wizard

frontend/src/app/blog/              # Blog pages
frontend/src/content/               # Markdown/MDX content for blog posts and pages
```

Key entry points:
- `Hero` in `hero.tsx` — the main landing page hero with animated background and CTA
- `Header` in `header.tsx` — server component with i18n-aware navigation and GitHub star counter
- `LoginPage` in `(auth)/login/page.tsx` — client component with login/register toggle and open redirect validation
- `validateNextParam()` in `login/page.tsx` — security-critical redirect validation function

## Gotchas

- The login page's `validateNextParam()` is a security-critical function that prevents open redirect attacks — it must reject protocol-relative URLs (`//evil.com`), absolute URLs (`http://`, `https://`), and URLs with dangerous protocols (`javascript:`, `data:`) (frontend/src/app/(auth)/login/page.tsx:19-45)
- Login uses `application/x-www-form-urlencoded` for the login endpoint but `application/json` for the register endpoint — mixing these up will cause 422 validation errors from FastAPI (frontend/src/app/(auth)/login/page.tsx:99-105)
- The login page checks `setup-status` on mount and redirects to `/setup` if the system hasn't been initialized — this is a client-side check; the SSR auth guard also handles `system_setup_required` (frontend/src/app/(auth)/login/page.tsx:71-88)
- The `Header` component is an async server component that calls `getI18n(locale)` — it cannot be used inside client components without passing locale as a prop (frontend/src/components/landing/header.tsx:17-20)
- The `StarCounter` component fetches GitHub stars at request time with `next: { revalidate: 3600 }` (ISR) — it requires `GITHUB_OAUTH_TOKEN` to avoid rate limiting; without the token, it falls back to a default of 10000 stars (frontend/src/components/landing/header.tsx:82-116)
- In static mode (`NEXT_PUBLIC_STATIC_WEBSITE_ONLY=true`), the hero shows a "In partnership with BytePlus" banner — this is gated by the env var and links to `byteplus.com` (frontend/src/components/landing/hero.tsx:60-71)

## Architecture

- Landing page composition: the homepage assembles `Header`, `Hero`, and multiple feature `Section` components — each section is a self-contained component with its own animations and content (frontend/src/components/landing/hero.tsx, frontend/src/components/landing/sections/)
- Hero animation layering: the hero uses three z-index layers — `Galaxy` (starfield background, z-0), `FlickeringGrid` (deer-shaped mask overlay, z-0), and content (z-10) — the FlickeringGrid uses a CSS mask from `/images/deer.svg` (frontend/src/components/landing/hero.tsx:21-38)
- Login page dual-mode: the same page component handles both login and register via an `isLogin` boolean state — the form endpoint, Content-Type, and body format change based on this toggle (frontend/src/app/(auth)/login/page.tsx:96-105)
- Auth redirect flow: after successful login/register, the user is redirected to `redirectPath` which is validated by `validateNextParam()` — if the `next` query param is invalid or missing, it defaults to `/workspace` (frontend/src/app/(auth)/login/page.tsx:60-61,122)
- Header i18n integration: the `Header` is a server component that accepts an optional `locale` prop — it resolves translations server-side via `getI18n()` and renders localized nav links (`/{lang}/docs`, `/blog/posts`) (frontend/src/components/landing/header.tsx:17-48)

## Patterns

- Open redirect prevention: `validateNextParam()` uses a whitelist approach — only relative paths starting with `/` are allowed; protocol-relative, absolute, and protocol-containing URLs are rejected (frontend/src/app/(auth)/login/page.tsx:19-45)
- Server component with client children: the `Header` is an async server component that fetches data (GitHub stars, i18n) at render time, while `Hero` and section components are client components with interactive animations (frontend/src/components/landing/header.tsx:17, frontend/src/components/landing/hero.tsx:1)
- Animated word rotation: `WordRotate` cycles through capability descriptions ("Deep Research", "Collect Data", "Analyze Data", etc.) — this is a client-side animation component (frontend/src/components/landing/hero.tsx:41-57)
- Feature sections as composable blocks: each landing section (`SkillsSection`, `SandboxSection`, `CaseStudySection`, etc.) uses the shared `Section` wrapper with `title` and `subtitle` props — this ensures consistent layout across the page (frontend/src/components/landing/sections/skills-section.tsx:8-27)

## Dependencies

- `next/link`, `next/navigation` — routing for CTA buttons, nav links, and auth redirects (frontend/src/components/landing/hero.tsx:4, frontend/src/app/(auth)/login/page.tsx:3-4)
- `next-themes` — `useTheme` for theme-aware FlickeringGrid color on login page (frontend/src/app/(auth)/login/page.tsx:5)
- `lucide-react` — `ChevronRightIcon` for CTA button (frontend/src/components/landing/hero.tsx:3)
- `@radix-ui/react-icons` — `StarFilledIcon`, `GitHubLogoIcon` for header (frontend/src/components/landing/header.tsx:1)
- `@/components/ui/button` — shadcn/ui Button component (frontend/src/components/landing/hero.tsx:6)
- `@/components/ui/flickering-grid` — animated grid background with SVG mask (frontend/src/components/landing/hero.tsx:7)
- `@/components/ui/galaxy` — starfield background animation (frontend/src/components/landing/hero.tsx:8)
- `@/components/ui/word-rotate` — rotating word animation (frontend/src/components/landing/hero.tsx:9)
- `@/components/ui/number-ticker` — animated number display for GitHub stars (frontend/src/components/landing/header.tsx:5)
- `@/core/auth/AuthProvider` — `useAuth()` for login page auth state (frontend/src/app/(auth)/login/page.tsx:11)
- `@/core/auth/types` — `parseAuthError()` for login error handling (frontend/src/app/(auth)/login/page.tsx:12)
- `@/core/i18n/server` — `getI18n()` for server-side translations in Header (frontend/src/components/landing/header.tsx:7)
- `@/env` — `env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY` for static mode gating (frontend/src/components/landing/hero.tsx:10)
