import type { BaseMessage } from "@langchain/core/messages";

import type { AgentThread } from "./types";

/**
 * 【生成线程对应的工作区路由路径】
 *
 * @param threadId - 【线程 ID】
 * @returns 【路由路径】例如 `/workspace/chats/<threadId>`。
 */
export function pathOfThread(threadId: string) {
  return `/workspace/chats/${threadId}`;
}

/**
 * 【从消息对象中提取纯文本内容】
 *
 * 消息的 `content` 可能是：
 * - string：直接返回
 * - 数组：从多模态 parts 中寻找 type="text" 的片段并返回其 text
 *
 * @param message - 【LangChain BaseMessage】
 * @returns 【文本内容】若无法提取则返回 null。
 */
export function textOfMessage(message: BaseMessage) {
  if (typeof message.content === "string") {
    return message.content;
  } else if (Array.isArray(message.content)) {
    return message.content.find((part) => part.type === "text" && part.text)
      ?.text as string;
  }
  return null;
}

/**
 * 【获取线程标题】
 *
 * - 若 thread.values 中存在 title 字段：返回该值
 * - 否则：返回 "Untitled"
 *
 * @param thread - 【线程对象】
 * @returns 【标题字符串】
 */
export function titleOfThread(thread: AgentThread) {
  if (thread.values && "title" in thread.values) {
    return thread.values.title;
  }
  return "Untitled";
}
