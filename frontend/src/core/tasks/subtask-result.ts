import type { Subtask } from "./types";

export type SubtaskStatus = Subtask["status"];

export interface SubtaskResultUpdate {
  status: SubtaskStatus;
  result?: string;
  error?: string;
}

/**
 * Structured-status keys the backend stamps onto
 * ``ToolMessage.additional_kwargs`` for every ``task`` tool result.
 *
 * The values mirror the Python contract in
 * ``backend/packages/harness/deerflow/subagents/status_contract.py``
 * (``SUBAGENT_STATUS_KEY`` / ``SUBAGENT_ERROR_KEY``). The cross-language
 * fixture at ``contracts/subagent_status_contract.json`` pins both sides
 * to the same values.
 * 后端在每个 ``task`` 工具结果的 ``ToolMessage.additional_kwargs`` 上标记的结构化状态键。
 *
 * 这些值与 Python 契约相对应，定义在
 * ``backend/packages/harness/deerflow/subagents/status_contract.py``
 * （``SUBAGENT_STATUS_KEY`` / ``SUBAGENT_ERROR_KEY``）。跨语言 fixture
 * ``contracts/subagent_status_contract.json`` 将两端固定为相同的值。
 */
export const SUBAGENT_STATUS_KEY = "subagent_status";
export const SUBAGENT_ERROR_KEY = "subagent_error";

/**
 * Map from the backend ``subagent_status`` value to the frontend
 * {@link SubtaskStatus} enum. The frontend collapses ``cancelled`` /
 * ``timed_out`` / ``polling_timed_out`` into ``failed`` because the
 * subtask card only renders three pill states. The richer backend
 * vocabulary still survives on ``error`` for tooling that wants the
 * detail.
 * 将后端 ``subagent_status`` 值映射到前端 {@link SubtaskStatus} 枚举。
 * 前端将 ``cancelled`` / ``timed_out`` / ``polling_timed_out`` 合并为 ``failed``，
 * 因为子任务卡片只渲染三种 pill 状态。更丰富的后端词汇仍然通过 ``error`` 保留，
 * 供需要详细信息的工具使用。
 */
const STRUCTURED_STATUS_TO_SUBTASK: Record<string, SubtaskStatus> = {
  completed: "completed",
  failed: "failed",
  cancelled: "failed",
  timed_out: "failed",
  polling_timed_out: "failed",
};

/**
 * Prefix strings the backend `task` tool writes into its result `content`.
 *
 * These values are not user-facing copy — they are part of the
 * backend↔frontend contract defined in
 * `backend/packages/harness/deerflow/tools/builtins/task_tool.py` (returned
 * from the tool body) and in
 * `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
 * (wrapper for tool exceptions). Any change here must be paired with the
 * matching backend change. Exported so a future structured-status migration
 * can reference the same values from one place.
 *
 * `task_tool.py` also emits three `Error:` strings for pre-execution failures
 * — unknown subagent type, host-bash disabled, and "task disappeared from
 * background tasks". They are handled by {@link ERROR_WRAPPER_PATTERN}
 * rather than dedicated prefixes because the wrapper already produces
 * exactly the right `terminal failed` shape.
 * 后端 `task` 工具写入其结果 `content` 的前缀字符串。
 *
 * 这些值不是面向用户的文案——它们是后端↔前端契约的一部分，定义在
 * `backend/packages/harness/deerflow/tools/builtins/task_tool.py`（从工具体返回）和
 * `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
 * （工具异常的包装器）中。此处的任何更改都必须与后端更改配对。导出这些值是为了让未来的
 * 结构化状态迁移可以从一个地方引用相同的值。
 *
 * `task_tool.py` 还会为执行前失败发出三种 `Error:` 字符串——未知的子代理类型、
 * host-bash 被禁用以及"任务从后台任务中消失"。它们由 {@link ERROR_WRAPPER_PATTERN}
 * 处理，而不是专用前缀，因为包装器已经产生了正确的 `terminal failed` 形态。
 */
export const SUCCESS_PREFIX = "Task Succeeded. Result:";
export const FAILURE_PREFIX = "Task failed.";
export const TIMEOUT_PREFIX = "Task timed out";
export const CANCELLED_PREFIX = "Task cancelled by user.";
export const POLLING_TIMEOUT_PREFIX = "Task polling timed out";
export const ERROR_WRAPPER_PATTERN = /^Error\b/i;

/**
 * Map a `task` tool result to a {@link SubtaskStatus}.
 *
 * Bytedance/deer-flow issue #3146: prefers the structured
 * ``additional_kwargs.subagent_status`` field the backend now stamps via
 * ``ToolErrorHandlingMiddleware``. Falls back to the legacy prefix
 * matching for messages that pre-date the stamping commit (historical
 * threads, third-party clients, or any tool path that bypasses the
 * middleware). Both shapes converge on the same {@link SubtaskStatus}
 * vocabulary the card UI renders.
 *
 * When the structured field is present, the prefix parser is still run
 * so the success `result` body and the wrapped-error message can be
 * back-filled from `content`. Today the backend only stamps the
 * `subagent_status` enum value — the human-facing payload still lives
 * in `content`, so dropping the prefix parse would regress the subtask
 * card display. Structured fields win on conflict: if `subagent_status`
 * and the text disagree, the text-derived `result`/`error` are
 * discarded so a malformed wrapper can't sneak through.
 *
 * Returning `in_progress` is the **deliberate** fallback for content that
 * matches none of the known prefixes and carries no structured stamp.
 * LangChain only ever emits a `ToolMessage` once the tool itself has
 * returned (success or wrapped exception), so an unknown shape means
 * "the contract changed underneath us" — surfacing it as still-running
 * prompts the operator to investigate, where eagerly marking it
 * terminal-failed would mask the drift.
 * 将 `task` 工具结果映射到 {@link SubtaskStatus}。
 *
 * Bytedance/deer-flow issue #3146：优先使用后端现在通过 ``ToolErrorHandlingMiddleware``
 * 标记的结构化 ``additional_kwargs.subagent_status`` 字段。对于早于标记提交的消息
 * （历史线程、第三方客户端或绕过中间件的任何工具路径），回退到传统的前缀匹配。
 * 两种形态都收敛到卡片 UI 渲染的相同 {@link SubtaskStatus} 词汇。
 *
 * 当结构化字段存在时，前缀解析器仍会运行，以便从 `content` 回填成功的 `result` 主体
 * 和包装的错误消息。目前后端只标记 `subagent_status` 枚举值——面向用户的内容仍然
 * 存在于 `content` 中，因此放弃前缀解析会导致子任务卡片显示退化。结构化字段在冲突时
 * 优先：如果 `subagent_status` 和文本不一致，则丢弃从文本派生的 `result`/`error`，
 * 以防止格式错误的包装器绕过。
 *
 * 返回 `in_progress` 是对不匹配任何已知前缀且没有结构化标记的内容的**有意的**回退。
 * LangChain 只在工具本身返回（成功或包装的异常）后才发出 `ToolMessage`，
 * 因此未知形态意味着"契约在我们之下发生了变化"——将其显示为仍在运行提示操作员进行调查，
 * 而急于将其标记为终端失败则会掩盖这种漂移。
 */
export function parseSubtaskResult(
  text: string,
  additionalKwargs?: Record<string, unknown> | null,
): SubtaskResultUpdate {
  const fromText = parseFromText(text.trim());
  const structured = readStructuredStatus(additionalKwargs);
  if (!structured) {
    return fromText;
  }

  const update: SubtaskResultUpdate = { status: structured.status };
  // Structured `subagent_error` wins; otherwise inherit the text-derived
  // error only when both sides agree on the status (so a "Task Succeeded"
  // body can't bleed into a `failed` structured stamp and vice versa).
  // 结构化的 `subagent_error` 优先；否则仅在双方状态一致时继承从文本派生的错误
  // （这样 "Task Succeeded" 主体不会泄漏到 `failed` 结构化标记中，反之亦然）。
  if (structured.error) {
    update.error = structured.error;
  } else if (
    fromText.status === structured.status &&
    fromText.error !== undefined
  ) {
    update.error = fromText.error;
  }
  // Result body only matters for `completed`; require text agreement so
  // a lying success prefix under a `failed` stamp is dropped.
  // Result 主体仅对 `completed` 有意义；要求文本一致，以便 `failed` 标记下的虚假成功前缀被丢弃。
  if (
    structured.status === "completed" &&
    fromText.status === "completed" &&
    fromText.result !== undefined
  ) {
    update.result = fromText.result;
  }
  return update;
}

function parseFromText(trimmed: string): SubtaskResultUpdate {
  if (trimmed.startsWith(SUCCESS_PREFIX)) {
    return {
      status: "completed",
      result: trimmed.slice(SUCCESS_PREFIX.length).trim(),
    };
  }

  if (trimmed.startsWith(FAILURE_PREFIX)) {
    return {
      status: "failed",
      error: trimmed.slice(FAILURE_PREFIX.length).trim(),
    };
  }

  if (trimmed.startsWith(TIMEOUT_PREFIX)) {
    return { status: "failed", error: trimmed };
  }

  if (trimmed.startsWith(CANCELLED_PREFIX)) {
    return { status: "failed", error: trimmed };
  }

  if (trimmed.startsWith(POLLING_TIMEOUT_PREFIX)) {
    return { status: "failed", error: trimmed };
  }

  // ToolErrorHandlingMiddleware-style wrapper, or any other terminal error
  // signal the backend forwards to the lead agent.
  // ToolErrorHandlingMiddleware 风格的包装器，或后端转发给主代理的任何其他终端错误信号。
  if (ERROR_WRAPPER_PATTERN.test(trimmed)) {
    return { status: "failed", error: trimmed };
  }

  return { status: "in_progress" };
}

interface StructuredStatus {
  status: SubtaskStatus;
  error?: string;
}

function readStructuredStatus(
  additionalKwargs: Record<string, unknown> | null | undefined,
): StructuredStatus | null {
  if (!additionalKwargs) return null;
  const rawStatus = additionalKwargs[SUBAGENT_STATUS_KEY];
  if (typeof rawStatus !== "string") return null;
  const mapped = STRUCTURED_STATUS_TO_SUBTASK[rawStatus];
  if (mapped === undefined) {
    // Unknown future status value — stay on the legacy prefix fallback
    // so a backend that ships a new enum variant before the frontend
    // upgrades still renders something predictable instead of getting
    // pinned to "in_progress" by an empty branch.
    // 未知的未来状态值——保持在传统前缀回退上，
    // 这样在前端升级之前发布新枚举变体的后端仍然能渲染出可预测的内容，
    // 而不是被空分支固定为 "in_progress"。
    return null;
  }
  const rawError = additionalKwargs[SUBAGENT_ERROR_KEY];
  const result: StructuredStatus = { status: mapped };
  if (typeof rawError === "string" && rawError.trim()) {
    result.error = rawError;
  }
  return result;
}
