import * as React from "react"

import { cn } from "@/lib/utils"

/**
 * 【组件功能描述】
 * 卡片容器组件。
 *
 * - 提供统一的背景/边框/圆角/阴影与内边距
 * - 通常与 CardHeader/CardContent/CardFooter 等子组件组合使用
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 卡片容器 JSX
 */
function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card"
      className={cn(
        "bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 卡片头部区域。
 *
 * - 用于放置标题/描述/操作区
 * - 内置 grid 布局，支持存在 `card-action` 时的两列排版
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 卡片头部 JSX
 */
function CardHeader({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-header"
      className={cn(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 卡片标题。
 *
 * - 通常放置在 CardHeader 内
 * - 默认加粗并去除行高干扰
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 标题 JSX
 */
function CardTitle({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-title"
      className={cn("leading-none font-semibold", className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 卡片描述文本。
 *
 * - 通常用于标题下方的辅助说明
 * - 默认使用 muted 前景色与较小字号
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 描述 JSX
 */
function CardDescription({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-description"
      className={cn("text-muted-foreground text-sm", className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 卡片操作区。
 *
 * - 通常放置在 CardHeader 内，用于右上角按钮/菜单等
 * - 通过 grid 定位到右侧并跨两行
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 操作区 JSX
 */
function CardAction({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-action"
      className={cn(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 卡片内容区。
 *
 * - 用于承载卡片主体内容
 * - 默认左右内边距与卡片整体保持一致
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 内容区 JSX
 */
function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-content"
      className={cn("px-6", className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 卡片底部区域。
 *
 * - 常用于放置操作按钮、统计信息等
 * - 当存在 border-t 样式时自动增加顶部内边距
 *
 * @param props - 原生 div 属性
 * @param props.className - 额外的 className
 * @returns 底部区域 JSX
 */
function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-footer"
      className={cn("flex items-center px-6 [.border-t]:pt-6", className)}
      {...props}
    />
  )
}

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent,
}
