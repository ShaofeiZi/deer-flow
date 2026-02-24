---
name: podcast-generation
描述: 当用户请求从文本内容生成、创建或制作播客时，请使用本技能。将书面内容转换为双主持人对话式播客音频格式，具有自然的对话风格。
---

# 播客生成技能

## 概览

本技能从文本内容生成高质量播客音频。工作流包括创建结构化 JSON 脚本（对话形式）并通过文本转语音合成执行音频生成。

## 核心能力

- 将任何文本内容（文章、报告、文档）转换为播客脚本
- 生成自然的双主持人对话（男女主持人）
- 使用文本转语音合成语音音频
- 将音频片段混合成最终播客 MP3 文件
- 支持英文和中文内容

## 工作流

### 步骤 1：理解需求

当用户请求播客生成时，确定：

- 源内容：要转换为播客的文本/文章/报告
- 语言：英文或中文（根据内容）
- 输出位置：保存生成播客的位置
- 不需要检查 `/mnt/user-data` 下的文件夹

### 步骤 2：创建结构化脚本 JSON

在 `/mnt/user-data/workspace/` 生成命名模式为 `{描述性名称}-script.json` 的结构化 JSON 脚本文件

JSON 结构：
```json
{
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "对话文本"},
    {"speaker": "female", "paragraph": "对话文本"}
  ]
}
```

### 步骤 3：执行生成

调用 Python 脚本：
```bash
python /mnt/skills/public/podcast-generation/scripts/generate.py \
  --script-file /mnt/user-data/workspace/script-file.json \
  --output-file /mnt/user-data/outputs/generated-podcast.mp3 \
  --transcript-file /mnt/user-data/outputs/generated-podcast-transcript.md
```

参数：

- `--script-file`：JSON 脚本文件的绝对路径（必填）
- `--output-file`：输出 MP3 文件的绝对路径（必填）
- `--transcript-file`：输出文本 Markdown 文件的绝对路径（可选，但推荐）

> [!重要]
> - 在一次完整调用中执行脚本。不要将工作流拆分为单独的步骤。
> - 脚本内部处理所有 TTS API 调用和音频生成。
> - 不要读取 Python 文件，只需使用参数调用它。
> - 始终包含 `--transcript-file` 以生成可读的文字稿供用户参考。

## 脚本 JSON 格式

脚本 JSON 文件必须遵循此结构：

```json
{
  "title": "人工智能的历史",
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "Hello Deer! Welcome back to another episode."},
    {"speaker": "female", "paragraph": "Hey everyone! Today we have an exciting topic to discuss."},
    {"speaker": "male", "paragraph": "That's right! We're going to talk about..."}
  ]
}
```

字段：
- `title`：播客节目标题（可选，用作文字稿中的标题）
- `locale`：语言代码 - "en" 表示英文，"zh" 表示中文
- `lines`：对话行数组
  - `speaker`："male" 或 "female"
  - `paragraph`：该说话者的对话文本

## 脚本编写指南

创建脚本 JSON 时，遵循以下指南：

### 格式要求
- 只有两个主持人：男和女，自然交替
- 目标时长：约 10 分钟对话（约 40-60 行）
- 以男主持人说出包含 "Hello Deer" 的问候语开始

### 语气与风格
- 自然、对话式的对话——像两个朋友聊天
- 使用随意的表达和对话式过渡
- 避免过于正式的语言或学术语气
- 包含反应、追问和自然的感叹词

### 内容指南
- 主持人之间频繁来回对话
- 句子保持简短，口语时易于理解
- 仅纯文本——输出中不要有 Markdown 格式
- 将技术概念翻译成通俗易懂的语言
- 不要数学公式、代码或复杂符号
- 使内容对纯音频听众有吸引力且易于理解
- 排除元信息如日期、作者姓名或文档结构

## 播客生成示例

用户请求："生成一个关于人工智能历史的播客"

步骤 1：创建脚本文件 `/mnt/user-data/workspace/ai-history-script.json`：
```json
{
  "title": "人工智能的历史",
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "Hello Deer! Welcome back to another fascinating episode. Today we're diving into something that's literally shaping our future - the history of artificial intelligence."},
    {"speaker": "female", "paragraph": "Oh, I love this topic! You know, AI feels so modern, but it actually has roots going back over seventy years."},
    {"speaker": "male", "paragraph": "Exactly! It all started back in the 1950s. The term artificial intelligence was actually coined by John McCarthy in 1956 at a famous conference at Dartmouth."},
    {"speaker": "female", "paragraph": "Wait, so they were already thinking about machines that could think back then? That's incredible!"},
    {"speaker": "male", "paragraph": "Right? The early pioneers were so optimistic. They thought we'd have human-level AI within a generation."},
    {"speaker": "female", "paragraph": "But things didn't quite work out that way, did they?"},
    {"speaker": "male", "paragraph": "No, not at all. The 1970s brought what's called the first AI winter..."}
  ]
}
```

步骤 2：执行生成：
```bash
python /mnt/skills/public/podcast-generation/scripts/generate.py \
  --script-file /mnt/user-data/workspace/ai-history-script.json \
  --output-file /mnt/user-data/outputs/ai-history-podcast.mp3 \
  --transcript-file /mnt/user-data/outputs/ai-history-transcript.md
```

这将生成：
- `ai-history-podcast.mp3`：音频播客文件
- `ai-history-transcript.md`：播客的可读 Markdown 文字稿

## 特定模板

仅在匹配用户请求时阅读以下模板文件。

- [技术讲解器](templates/tech-explainer.md) - 用于转换技术文档和教程

## 输出格式

生成的播客遵循 "Hello Deer" 格式：
- 两个主持人：一男一女
- 自然的对话式对话
- 以 "Hello Deer" 问候开始
- 目标时长：约 10 分钟
- 交替说话者以保持吸引人的流畅度

## 输出处理

生成后：

- 播客和文字稿保存在 `/mnt/user-data/outputs/`
- 使用 `present_files` 工具与用户分享播客 MP3 和文字稿 MD
- 提供生成结果的简要描述（主题、时长、主持人）
- 如需调整，提供重新生成选项

## 环境要求

必须设置以下环境变量：
- `VOLCENGINE_TTS_APPID`：火山引擎 TTS 应用 ID
- `VOLCENGINE_TTS_ACCESS_TOKEN`：火山引擎 TTS 访问令牌
- `VOLCENGINE_TTS_CLUSTER`：火山引擎 TTS 集群（可选，默认为 "volcano_tts"）

## 注意事项

- **始终在单次调用中执行完整流程** - 无需测试单独步骤或担心超时
- 脚本 JSON 应与内容语言匹配（en 或 zh）
- 技术内容应在脚本中简化以便音频理解
- 复杂符号（公式、代码）应在脚本中翻译为通俗语言
- 较长的内容可能导致较长的播客
