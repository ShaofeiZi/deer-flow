import { type BaseMessage } from "@langchain/core/messages";
import type { Thread } from "@langchain/langgraph-sdk";

import type { Todo } from "../todos";

/**
 * 【Agent 线程状态（LangGraph Thread values）】
 *
 * 该结构对应 LangGraph 线程的 `values`：
 * - `messages`：对话消息列表（LangChain BaseMessage）
 * - `title`：线程标题（用于侧边栏展示等）
 * - `artifacts`：关联产物路径/标识
 * - `todos`：可选的待办列表（部分任务/模式下才会产出）
 */
export interface AgentThreadState extends Record<string, unknown> {
  /**
   * 【线程标题】
   */
  title: string;
  /**
   * 【线程消息列表】
   */
  messages: BaseMessage[];
  /**
   * 【产物列表】通常为路径片段/标识符。
   */
  artifacts: string[];
  /**
   * 【待办列表】可选。
   */
  todos?: Todo[];
}

/**
 * 【Agent 线程（Thread<AgentThreadState>）】
 *
 * 在 LangGraph SDK 的 Thread 基础上，用本项目的 AgentThreadState 约束其 values 类型。
 */
export interface AgentThread extends Thread<AgentThreadState> {}

/**
 * 【线程上下文（提交消息时透传给后端）】
 *
 * 用途：作为 LangGraph `context` 发送到后端，用于选择模型、开关思考/计划模式、启用子代理等。
 */
export interface AgentThreadContext extends Record<string, unknown> {
  /**
   * 【线程 ID】
   */
  thread_id: string;
  /**
   * 【模型名称】未选择时可能为 undefined。
   */
  model_name: string | undefined;
  /**
   * 【是否启用 thinking】
   */
  thinking_enabled: boolean;
  /**
   * 【是否为计划模式】
   */
  is_plan_mode: boolean;
  /**
   * 【是否启用子代理】
   */
  subagent_enabled: boolean;
}
