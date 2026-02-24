"use client";

import { useEffect } from "react";

/**
 * 【函数功能描述】
 */
export function Overscroll({
  behavior,
  overflow = "hidden",
}: {
  behavior: "none" | "contain" | "auto";
  overflow?: "hidden" | "auto" | "scroll";
}) {
  useEffect(() => {
    document.documentElement.style.overflow = overflow;
    document.documentElement.style.overscrollBehavior = behavior;
  }, [behavior, overflow]);
  return null;
}
