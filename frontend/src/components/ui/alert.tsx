import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

/**
 * Alert 组件的样式变体集合。
 *
 * - 使用 class-variance-authority(cva) 统一管理不同告警类型的 className 组合
 * - 通过 `variant` 切换默认/危险（destructive）样式
 */
const alertVariants = cva(
  "relative w-full rounded-lg border px-4 py-3 text-sm grid has-[>svg]:grid-cols-[calc(var(--spacing)*4)_1fr] grid-cols-[0_1fr] has-[>svg]:gap-x-3 gap-y-0.5 items-start [&>svg]:size-4 [&>svg]:translate-y-0.5 [&>svg]:text-current",
  {
    variants: {
      variant: {
        default: "bg-card text-card-foreground",
        destructive:
          "text-destructive bg-card [&>svg]:text-current *:data-[slot=alert-description]:text-destructive/90",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

/**
 * 【函数功能描述】
 * 通用告警容器组件。
 *
 * - 作为 Alert 的外层包裹，提供边框/背景/排版等基础样式
 * - 支持通过 `variant` 切换普通提示与危险提示（通常用于错误/高风险操作提醒）
 *
 * @param props - 组件属性
 * @param props.className - 额外的 className（用于追加/覆盖样式）
 * @param props.variant - 告警样式变体：default | destructive
 * @returns 告警容器的 JSX
 */
function Alert({
  className,
  variant,
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof alertVariants>) {
  return (
    <div
      data-slot="alert"
      role="alert"
      className={cn(alertVariants({ variant }), className)}
      {...props}
    />
  )
}

/**
 * 【函数功能描述】
 * 告警标题区域。
 *
 * - 建议放置简短标题（如“错误”“注意”）
 * - 与 AlertDescription 搭配使用时，位于内容的第一行
 *
 * @param props - 原生 div 属性（可传 className 等）
 * @returns 告警标题的 JSX
 */
function AlertTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-title"
      className={cn(
        "col-start-2 line-clamp-1 min-h-4 font-medium tracking-tight",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【函数功能描述】
 * 告警描述/正文区域。
 *
 * - 用于承载较长的说明文本或富文本内容
 * - 内置对段落行高与间距的处理，保证可读性
 *
 * @param props - 原生 div 属性（可传 className 等）
 * @returns 告警描述区域的 JSX
 */
function AlertDescription({
  className,
  ...props
}: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="alert-description"
      className={cn(
        "text-muted-foreground col-start-2 grid justify-items-start gap-1 text-sm [&_p]:leading-relaxed",
        className
      )}
      {...props}
    />
  )
}

export { Alert, AlertTitle, AlertDescription }
