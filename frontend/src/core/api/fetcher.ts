import { buildLoginUrl } from "@/core/auth/types";

/** HTTP methods that the gateway's CSRFMiddleware checks.
 *  网关 CSRFMiddleware 检查的 HTTP 方法。 */
export type StateChangingMethod = "POST" | "PUT" | "DELETE" | "PATCH";

export const STATE_CHANGING_METHODS: ReadonlySet<StateChangingMethod> = new Set(
  ["POST", "PUT", "DELETE", "PATCH"],
);

/** Mirror of the gateway's ``should_check_csrf`` decision.
 *  镜像网关的 ``should_check_csrf`` 决策。 */
export function isStateChangingMethod(method: string): boolean {
  return (STATE_CHANGING_METHODS as ReadonlySet<string>).has(
    method.toUpperCase(),
  );
}

const CSRF_COOKIE_PREFIX = "csrf_token=";

/**
 * Read the ``csrf_token`` cookie set by the gateway at login.
 *
 * SSR-safe: returns ``null`` when ``document`` is undefined so the same
 * helper can be imported from server components without a guard.
 *
 * Uses `String.split` instead of a regex to side-step ESLint's
 * `prefer-regexp-exec` rule and the cookie value's reliable `; `
 * separator (set by the gateway, not the browser, so format is stable).
 * 读取网关在登录时设置的 ``csrf_token`` cookie。
 *
 * SSR 安全：当 ``document`` 为 undefined 时返回 ``null``，因此同一个辅助函数
 * 可以从服务器组件中导入而无需守卫。
 *
 * 使用 `String.split` 而非正则表达式，以绕过 ESLint 的 `prefer-regexp-exec` 规则，
 * 并利用 cookie 值可靠的 `; ` 分隔符（由网关设置，而非浏览器，因此格式稳定）。
 */
export function readCsrfCookie(): string | null {
  if (typeof document === "undefined") return null;
  for (const pair of document.cookie.split("; ")) {
    if (pair.startsWith(CSRF_COOKIE_PREFIX)) {
      return decodeURIComponent(pair.slice(CSRF_COOKIE_PREFIX.length));
    }
  }
  return null;
}

/**
 * Fetch with credentials and automatic CSRF protection.
 *
 * Two centralized contracts every API call needs:
 *
 * 1. ``credentials: "include"`` so the HttpOnly access_token cookie
 *    accompanies cross-origin SSR-routed requests.
 * 2. ``X-CSRF-Token`` header on state-changing methods (POST/PUT/
 *    DELETE/PATCH), echoed from the ``csrf_token`` cookie. The gateway's
 *    CSRFMiddleware enforces Double Submit Cookie comparison and returns
 *    403 if the header is missing — silently breaking every call site
 *    that uses raw ``fetch()`` instead of this wrapper.
 *
 * Auto-redirects to ``/login`` on 401. Caller-supplied headers are
 * preserved; the helper only ADDS the CSRF header when it isn't already
 * present, so explicit overrides win.
 * 带凭据和自动 CSRF 保护的 fetch。
 *
 * 每个 API 调用需要的两个集中化契约：
 *
 * 1. ``credentials: "include"`` 使 HttpOnly access_token cookie 伴随跨域 SSR 路由的请求。
 * 2. 在状态变更方法（POST/PUT/DELETE/PATCH）上添加 ``X-CSRF-Token`` 头，
 *    从 ``csrf_token`` cookie 中回显。网关的 CSRFMiddleware 强制执行 Double Submit Cookie 比较，
 *    如果缺少该头则返回 403——静默地破坏每个使用原始 ``fetch()`` 而非此包装器的调用点。
 *
 * 在 401 时自动重定向到 ``/login``。调用者提供的 headers 被保留；
 * 辅助函数仅在 CSRF 头尚未存在时添加，因此显式覆盖优先。
 */
export async function fetch(
  input: RequestInfo | string,
  init?: RequestInit,
): Promise<Response> {
  const url = typeof input === "string" ? input : input.url;

  // Inject CSRF for state-changing methods. GET/HEAD/OPTIONS/TRACE skip
  // it to mirror the gateway's ``should_check_csrf`` logic exactly.
  // 为状态变更方法注入 CSRF。GET/HEAD/OPTIONS/TRACE 跳过它以精确镜像网关的 ``should_check_csrf`` 逻辑。
  let headers = init?.headers;
  if (isStateChangingMethod(init?.method ?? "GET")) {
    const token = readCsrfCookie();
    if (token) {
      // Fresh Headers instance so we don't mutate caller-supplied objects.
      // 创建新的 Headers 实例，以免修改调用者提供的对象。
      const merged = new Headers(headers);
      if (!merged.has("X-CSRF-Token")) {
        merged.set("X-CSRF-Token", token);
      }
      headers = merged;
    }
  }

  const res = await globalThis.fetch(url, {
    ...init,
    headers,
    credentials: "include",
  });

  if (res.status === 401) {
    window.location.href = buildLoginUrl(window.location.pathname);
    throw new Error("Unauthorized");
  }

  return res;
}

/**
 * Build headers for CSRF-protected requests.
 *
 * **Prefer :func:`fetchWithAuth`** for new code — it injects the header
 * automatically on state-changing methods. This helper exists for legacy
 * call sites that need to compose headers manually (e.g. inside
 * `next/server` route handlers that build their own ``Headers`` object).
 *
 * Per RFC-001: Double Submit Cookie pattern.
 * 构建 CSRF 保护请求的 headers。
 *
 * **新代码请优先使用 :func:`fetchWithAuth`**——它会在状态变更方法上自动注入头。
 * 此辅助函数为需要手动组合 headers 的旧调用点而存在（例如在构建自己的 ``Headers`` 对象的
 * `next/server` 路由处理器中）。
 *
 * 根据 RFC-001：Double Submit Cookie 模式。
 */
export function getCsrfHeaders(): HeadersInit {
  const token = readCsrfCookie();
  return token ? { "X-CSRF-Token": token } : {};
}
