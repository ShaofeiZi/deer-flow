import { env } from "@/env";

/**
 * 【获取后端（业务服务）Base URL】
 *
 * 优先读取环境变量 `NEXT_PUBLIC_BACKEND_BASE_URL`：
 * - 配置存在：直接返回配置值。
 * - 未配置：返回空字符串，表示使用默认的相对路径/代理（由部署环境决定）。
 *
 * @returns 【后端 Base URL】可能为空字符串。
 */
export function getBackendBaseURL() {
  if (env.NEXT_PUBLIC_BACKEND_BASE_URL) {
    return env.NEXT_PUBLIC_BACKEND_BASE_URL;
  } else {
    return "";
  }
}

/**
 * 【获取 LangGraph Base URL】
 *
 * 说明：LangGraph SDK 通常要求传入“完整 URL”。本方法的回退策略为：
 * - 若配置了 `NEXT_PUBLIC_LANGGRAPH_BASE_URL`：直接使用该值。
 * - 否则在浏览器端：基于 `window.location.origin` 构造 `/api/langgraph`（便于走同源代理）。
 * - SSR 场景下：提供本地开发的兜底 URL，避免构建期/服务端渲染时报错。
 *
 * @returns 【LangGraph Base URL】用于初始化 LangGraph SDK Client。
 */
export function getLangGraphBaseURL() {
  if (env.NEXT_PUBLIC_LANGGRAPH_BASE_URL) {
    return env.NEXT_PUBLIC_LANGGRAPH_BASE_URL;
  } else {
    // LangGraph SDK requires a full URL, construct it from current origin
    if (typeof window !== "undefined") {
      return `${window.location.origin}/api/langgraph`;
    }
    // Fallback for SSR
    return "http://localhost:2026/api/langgraph";
  }
}
