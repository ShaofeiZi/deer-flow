import type { AIMessage, Message } from "@langchain/langgraph-sdk";

interface GenericMessageGroup<T = string> {
  type: T;
  id: string | undefined;
  messages: Message[];
}

interface HumanMessageGroup extends GenericMessageGroup<"human"> {}

interface AssistantProcessingGroup extends GenericMessageGroup<"assistant:processing"> {}

interface AssistantMessageGroup extends GenericMessageGroup<"assistant"> {}

interface AssistantPresentFilesGroup extends GenericMessageGroup<"assistant:present-files"> {}

interface AssistantClarificationGroup extends GenericMessageGroup<"assistant:clarification"> {}

interface AssistantSubagentGroup extends GenericMessageGroup<"assistant:subagent"> {}

export type MessageGroup =
  | HumanMessageGroup
  | AssistantProcessingGroup
  | AssistantMessageGroup
  | AssistantPresentFilesGroup
  | AssistantClarificationGroup
  | AssistantSubagentGroup;

const HIDDEN_CONTROL_MESSAGE_NAMES = new Set([
  "summary",
  "loop_warning",
  "todo_reminder",
  "todo_completion_reminder",
]);

export function getMessageGroups(messages: Message[]): MessageGroup[] {
  if (messages.length === 0) {
    return [];
  }

  const groups: MessageGroup[] = [];

  // Returns the last group if it can still accept tool messages
  // (i.e. it's an in-flight processing group, not a terminal human/assistant group).
  // 返回最后一个组，如果它仍然可以接受工具消息
  // （即它是一个进行中的处理组，而不是终端的人类/助手组）。
  function lastOpenGroup() {
    const last = groups[groups.length - 1];
    if (
      last &&
      last.type !== "human" &&
      last.type !== "assistant" &&
      last.type !== "assistant:clarification"
    ) {
      return last;
    }
    return null;
  }

  for (const message of messages) {
    if (isHiddenFromUIMessage(message)) {
      continue;
    }

    if (message.type === "human") {
      groups.push({ id: message.id, type: "human", messages: [message] });
      continue;
    }

    if (message.type === "tool") {
      if (isClarificationToolMessage(message)) {
        // Add to the preceding processing group to preserve tool-call association,
        // then also open a standalone clarification group for prominent display.
        // 添加到前面的处理组以保留工具调用关联，然后也打开一个独立的澄清组以突出显示。
        lastOpenGroup()?.messages.push(message);
        groups.push({
          id: message.id,
          type: "assistant:clarification",
          messages: [message],
        });
      } else {
        const open = lastOpenGroup();
        if (open) {
          open.messages.push(message);
        } else {
          console.error(
            "Unexpected tool message outside a processing group",
            message,
          );
        }
      }
      continue;
    }

    if (message.type === "ai") {
      if (hasPresentFiles(message)) {
        groups.push({
          id: message.id,
          type: "assistant:present-files",
          messages: [message],
        });
      } else if (hasSubagent(message)) {
        groups.push({
          id: message.id,
          type: "assistant:subagent",
          messages: [message],
        });
      } else if (hasReasoning(message) || hasToolCalls(message)) {
        const lastGroup = groups[groups.length - 1];
        // Accumulate consecutive intermediate AI messages into one processing group.
        // 将连续的中间 AI 消息累积到一个处理组中。
        if (lastGroup?.type !== "assistant:processing") {
          groups.push({
            id: message.id,
            type: "assistant:processing",
            messages: [message],
          });
        } else {
          lastGroup.messages.push(message);
        }
      }

      // Not an else-if: a message with reasoning + content (but no tool calls) goes
      // into the processing group above AND gets its own assistant bubble here.
      // 不是 else-if：带有推理 + 内容（但没有工具调用）的消息既进入上面的处理组，也在此处获得自己的助手气泡。
      if (hasContent(message) && !hasToolCalls(message)) {
        groups.push({ id: message.id, type: "assistant", messages: [message] });
      }
    }
  }

  return groups;
}

export function groupMessages<T>(
  messages: Message[],
  mapper: (group: MessageGroup) => T,
): T[] {
  return getMessageGroups(messages)
    .map(mapper)
    .filter((result) => result !== undefined && result !== null) as T[];
}

export function getAssistantTurnUsageMessages(groups: MessageGroup[]) {
  const usageMessagesByGroupIndex: Array<Message[] | null> = Array.from(
    { length: groups.length },
    () => null,
  );

  let turnStartIndex: number | null = null;

  for (const [index, group] of groups.entries()) {
    if (group.type === "human") {
      turnStartIndex = null;
      continue;
    }

    turnStartIndex ??= index;

    const nextGroup = groups[index + 1];
    const isTurnEnd = !nextGroup || nextGroup.type === "human";

    if (!isTurnEnd) {
      continue;
    }

    usageMessagesByGroupIndex[index] = groups
      .slice(turnStartIndex, index + 1)
      .flatMap((currentGroup) => currentGroup.messages)
      .filter((message) => message.type === "ai");

    turnStartIndex = null;
  }

  return usageMessagesByGroupIndex;
}

type MessageMetadataLookup = (
  message: Message,
  index: number,
) => { streamMetadata?: Record<string, unknown> } | undefined;

export type StreamingMessageLookup = {
  ids: ReadonlySet<string>;
  messages: ReadonlySet<Message>;
};

export function getStreamingMessageLookup(
  messages: Message[],
  isStreaming: boolean,
  getMessagesMetadata?: MessageMetadataLookup,
): StreamingMessageLookup {
  const streamingMessageIds = new Set<string>();
  const streamingMessages = new Set<Message>();

  if (!isStreaming) {
    return {
      ids: streamingMessageIds,
      messages: streamingMessages,
    };
  }

  messages.forEach((message, index) => {
    if (!getMessagesMetadata?.(message, index)?.streamMetadata) {
      return;
    }

    if (typeof message.id === "string" && message.id.length > 0) {
      streamingMessageIds.add(message.id);
    }
    streamingMessages.add(message);
  });

  return {
    ids: streamingMessageIds,
    messages: streamingMessages,
  };
}

export function isAssistantMessageGroupStreaming(
  groupMessages: Message[],
  streamingMessages: StreamingMessageLookup,
) {
  return groupMessages.some((message) => {
    if (message.type !== "ai") {
      return false;
    }

    return (
      (typeof message.id === "string" &&
        message.id.length > 0 &&
        streamingMessages.ids.has(message.id)) ||
      streamingMessages.messages.has(message)
    );
  });
}

export function getAssistantTurnCopyData(
  messages: Message[],
  { isStreaming = false }: { isStreaming?: boolean } = {},
) {
  if (isStreaming) {
    return null;
  }

  return (
    [...messages]
      .reverse()
      .filter((message) => message.type === "ai")
      .map((message) => {
        const content = extractContentFromMessage(message);
        return content ?? extractReasoningContentFromMessage(message) ?? "";
      })
      .find((content) => content.length > 0) ?? null
  );
}

export function extractTextFromMessage(message: Message) {
  if (typeof message.content === "string") {
    return (
      splitInlineReasoningFromAIMessage(message)?.content ??
      message.content.trim()
    );
  }
  if (Array.isArray(message.content)) {
    return message.content
      .map((content) => (content.type === "text" ? content.text : ""))
      .join("\n")
      .trim();
  }
  return "";
}

const THINK_OPEN_TAG = "<think>";
const THINK_TAG_RE = /<think>\s*([\s\S]*?)\s*<\/think>/g;

function splitInlineReasoning(content: string) {
  const reasoningParts: string[] = [];

  // First pass: strip every fully closed ` thinking... response` pair and
  // collect its body as reasoning.
  // 第一遍：剥离每个完全闭合的 ` thinking... response` 对，并将其主体收集为推理。
  let cleaned = content.replace(THINK_TAG_RE, (_, reasoning: string) => {
    const normalized = reasoning.trim();
    if (normalized) {
      reasoningParts.push(normalized);
    }
    return "";
  });

  // Streaming-safe pass: a ` thinking` opener whose ` response` has not arrived
  // yet means the rest of the chunk is reasoning in flight. Route it into the
  // reasoning slot instead of letting it render as message content (the
  // raw-HTML markdown pipeline would otherwise paint the inner text on
  // screen until the closing tag lands).
  //
  // Skip when the opener sits right after a backtick — that is the model
  // talking about ` thinking` literally inside markdown inline code, not
  // actually streaming reasoning.
  // 流式安全处理：` thinking` 开始标签出现但 ` response` 尚未到达时，
  // 意味着剩余部分是在传输中的推理内容。将其路由到推理槽中，而不是让其作为消息内容渲染
  // （否则 raw-HTML markdown 管道会在闭合标签到达之前将内部文本绘制到屏幕上）。
  //
  // 当开始标签紧跟在反引号之后时跳过——这是模型在 markdown 行内代码中字面讨论 ` thinking`，
  // 而不是实际流式传输推理。
  const openTagIndex = cleaned.indexOf(THINK_OPEN_TAG);
  if (openTagIndex !== -1 && cleaned[openTagIndex - 1] !== "`") {
    const tail = cleaned.slice(openTagIndex + THINK_OPEN_TAG.length).trim();
    if (tail) {
      reasoningParts.push(tail);
    }
    cleaned = cleaned.slice(0, openTagIndex);
  }

  return {
    content: cleaned.trim(),
    reasoning: reasoningParts.length > 0 ? reasoningParts.join("\n\n") : null,
  };
}

function splitInlineReasoningFromAIMessage(message: Message) {
  if (message.type !== "ai" || typeof message.content !== "string") {
    return null;
  }
  return splitInlineReasoning(message.content);
}

export function extractContentFromMessage(message: Message) {
  if (typeof message.content === "string") {
    return (
      splitInlineReasoningFromAIMessage(message)?.content ??
      message.content.trim()
    );
  }
  if (Array.isArray(message.content)) {
    return message.content
      .map((content) => {
        switch (content.type) {
          case "text":
            return content.text;
          case "image_url":
            const imageURL = extractURLFromImageURLContent(content.image_url);
            return `![image](${imageURL})`;
          default:
            return "";
        }
      })
      .join("\n")
      .trim();
  }
  return "";
}

export function extractReasoningContentFromMessage(message: Message) {
  if (message.type !== "ai") {
    return null;
  }
  if (
    message.additional_kwargs &&
    "reasoning_content" in message.additional_kwargs
  ) {
    return message.additional_kwargs.reasoning_content as string | null;
  }
  if (Array.isArray(message.content)) {
    const part = message.content[0];
    if (part && typeof part === "object" && "thinking" in part) {
      return part.thinking as string;
    }
  }
  if (typeof message.content === "string") {
    return splitInlineReasoning(message.content).reasoning;
  }
  return null;
}

export function removeReasoningContentFromMessage(message: Message) {
  if (message.type !== "ai" || !message.additional_kwargs) {
    return;
  }
  delete message.additional_kwargs.reasoning_content;
}

export function extractURLFromImageURLContent(
  content:
    | string
    | {
        url: string;
      },
) {
  if (typeof content === "string") {
    return content;
  }
  return content.url;
}

export function hasContent(message: Message) {
  if (typeof message.content === "string") {
    return (
      (
        splitInlineReasoningFromAIMessage(message)?.content ??
        message.content.trim()
      ).length > 0
    );
  }
  if (Array.isArray(message.content)) {
    return message.content.length > 0;
  }
  return false;
}

export function hasReasoning(message: Message) {
  if (message.type !== "ai") {
    return false;
  }
  if (typeof message.additional_kwargs?.reasoning_content === "string") {
    return true;
  }
  if (Array.isArray(message.content)) {
    const part = message.content[0];
    // Compatible with the Anthropic gateway
    // 兼容 Anthropic 网关
    return (part as unknown as { type: "thinking" })?.type === "thinking";
  }
  if (typeof message.content === "string") {
    return splitInlineReasoning(message.content).reasoning !== null;
  }
  return false;
}

export function hasToolCalls(message: Message) {
  return (
    message.type === "ai" && message.tool_calls && message.tool_calls.length > 0
  );
}

export function hasPresentFiles(message: Message) {
  return (
    message.type === "ai" &&
    message.tool_calls?.some((toolCall) => toolCall.name === "present_files")
  );
}

export function isClarificationToolMessage(message: Message) {
  return message.type === "tool" && message.name === "ask_clarification";
}

export function extractPresentFilesFromMessage(message: Message) {
  if (message.type !== "ai" || !hasPresentFiles(message)) {
    return [];
  }
  const files: string[] = [];
  for (const toolCall of message.tool_calls ?? []) {
    if (
      toolCall.name === "present_files" &&
      Array.isArray(toolCall.args.filepaths)
    ) {
      files.push(...(toolCall.args.filepaths as string[]));
    }
  }
  return files;
}

export function hasSubagent(message: AIMessage) {
  for (const toolCall of message.tool_calls ?? []) {
    if (toolCall.name === "task") {
      return true;
    }
  }
  return false;
}

export function findToolCallResult(toolCallId: string, messages: Message[]) {
  for (const message of messages) {
    if (message.type === "tool" && message.tool_call_id === toolCallId) {
      const content = extractTextFromMessage(message);
      if (content) {
        return content;
      }
    }
  }
  return undefined;
}

export function isHiddenFromUIMessage(message: Message) {
  const content = extractTextFromMessage(message);
  return (
    message.additional_kwargs?.hide_from_ui === true ||
    (typeof message.name === "string" &&
      HIDDEN_CONTROL_MESSAGE_NAMES.has(message.name)) ||
    (message.type === "human" &&
      content.includes("<slash_skill_activation>") &&
      stripUploadedFilesTag(content).length === 0)
  );
}

/**
 * Represents a file stored in message additional_kwargs.files.
 * Used for optimistic UI (uploading state) and structured file metadata.
 * 表示存储在消息 additional_kwargs.files 中的文件。
 * 用于乐观 UI（上传状态）和结构化文件元数据。
 */
export interface FileInMessage {
  filename: string;
  size: number; // bytes | 字节
  path?: string; // virtual path, may not be set during upload | 虚拟路径，上传期间可能未设置
  status?: "uploading" | "uploaded";
}

/**
 * Strip backend-injected human context tags from message content.
 * Kept under its historical name because callers use it for uploaded-file
 * display cleanup.
 * 从消息内容中剥离后端注入的人类上下文标签。
 * 保留其历史名称，因为调用者使用它来清理上传文件的显示。
 */
export function stripUploadedFilesTag(content: string): string {
  return content
    .replace(/<(uploaded_files|slash_skill_activation)>[\s\S]*?<\/\1>/g, "")
    .trim();
}

/**
 * Tag names that backend middlewares wrap around internal payloads before
 * letting them ride along inside LangGraph message ``content``.
 *
 * These markers are *not* user copy — they come from:
 *
 * - ``UploadsMiddleware`` → ``<uploaded_files>``
 * - ``SkillActivationMiddleware`` → ``<slash_skill_activation>``
 * - ``DynamicContextMiddleware`` → ``<system-reminder>`` (carrying
 *   ``<memory>`` / ``<current_date>`` inside)
 * - ``TodoListMiddleware`` / ``LoopDetectionMiddleware`` style reminders
 *   live in ``hide_from_ui`` HumanMessages, but their inner payload uses
 *   the same tag vocabulary.
 *
 * The primary export filter is {@link isHiddenFromUIMessage}. This list is
 * the defence-in-depth strip for any message that — by middleware bug,
 * provider quirk, or merge-conflict regression — slips through without
 * its ``hide_from_ui`` flag set.
 * 后端中间件在将内部负载放入 LangGraph 消息 ``content`` 之前包裹的标签名称。
 *
 * 这些标记 *不是* 用户内容——它们来自：
 *
 * - ``UploadsMiddleware`` → ``<uploaded_files>``
 * - ``SkillActivationMiddleware`` → ``<slash_skill_activation>``
 * - ``DynamicContextMiddleware`` → ``<system-reminder>``（内部携带
 *   ``<memory>`` / ``<current_date>``）
 * - ``TodoListMiddleware`` / ``LoopDetectionMiddleware`` 风格的提醒
 *   存在于 ``hide_from_ui`` HumanMessages 中，但其内部负载使用相同的标签词汇。
 *
 * 主要的导出过滤器是 {@link isHiddenFromUIMessage}。此列表是对任何因中间件 bug、
 * 提供商异常或合并冲突回归而未被设置 ``hide_from_ui`` 标志的消息的纵深防御剥离。
 */
export const INTERNAL_MARKER_TAGS = [
  "uploaded_files",
  "slash_skill_activation",
  "system-reminder",
  "memory",
  "current_date",
] as const;

const INTERNAL_MARKER_RE = new RegExp(
  `<(${INTERNAL_MARKER_TAGS.join("|")})>[\\s\\S]*?</\\1>`,
  "g",
);

/**
 * Strip every known backend-injected marker from message content.
 *
 * Intended for the chat export path where a marker leaking through is a
 * privacy regression. UI render paths should keep using
 * {@link stripUploadedFilesTag} — they receive ``hide_from_ui`` messages
 * via a separate filter and the narrower function avoids stripping content
 * a user might legitimately type into a meta-discussion (e.g. asking the
 * model about its own ``<memory>`` system).
 * 从消息内容中剥离所有已知的后端注入标记。
 *
 * 用于聊天导出路径，标记泄漏会导致隐私回归。UI 渲染路径应继续使用
 * {@link stripUploadedFilesTag}——它们通过单独的过滤器接收 ``hide_from_ui`` 消息，
 * 而较窄的函数避免了剥离用户可能在元讨论中合法输入的内容（例如询问模型关于其自身的 ``<memory>`` 系统）。
 */
export function stripInternalMarkers(content: string): string {
  return content.replace(INTERNAL_MARKER_RE, "").trim();
}

export function parseUploadedFiles(content: string): FileInMessage[] {
  // Match <uploaded_files>...</uploaded_files> tag
  // 匹配 <uploaded_files>...</uploaded_files> 标签
  const uploadedFilesRegex = /<uploaded_files>([\s\S]*?)<\/uploaded_files>/;
  // eslint-disable-next-line @typescript-eslint/prefer-regexp-exec
  const match = content.match(uploadedFilesRegex);

  if (!match) {
    return [];
  }

  const uploadedFilesContent = match[1];

  // Check if it's "No files have been uploaded yet."
  // 检查是否为 "No files have been uploaded yet."
  if (uploadedFilesContent?.includes("No files have been uploaded yet.")) {
    return [];
  }

  // Check if the backend reported no new files were uploaded in this message
  // 检查后端是否报告此消息中没有新文件被上传
  if (uploadedFilesContent?.includes("(empty)")) {
    return [];
  }

  // Parse file list
  // Format: - filename (size)\n  Path: /path/to/file
  // 解析文件列表
  // 格式：- filename (size)\n  Path: /path/to/file
  const fileRegex = /- ([^\n(]+)\s*\(([^)]+)\)\s*\n\s*Path:\s*([^\n]+)/g;
  const files: FileInMessage[] = [];
  let fileMatch;

  while ((fileMatch = fileRegex.exec(uploadedFilesContent ?? "")) !== null) {
    files.push({
      filename: fileMatch[1].trim(),
      size: parseInt(fileMatch[2].trim(), 10) ?? 0,
      path: fileMatch[3].trim(),
    });
  }

  return files;
}
