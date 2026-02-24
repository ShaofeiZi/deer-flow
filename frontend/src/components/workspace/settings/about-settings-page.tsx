"use client";

import { Streamdown } from "streamdown";

import { aboutMarkdown } from "./about-content";

/**
 * 【函数功能描述】
 */
export function AboutSettingsPage() {
  return <Streamdown>{aboutMarkdown}</Streamdown>;
}
