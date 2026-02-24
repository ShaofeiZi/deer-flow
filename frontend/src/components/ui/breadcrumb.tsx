import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { ChevronRight, MoreHorizontal } from "lucide-react"

import { cn } from "@/lib/utils"

/**
 * 【组件功能描述】
 * 面包屑导航容器组件。
 *
 * - 提供语义化的 <nav aria-label="breadcrumb"> 容器
 * - 内部通常搭配 BreadcrumbList / BreadcrumbItem / BreadcrumbLink 等子组件使用
 *
 * @param props - 原生 nav 属性
 * @returns 面包屑导航容器 JSX
 */
function Breadcrumb({ ...props }: React.ComponentProps<"nav">) {
  return <nav aria-label="breadcrumb" data-slot="breadcrumb" {...props} />
}

/**
 * 【组件功能描述】
 * 面包屑列表容器。
 *
 * - 渲染为 <ol>，承载多个 BreadcrumbItem
 * - 内置换行与间距样式，适配长路径
 *
 * @param props - 原生 ol 属性
 * @param props.className - 额外的 className
 * @returns 面包屑列表 JSX
 */
function BreadcrumbList({ className, ...props }: React.ComponentProps<"ol">) {
  return (
    <ol
      data-slot="breadcrumb-list"
      className={cn(
        "text-muted-foreground flex flex-wrap items-center gap-1.5 text-sm break-words sm:gap-2.5",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 面包屑单项容器。
 *
 * - 渲染为 <li>
 * - 通常内部放 BreadcrumbLink / BreadcrumbPage / BreadcrumbSeparator
 *
 * @param props - 原生 li 属性
 * @param props.className - 额外的 className
 * @returns 面包屑项 JSX
 */
function BreadcrumbItem({ className, ...props }: React.ComponentProps<"li">) {
  return (
    <li
      data-slot="breadcrumb-item"
      className={cn("inline-flex items-center gap-1.5", className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 面包屑链接组件。
 *
 * - 默认渲染为 <a>
 * - 支持 `asChild`：通过 Radix Slot 将链接能力/样式透传到子节点（例如 Next.js 的 <Link>）
 *
 * @param props - 组件属性
 * @param props.asChild - 是否使用 Slot 让子元素作为实际渲染节点
 * @param props.className - 额外的 className
 * @returns 面包屑链接 JSX
 */
function BreadcrumbLink({
  asChild,
  className,
  ...props
}: React.ComponentProps<"a"> & {
  asChild?: boolean
}) {
  const Comp = asChild ? Slot : "a"

  return (
    <Comp
      data-slot="breadcrumb-link"
      className={cn("hover:text-foreground transition-colors", className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 面包屑当前页（不可点击）展示。
 *
 * - 渲染为 <span>
 * - 自动设置 aria-current="page"，用于无障碍标识当前所在位置
 *
 * @param props - 原生 span 属性
 * @param props.className - 额外的 className
 * @returns 当前页展示 JSX
 */
function BreadcrumbPage({ className, ...props }: React.ComponentProps<"span">) {
  return (
    <span
      data-slot="breadcrumb-page"
      role="link"
      aria-disabled="true"
      aria-current="page"
      className={cn("text-foreground font-normal", className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 面包屑分隔符。
 *
 * - 默认使用 ChevronRight 图标
 * - 允许通过 children 自定义分隔符内容
 *
 * @param props - 原生 li 属性
 * @param props.children - 自定义分隔符（不传则使用默认图标）
 * @param props.className - 额外的 className
 * @returns 分隔符 JSX
 */
function BreadcrumbSeparator({
  children,
  className,
  ...props
}: React.ComponentProps<"li">) {
  return (
    <li
      data-slot="breadcrumb-separator"
      role="presentation"
      aria-hidden="true"
      className={cn("[&>svg]:size-3.5", className)}
      {...props}
    >
      {children ?? <ChevronRight />}
    </li>
  )
}

/**
 * 【组件功能描述】
 * 面包屑省略号占位。
 *
 * - 用于路径过长时折叠中间部分的视觉提示
 * - 包含 sr-only 文本，提升无障碍体验
 *
 * @param props - 原生 span 属性
 * @param props.className - 额外的 className
 * @returns 省略号占位 JSX
 */
function BreadcrumbEllipsis({
  className,
  ...props
}: React.ComponentProps<"span">) {
  return (
    <span
      data-slot="breadcrumb-ellipsis"
      role="presentation"
      aria-hidden="true"
      className={cn("flex size-9 items-center justify-center", className)}
      {...props}
    >
      <MoreHorizontal className="size-4" />
      <span className="sr-only">More</span>
    </span>
  )
}

export {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbPage,
  BreadcrumbSeparator,
  BreadcrumbEllipsis,
}
