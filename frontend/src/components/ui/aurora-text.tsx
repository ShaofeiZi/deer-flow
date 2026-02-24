"use client"

import React, { memo } from "react"

/**
 * AuroraText 组件 Props。
 */
interface AuroraTextProps {
  /** 需要渲染的文本/节点内容（会被应用极光渐变动画效果） */
  children: React.ReactNode
  /** 额外的 className（用于追加/覆盖外层 span 样式） */
  className?: string
  /** 渐变色数组（按顺序拼接为 linear-gradient，并会首尾闭合） */
  colors?: string[]
  /** 动画速度倍率（值越大动画越快；默认 1） */
  speed?: number
}

/**
 * 【组件功能描述】
 * AuroraText（极光文字）组件。
 *
 * - 使用 CSS 线性渐变 + background-clip 实现“彩色文字”效果
 * - 通过 animationDuration 根据 speed 调整动画速度
 * - 包含 sr-only 文本以兼顾可访问性（屏幕阅读器读取实际内容）
 *
 * @param props - 组件属性
 * @param props.children - 需要展示的内容
 * @param props.className - 额外样式
 * @param props.colors - 渐变色数组
 * @param props.speed - 动画速度倍率
 * @returns 渐变动画文字的 JSX
 */
export const AuroraText = memo(
  ({
    children,
    className = "",
    colors = ["#FF0080", "#7928CA", "#0070F3", "#38bdf8"],
    speed = 1,
  }: AuroraTextProps) => {
    /**
     * 【工具函数描述】
     * 渐变动画需要的内联样式。
     *
     * - backgroundImage：根据 colors 生成线性渐变，并在末尾补上 colors[0] 实现闭环过渡
     * - WebkitBackgroundClip/WebkitTextFillColor：让渐变只作用于文字本身
     * - animationDuration：根据 speed 动态计算动画时长（speed 越大，时长越短）
     */
    const gradientStyle = {
      backgroundImage: `linear-gradient(135deg, ${colors.join(", ")}, ${
        colors[0]
      })`,
      WebkitBackgroundClip: "text",
      WebkitTextFillColor: "transparent",
      animationDuration: `${10 / speed}s`,
    }

    return (
      <span className={`relative inline-block ${className}`}>
        <span className="sr-only">{children}</span>
        <span
          className="animate-aurora relative bg-size-[200%_auto] bg-clip-text text-transparent"
          style={gradientStyle}
          aria-hidden="true"
        >
          {children}
        </span>
      </span>
    )
  }
)

AuroraText.displayName = "AuroraText"
