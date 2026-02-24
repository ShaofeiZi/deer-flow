/**
 * Cookie utilities for locale management
 * Works on both client and server side
 */

/**
 * 【Locale Cookie 名称】
 *
 * 用于在浏览器 cookie 与服务端请求头中统一读写语言设置。
 */
const LOCALE_COOKIE_NAME = "locale";

/**
 * Get locale from cookie (client-side)
 */
/**
 * 【从 Cookie 读取语言（浏览器端）】
 *
 * 注意：
 * - 仅在 `document` 可用时工作；SSR/构建期会直接返回 null。
 * - 返回值为原始字符串，调用方通常需要再断言/校验为 `Locale`。
 *
 * @returns 【语言字符串】不存在则返回 null。
 */
export function getLocaleFromCookie(): string | null {
  if (typeof document === "undefined") {
    return null;
  }

  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split("=");
    if (name === LOCALE_COOKIE_NAME) {
      return decodeURIComponent(value ?? "");
    }
  }
  return null;
}

/**
 * Set locale in cookie (client-side)
 */
/**
 * 【写入语言到 Cookie（浏览器端）】
 *
 * 使用 1 年过期时间，并设置：
 * - path=/：全站可用
 * - SameSite=Lax：减少跨站请求携带 cookie 的风险
 *
 * @param locale - 【语言字符串】通常为 "zh-CN" / "en-US"。
 */
export function setLocaleInCookie(locale: string): void {
  if (typeof document === "undefined") {
    return;
  }

  // Set cookie with 1 year expiration
  const maxAge = 365 * 24 * 60 * 60; // 1 year in seconds
  document.cookie = `${LOCALE_COOKIE_NAME}=${encodeURIComponent(locale)}; max-age=${maxAge}; path=/; SameSite=Lax`;
}

/**
 * Get locale from cookie (server-side)
 * Use this in server components or API routes
 */
/**
 * 【从 Cookie 读取语言（服务端）】
 *
 * - 通过 `next/headers` 的 `cookies()` 读取请求 cookie。
 * - 若运行环境不支持（例如某些 middleware 场景），会捕获异常并返回 null。
 *
 * @returns 【语言字符串】不存在或不可用时返回 null。
 */
export async function getLocaleFromCookieServer(): Promise<string | null> {
  try {
    const { cookies } = await import("next/headers");
    const cookieStore = await cookies();
    return cookieStore.get(LOCALE_COOKIE_NAME)?.value ?? null;
  } catch {
    // Fallback if cookies() is not available (e.g., in middleware)
    return null;
  }
}
