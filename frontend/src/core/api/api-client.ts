"use client";

import { Client as LangGraphClient } from "@langchain/langgraph-sdk/client";

import { getLangGraphBaseURL } from "../config";

/**
 * 【LangGraph API Client 单例缓存】
 *
 * - 由于 SDK Client 的创建成本较高（需要绑定 baseUrl、内部配置等），这里采用模块级单例缓存。
 * - 在同一浏览器会话中多次调用 `getAPIClient()` 会复用同一个实例。
 */
let _singleton: LangGraphClient | null = null;

/**
 * 【获取 LangGraph SDK 客户端】
 *
 * 该方法会按需（lazy）创建并缓存 `LangGraphClient`：
 * - 首次调用：根据当前运行环境配置的 LangGraph Base URL 创建实例。
 * - 后续调用：直接返回已缓存的单例实例。
 *
 * @returns 【LangGraphClient 实例】用于发起对 LangGraph 后端的请求。
 */
export function getAPIClient(): LangGraphClient {
  _singleton ??= new LangGraphClient({
    apiUrl: getLangGraphBaseURL(),
  });
  return _singleton;
}
