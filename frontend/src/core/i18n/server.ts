import { cookies } from "next/headers";

/**
 * 【服务端 Locale 类型】
 *
 * 用于 Server Components / Route Handlers 中的语言选择。
 */
export type Locale = "en-US" | "zh-CN";

/**
 * 【服务端检测语言】
 *
 * 当前实现：从请求 cookie 读取 `locale`，若缺失则默认 "en-US"。
 *
 * @returns 【Locale】服务端可用的语言枚举。
 */
export async function detectLocaleServer(): Promise<Locale> {
  const cookieStore = await cookies();
  const locale = cookieStore.get("locale")?.value ?? "en-US";
  return locale as Locale;
}
