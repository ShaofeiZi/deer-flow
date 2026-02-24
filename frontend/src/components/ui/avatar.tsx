"use client"

import * as React from "react"
import * as AvatarPrimitive from "@radix-ui/react-avatar"

import { cn } from "@/lib/utils"

/**
 * 【组件功能描述】
 * 头像根容器组件。
 *
 * - 基于 Radix Avatar 的 Root 封装
 * - 提供默认尺寸/圆角/溢出裁剪等样式
 *
 * @param props - AvatarPrimitive.Root 的原生属性
 * @param props.className - 额外的 className（用于追加/覆盖样式）
 * @returns 头像根容器 JSX
 */
function Avatar({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Root>) {
  return (
    <AvatarPrimitive.Root
      data-slot="avatar"
      className={cn(
        "relative flex size-8 shrink-0 overflow-hidden rounded-full",
        className
      )}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 头像图片组件。
 *
 * - 基于 Radix Avatar 的 Image 封装
 * - 负责渲染实际头像图片（通常由 src 提供）
 *
 * @param props - AvatarPrimitive.Image 的原生属性
 * @param props.className - 额外的 className（用于追加/覆盖样式）
 * @returns 头像图片 JSX
 */
function AvatarImage({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Image>) {
  return (
    <AvatarPrimitive.Image
      data-slot="avatar-image"
      className={cn("aspect-square size-full", className)}
      {...props}
    />
  )
}

/**
 * 【组件功能描述】
 * 头像占位/回退组件。
 *
 * - 基于 Radix Avatar 的 Fallback 封装
 * - 当图片加载失败或未提供时显示（如用户首字母/默认图标）
 *
 * @param props - AvatarPrimitive.Fallback 的原生属性
 * @param props.className - 额外的 className（用于追加/覆盖样式）
 * @returns 头像回退占位 JSX
 */
function AvatarFallback({
  className,
  ...props
}: React.ComponentProps<typeof AvatarPrimitive.Fallback>) {
  return (
    <AvatarPrimitive.Fallback
      data-slot="avatar-fallback"
      className={cn(
        "bg-muted flex size-full items-center justify-center rounded-full",
        className
      )}
      {...props}
    />
  )
}

export { Avatar, AvatarImage, AvatarFallback }
