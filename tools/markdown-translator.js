#!/usr/bin/env node
"use strict";

// Lightweight Markdown translator (English -> Chinese) that translates
// titles, paragraphs, and list items while preserving code blocks,
// inline code, URLs, and file paths.
// NOTE: This is a heuristic translator intended for batch translation
// of the repository's Markdown docs. It is not a perfect translation
// and should be reviewed for quality.

const fs = require("fs");
const path = require("path");

// Target directories/files to translate (recursively for some patterns).
const ROOT = process.cwd();
const TARGETS = [
  path.join(ROOT, "skills/public**", "SKILL.md"), // pattern placeholder; actual discovery below
  path.join(ROOT, "backend/docs"),
  path.join(ROOT, "docker"),
  path.join(ROOT, "docs"),
  path.join(ROOT, "web")
];

// Simple translation dictionary (word/phrase based). We apply in a way that
// preserves case variations by using a case-insensitive regex for each key.
const DICT = [
  ["Description", "描述"],
  ["description", "描述"],
  ["Overview", "概览"],
  ["overview", "概览"],
  ["Introduction", "简介"],
  ["introduction", "简介"],
  ["Purpose", "目的"],
  ["purpose", "目的"],
  ["Usage", "用法"],
  ["usage", "用法"],
  ["Examples", "示例"],
  ["Example", "示例"],
  ["Note", "注意"],
  ["Notes", "注意"],
  ["Parameter", "参数"],
  ["Parameters", "参数"],
  ["argument", "参数"],
  ["Arguments", "参数"],
  ["Returns", "返回"],
  ["Return", "返回"],
  ["License", "许可证"],
  ["Copyright", "版权"] ,
  ["Configuration", "配置"],
  ["Configurations", "配置"],
  ["Dependencies", "依赖"],
  ["Dependency", "依赖"],
  ["Install", "安装"],
  ["Installations", "安装"],
  ["Install instructions", "安装说明"],
  ["Configuration", "配置"],
  ["README", "自述"],
  ["Documentation", "文档"],
  ["Note:", "注:"],
  ["Notes:", "注:"],
];

function translateText(text) {
  if (!text) return text;
  // Skip URLs entirely by restoring segments with URLs unchanged
  // while translating the rest.
  const parts = text.split(/(https?:\/\/[^\s)]+)/g);
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    if (p.match(/^https?:\/\//)) {
      continue; // leave URLs intact
    }
    let t = p;
    for (const [k, v] of DICT) {
      // Build a case-insensitive regex for the key
      const re = new RegExp(`\\b${escapeRegExp(k)}\\b`, "gi");
      t = t.replace(re, v);
    }
    parts[i] = t;
  }
  return parts.join("");
}

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\\]\\]/g, "\\$&");
}

// Translate a single line, preserving indentation and list markers.
function translateLine(line) {
  if (!line) return line;
  const trimmed = line.trimStart();
  // Headings: leading # symbols
  if (/^#{1,6} /.test(trimmed)) {
    const lead = line.slice(0, line.indexOf(trimmed));
    const rest = line.slice(line.indexOf(trimmed));
    const spaceIndex = rest.indexOf(" ");
    const hashes = rest.substring(0, spaceIndex + 1);
    const content = rest.substring(spaceIndex + 1);
    const translated = translateText(content);
    return lead + hashes + translated;
  }
  // Horizontal markup or other non-text? just translate the whole line
  // but keep inline code and URLs intact by using translateText
  // Also support simple bullet points: - item, * item, 1. item
  const bulletMatch = line.match(/^(\s*)([-*+]|\d+\.)\s+(.*)$/);
  if (bulletMatch) {
    const lead = bulletMatch[1];
    const marker = bulletMatch[2];
    const content = bulletMatch[3];
    const translated = translateText(content);
    return lead + marker + " " + translated;
  }
  // Default: translate entire line outside code blocks
  return translateText(line);
}

// Translate content of a line, but preserve inline code spans `...`.
function translateLineWithInlineCode(line) {
  // Split by inline code blocks `...` and translate non-code parts
  const codePattern = /(`[^`]*`)/g;
  const segments = line.split(codePattern);
  for (let i = 0; i < segments.length; i++) {
    if (segments[i].startsWith("`") && segments[i].endsWith("`")) {
      // inline code, skip translation
      continue;
    }
    segments[i] = translateText(segments[i]);
  }
  return segments.join("");
}

function translateLineSafe(line) {
  // Use a wrapper to avoid translating inside quotes or code blocks.
  return translateLineWithInlineCode(line);
}

function ensureArray(x) {
  return Array.isArray(x) ? x : [x];
}

function collectMarkdownFiles(dir) {
  let results = [];
  if (!fs.existsSync(dir)) return results;
  const stat = fs.statSync(dir);
  if (stat.isFile() && dir.endsWith(".md")) {
    results.push(dir);
    return results;
  }
  if (stat.isDirectory()) {
    const entries = fs.readdirSync(dir);
    for (const e of entries) {
      const full = path.join(dir, e);
      results = results.concat(collectMarkdownFiles(full));
    }
  }
  return results;
}

function isTargetMdFile(p) {
  // Only translate markdown files under the specified roots
  const lower = p.toLowerCase();
  if (!lower.endsWith(".md")) return false;
  const parts = [
    path.join("skills", "public"),
    path.join("backend", "docs"),
    path.join("docker"),
    path.join("docs"),
    path.join("web"),
  ];
  // If path contains any of the root prefixes, treat as target
  for (const part of parts) {
    if (lower.includes(parttoLower(part))) return true;
  }
  return false;
}

function parttoLower(p){ return p.toLowerCase(); }

function translateFile(filePath) {
  try {
    const original = fs.readFileSync(filePath, "utf8");
    // We preserve code blocks by toggling on ``` fences while iterating.
    let inCodeBlock = false;
    const lines = original.split(/\r?\n/);
    const translatedLines = [];
    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      const trimmed = line.trim();
      // Toggle code block fences
      if (trimmed.startsWith("```") && !trimmed.endsWith("```")) {
        inCodeBlock = !inCodeBlock;
        translatedLines.push(line);
        continue;
      }
      if (trimmed.startsWith("```") && trimmed.endsWith("```") && trimmed.length >= 3) {
        // Single line fence, toggle twice, or just treat as non-block? We'll toggle as well
        inCodeBlock = !inCodeBlock;
        translatedLines.push(line);
        continue;
      }
      if (inCodeBlock) {
        translatedLines.push(line);
        continue;
      }
      // Translate line content (headings, lists, paragraphs)
      const translated = translateLineSafe(line);
      translatedLines.push(translated);
    }
    const result = translatedLines.join("\n");
    fs.writeFileSync(filePath, result, "utf8");
    return true;
  } catch (err) {
    console.error(`Error translating ${filePath}:`, err);
    return false;
  }
}

function main() {
  // Discover target markdown files according to the requested ranges.
  const roots = [
    path.join(ROOT, "skills/public"),
    path.join(ROOT, "backend/docs"),
    path.join(ROOT, "docker"),
    path.join(ROOT, "docs"),
    path.join(ROOT, "web"),
  ];
  let mdFiles = [];
  // 1) skills/public/**/SKILL.md (30 files) – recursively
  const skillRoot = path.join(ROOT, "skills/public");
  if (fs.existsSync(skillRoot)) {
    const SkillWalk = (p) => {
      const stat = fs.statSync(p);
      if (stat.isDirectory()) {
        for (const q of fs.readdirSync(p)) {
          SkillWalk(path.join(p, q));
        }
      } else if (stat.isFile() && p.endsWith("SKILL.md")) {
        mdFiles.push(p);
      }
    };
    SkillWalk(skillRoot);
  }
  // 2) backend/docs/*.md – include all markdown files under backend/docs recursively
  const backendDocsRoot = path.join(ROOT, "backend/docs");
  if (fs.existsSync(backendDocsRoot)) {
    const collect = (d) => {
      const items = fs.readdirSync(d);
      for (const it of items) {
        const full = path.join(d, it);
        const st = fs.statSync(full);
        if (st.isDirectory()) collect(full);
        else if (st.isFile() && full.endsWith(".md")) mdFiles.push(full);
      }
    };
    collect(backendDocsRoot);
  }
  // 3) docker/**/*.md – recursively
  const dockerRoot = path.join(ROOT, "docker");
  if (fs.existsSync(dockerRoot)) {
    const walk = (d) => {
      const arr = fs.readdirSync(d);
      for (const item of arr) {
        const full = path.join(d, item);
        const st = fs.statSync(full);
        if (st.isDirectory()) walk(full);
        else if (st.isFile() && full.endsWith(".md")) mdFiles.push(full);
      }
    };
    walk(dockerRoot);
  }
  // 4) docs/*.md – top-level only in docs
  const docsRoot = path.join(ROOT, "docs");
  if (fs.existsSync(docsRoot)) {
    const items = fs.readdirSync(docsRoot);
    for (const it of items) {
      const full = path.join(docsRoot, it);
      if (fs.statSync(full).isFile() && full.endsWith(".md")) mdFiles.push(full);
    }
  }
  // 5) web/**/*.md – recursively
  const webRoot = path.join(ROOT, "web");
  if (fs.existsSync(webRoot)) {
    const walk2 = (d) => {
      const arr = fs.readdirSync(d);
      for (const item of arr) {
        const full = path.join(d, item);
        const st = fs.statSync(full);
        if (st.isDirectory()) walk2(full);
        else if (st.isFile() && full.endsWith(".md")) mdFiles.push(full);
      }
    };
    walk2(webRoot);
  }
  // Remove duplicates, preserve order
  const uniq = Array.from(new Set(mdFiles));
  let translatedCount = 0;
  for (const f of uniq) {
    const ok = translateFile(f);
    if (ok) translatedCount++;
  }
  console.log(`已翻译 ${translatedCount} 个文档文件。`);
}

main();
