import type { Message } from "@langchain/langgraph-sdk";

import {
  extractContentFromMessage,
  extractReasoningContentFromMessage,
  hasContent,
  hasToolCalls,
  isHiddenFromUIMessage,
  stripInternalMarkers,
} from "../messages/utils";

import type { AgentThread } from "./types";
import { titleOfThread } from "./utils";

/**
 * Optional debug switches for advanced exports.
 *
 * Bytedance/deer-flow issue #3107 BUG-006 explicitly prescribes that the
 * default export includes only the user-visible transcript and excludes
 * thinking/reasoning content, tool calls, tool results, hidden messages,
 * memory injection, and `<system-reminder>` payloads. These options let a
 * future "debug export" surface re-include any of those categories without
 * forking the formatter. They are not currently wired to any UI control —
 * callers that want them must construct the options object explicitly.
 * 高级导出的可选调试开关。
 *
 * Bytedance/deer-flow issue #3107 BUG-006 明确规定默认导出仅包含用户可见的对话记录，
 * 并排除思考/推理内容、工具调用、工具结果、隐藏消息、记忆注入和 `<system-reminder>` 负载。
 * 这些选项允许未来的"调试导出"界面重新包含这些类别中的任何一项，而无需 fork 格式化器。
 * 它们目前未连接到任何 UI 控件——需要它们的调用者必须显式构造 options 对象。
 */
export interface ExportOptions {
  includeReasoning?: boolean;
  includeToolCalls?: boolean;
  includeToolMessages?: boolean;
  includeHidden?: boolean;
}

function visibleMessages(
  messages: Message[],
  options: ExportOptions,
): Message[] {
  return messages.filter((message) => {
    if (!options.includeHidden && isHiddenFromUIMessage(message)) {
      return false;
    }
    if (!options.includeToolMessages && message.type === "tool") {
      return false;
    }
    return true;
  });
}

function formatMessageContent(message: Message): string {
  const text = extractContentFromMessage(message);
  if (!text) return "";
  // Defence-in-depth: even if a middleware-injected marker slipped through
  // the `hide_from_ui` filter, scrub every known internal tag before the
  // content lands in a user-visible export file.
  // 纵深防御：即使中间件注入的标记绕过了 `hide_from_ui` 过滤器，
  // 在内容进入用户可见的导出文件之前，清除所有已知的内部标签。
  return stripInternalMarkers(text);
}

function formatToolCalls(message: Message): string {
  if (message.type !== "ai" || !hasToolCalls(message)) return "";
  const calls = message.tool_calls ?? [];
  return calls.map((call) => `- **Tool:** \`${call.name}\``).join("\n");
}

export function formatThreadAsMarkdown(
  thread: AgentThread,
  messages: Message[],
  options: ExportOptions = {},
): string {
  const title = titleOfThread(thread);
  const createdAt = thread.created_at
    ? new Date(thread.created_at).toLocaleString()
    : "Unknown";

  const lines: string[] = [
    `# ${title}`,
    "",
    `*Exported on ${new Date().toLocaleString()} · Created ${createdAt}*`,
    "",
    "---",
    "",
  ];

  for (const message of visibleMessages(messages, options)) {
    if (message.type === "human") {
      const content = formatMessageContent(message);
      if (content) {
        lines.push(`## 🧑 User`, "", content, "", "---", "");
      }
    } else if (message.type === "ai") {
      const reasoning = options.includeReasoning
        ? extractReasoningContentFromMessage(message)
        : undefined;
      const content = formatMessageContent(message);
      const toolCalls = options.includeToolCalls
        ? formatToolCalls(message)
        : "";

      if (!content && !toolCalls && !reasoning) continue;

      lines.push(`## 🤖 Assistant`);

      if (reasoning) {
        lines.push(
          "",
          "<details>",
          "<summary>Thinking</summary>",
          "",
          reasoning,
          "",
          "</details>",
        );
      }

      if (toolCalls) {
        lines.push("", toolCalls);
      }

      if (content && hasContent(message)) {
        lines.push("", content);
      }

      lines.push("", "---", "");
    }
  }

  return lines.join("\n").trimEnd() + "\n";
}

interface JSONExportMessage {
  type: Message["type"];
  id: string | undefined;
  content: string;
  reasoning?: string;
  tool_calls?: unknown;
}

function buildJSONMessage(
  msg: Message,
  options: ExportOptions,
): JSONExportMessage | null {
  // Run the same sanitiser the Markdown path uses so the JSON `content`
  // field never carries inline ` thinking... response` wrappers, content-array
  // thinking blocks, `<uploaded_files>` markers, or other internal payloads.
  // 使用与 Markdown 路径相同的清理器，使 JSON `content` 字段永远不会携带
  // 内联 ` thinking... response` 包装器、content-array 思考块、
  // `<uploaded_files>` 标记或其他内部负载。
  const content = formatMessageContent(msg);
  const reasoning =
    options.includeReasoning && msg.type === "ai"
      ? (extractReasoningContentFromMessage(msg) ?? undefined)
      : undefined;
  const toolCalls =
    options.includeToolCalls &&
    msg.type === "ai" &&
    "tool_calls" in msg &&
    msg.tool_calls?.length
      ? msg.tool_calls
      : undefined;

  // Drop rows with no exportable payload (empty content + no opted-in
  // reasoning / tool_calls). Uses falsy semantics so `reasoning: ""` (the
  // empty string ``extractReasoningContentFromMessage`` can hand back) is
  // treated the same way Markdown's `!reasoning` continue does — otherwise
  // an opted-in but empty reasoning field would leak as `{reasoning: ""}`.
  // 丢弃没有可导出负载的行（空内容 + 没有选择加入的 reasoning / tool_calls）。
  // 使用 falsy 语义，使 `reasoning: ""`（``extractReasoningContentFromMessage`` 可能返回的空字符串）
  // 与 Markdown 的 `!reasoning` continue 处理方式相同——否则一个选择加入但为空的 reasoning 字段
  // 会泄漏为 `{reasoning: ""}`。
  if (!content && !reasoning && !toolCalls) {
    return null;
  }

  return {
    type: msg.type,
    id: msg.id,
    content,
    ...(reasoning !== undefined ? { reasoning } : {}),
    ...(toolCalls !== undefined ? { tool_calls: toolCalls } : {}),
  };
}

export function formatThreadAsJSON(
  thread: AgentThread,
  messages: Message[],
  options: ExportOptions = {},
): string {
  const exportData = {
    title: titleOfThread(thread),
    thread_id: thread.thread_id,
    created_at: thread.created_at,
    exported_at: new Date().toISOString(),
    messages: visibleMessages(messages, options)
      .map((msg) => buildJSONMessage(msg, options))
      .filter((m): m is JSONExportMessage => m !== null),
  };
  return JSON.stringify(exportData, null, 2);
}

function sanitizeFilename(name: string): string {
  return name.replace(/[^\p{L}\p{N}_\- ]/gu, "").trim() || "conversation";
}

export function downloadAsFile(
  content: string,
  filename: string,
  mimeType: string,
) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function exportThreadAsMarkdown(
  thread: AgentThread,
  messages: Message[],
) {
  const markdown = formatThreadAsMarkdown(thread, messages);
  const filename = `${sanitizeFilename(titleOfThread(thread))}.md`;
  downloadAsFile(markdown, filename, "text/markdown;charset=utf-8");
}

export function exportThreadAsJSON(thread: AgentThread, messages: Message[]) {
  const json = formatThreadAsJSON(thread, messages);
  const filename = `${sanitizeFilename(titleOfThread(thread))}.json`;
  downloadAsFile(json, filename, "application/json;charset=utf-8");
}
