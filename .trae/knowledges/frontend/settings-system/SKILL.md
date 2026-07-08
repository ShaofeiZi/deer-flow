---
name: frontend-settings-system
description: >
  Client-side settings persistence for the DeerFlow frontend — covers localStorage-based
  settings store with `useSyncExternalStore`, cross-tab synchronization, per-thread model
  overrides, and the settings dialog UI. Navigate here when working on user preferences,
  notification settings, token usage display configuration, or model selection persistence.
covers:
  - frontend/src/core/settings/
  - frontend/src/components/workspace/settings/
navigate-when:
  - adding a new settings category (notification, tokenUsage, context, etc.)
  - debugging settings not persisting across page reloads
  - understanding how per-thread model overrides work
  - modifying the settings dialog UI or adding new settings pages
  - working with cross-tab settings synchronization
excludes:
  - thread streaming (thread-client domain)
  - API integration (api-integration domain)
  - i18n (internationalization domain)
keywords:
  - localStorage
  - useSyncExternalStore
  - settings persistence
  - cross-tab sync
  - thread model override
  - LocalSettings
  - settings dialog
  - notification settings
  - token usage
---

## Module Structure

```
frontend/src/core/settings/
├── local.ts           # LocalSettings type, DEFAULT_LOCAL_SETTINGS, localStorage read/write, thread model overrides
├── store.ts           # External store with subscribe/getSnapshot pattern, cross-tab sync via storage event
├── hooks.ts           # useLocalSettings(), useThreadSettings() — React hooks wrapping useSyncExternalStore
└── index.ts           # Barrel exports

frontend/src/components/workspace/settings/
├── settings-dialog.tsx        # Settings dialog with 7 sections (account, appearance, memory, tools, skills, notification, about)
├── account-settings-page.tsx  # Change password, change email, logout
├── appearance-settings-page.tsx # Theme selection
├── memory-settings-page.tsx   # Memory configuration
├── notification-settings-page.tsx # Notification toggle
├── skill-settings-page.tsx    # Skill management
├── tool-settings-page.tsx     # Tool configuration
└── about-settings-page.tsx    # Version and about info
```

Key entry points:
- `useLocalSettings()` in `hooks.ts` — returns `[LocalSettings, LocalSettingsSetter]` for global settings
- `useThreadSettings()` in `hooks.ts` — returns `[LocalSettings, LocalSettingsSetter]` with per-thread model override applied
- `getLocalSettings()` / `saveLocalSettings()` in `local.ts` — raw localStorage read/write with default merging
- `SettingsDialog` in `settings-dialog.tsx` — the settings UI with 7 tabbed sections

## Gotchas

- Settings are stored in localStorage as JSON under the key `deerflow.local-settings` — malformed JSON silently falls back to defaults without warning; there is no migration path for schema changes (frontend/src/core/settings/local.ts:19,109-121)
- The settings store uses `useSyncExternalStore` with a server snapshot of `DEFAULT_LOCAL_SETTINGS` — during SSR, all components see default settings; client-specific values only appear after hydration (frontend/src/core/settings/hooks.ts:17-29)
- Per-thread model overrides are stored in separate localStorage keys (`deerflow.thread-model.<threadId>`) — they are NOT part of the main settings JSON; clearing all settings via the settings dialog does NOT clear per-thread model overrides (frontend/src/core/settings/local.ts:20,67-91)
- The `storage` event listener only fires for changes made in OTHER tabs — settings changed in the current tab are propagated via the `emitChange()` subscriber pattern, not the storage event (frontend/src/core/settings/store.ts:64-91)
- `updateThreadSettings()` has special handling for `context.model_name` — when the key is `"context"` and the value contains `model_name`, it also saves the model name to the per-thread key; other context changes do not trigger this side effect (frontend/src/core/settings/store.ts:127-149)
- The `SettingsDialog` resets `activeSection` to `defaultSection` when `open` transitions to `true` — if a caller passes a `defaultSection` that differs from the current section, the dialog jumps on open (frontend/src/components/workspace/settings/settings-dialog.tsx:50-56)

## Architecture

- External store pattern: `store.ts` implements a pub/sub store with `subscribe()`, `getBaseSettingsSnapshot()`, and `getThreadModelSnapshot()` — React components consume it via `useSyncExternalStore` in `hooks.ts` (frontend/src/core/settings/store.ts:93-116)
- Cross-tab synchronization: the store listens for the browser's `storage` event and handles three cases — `event.key === null` (clear all), `event.key === LOCAL_SETTINGS_KEY` (settings changed), and `event.key.startsWith(THREAD_MODEL_KEY_PREFIX)` (thread model changed) (frontend/src/core/settings/store.ts:64-91)
- Default merging: `getLocalSettings()` reads raw JSON from localStorage and merges it with `DEFAULT_LOCAL_SETTINGS` via `mergeLocalSettings()` — this ensures new settings keys added in updates get default values even for users with old stored data (frontend/src/core/settings/local.ts:49-65,109-121)
- Thread model override layering: `useThreadSettings()` reads both base settings and the per-thread model name, then applies the override via `applyThreadModelOverride()` — the thread model name takes precedence over the global model setting (frontend/src/core/settings/hooks.ts:31-59)
- Settings dialog sections: the dialog uses a tabbed interface with 7 sections (`account`, `appearance`, `memory`, `tools`, `skills`, `notification`, `about`) — each section is a separate page component, and the dialog manages which section is active (frontend/src/components/workspace/settings/settings-dialog.tsx:31-38)

## Patterns

- Lazy initialization: `ensureBaseSettingsLoaded()` and `ensureStorageListenerRegistered()` are called on first `subscribe()` or `getBaseSettingsSnapshot()` — settings are not read from localStorage until a component actually subscribes (frontend/src/core/settings/store.ts:32-48)
- Sectioned settings merging: `mergeSettingsSection()` merges a partial section into the full settings object using spread syntax — this allows updating one section (e.g., `notification`) without affecting others (frontend/src/core/settings/store.ts:50-62)
- Settings setter as typed callback: `LocalSettingsSetter` is typed as `<K extends keyof LocalSettings>(key: K, value: Partial<LocalSettings[K]>) => void` — this ensures type-safe partial updates to specific settings sections (frontend/src/core/settings/store.ts:14-17)
- Thread model name caching: `threadModelNames` is a module-level `Map<string, string | undefined>` that caches per-thread model names — it's populated lazily on first access and invalidated by storage events (frontend/src/core/settings/store.ts:20,108-116)

## Dependencies

- `react` — `useSyncExternalStore`, `useCallback`, `useMemo` for store integration (frontend/src/core/settings/hooks.ts:1)
- `@/core/threads` — `AgentThreadContext` type for context settings shape (frontend/src/core/settings/local.ts:2)
- `@/core/messages/usage-model` — `TokenUsageInlineMode` type for token usage display settings (frontend/src/core/settings/local.ts:1)
- `@/core/i18n/hooks` — `useI18n()` for settings dialog labels (frontend/src/components/workspace/settings/settings-dialog.tsx:28)
- `lucide-react` — icons for settings section tabs (frontend/src/components/workspace/settings/settings-dialog.tsx:3-11)
- `@/components/ui/dialog` — `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle` for settings modal (frontend/src/components/workspace/settings/settings-dialog.tsx:14-19)
