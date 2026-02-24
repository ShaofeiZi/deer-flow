import { FlipDisplay } from "./flip-display";

/**
 * 【函数功能描述】
 */
export function ThreadTitle({
  threadTitle,
}: {
  className?: string;
  threadId: string;
  threadTitle: string;
}) {
  return <FlipDisplay uniqueKey={threadTitle}>{threadTitle}</FlipDisplay>;
}
