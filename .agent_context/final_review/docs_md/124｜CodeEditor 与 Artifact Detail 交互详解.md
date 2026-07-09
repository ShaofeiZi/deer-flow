<title>124｜CodeEditor 与 Artifact Detail 交互详解</title>

<callout emoji="✅">
**本章目标：**继续按 workspace 业务组件讲解职责、输入输出和运行逻辑。
</callout>

| 组件/文件 | 说明 |
|-|-|
| code-editor.tsx | 代码查看/编辑展示。 |
| artifact-file-detail.tsx | 根据文件类型选择 code/preview/download。 |
| artifact-file-list.tsx | 选择 artifact。 |
| core/artifacts/preview.ts | 判断预览类型。 |

```mermaid
flowchart TD
  ArtifactList --> SelectFile
  SelectFile --> Detail[ArtifactFileDetail]
  Detail --> IsWrite{filepath starts write-file}
  IsWrite -->|yes| ToolCallDraft[find tool call result or draft content]
  IsWrite -->|no| FetchArtifact[useArtifactContent]
  FetchArtifact --> SkillPath{ends .skill}
  SkillPath -->|yes| FetchSkillMd[append SKILL.md]
  SkillPath -->|no| FetchRaw[artifact URL]
  ToolCallDraft --> ViewState[getArtifactViewState]
  FetchRaw --> ViewState
  FetchSkillMd --> ViewState
  ViewState -->|code mode| CodeEditor
  ViewState -->|markdown preview| StreamdownPreview
  ViewState -->|html preview| HtmlBlobIframe[base href + scroll restore + sandbox iframe]
  ViewState -->|non-code| RawIframe[artifact URL iframe]
  Detail --> Actions[copy open download close]
  SkillPath --> InstallSkill[install skill action]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart TD
  Start["write-file filepath"] --> Parse["parseWriteFileArtifact"]
  Parse --> Scan["scan ai messages tool_calls"]
  Scan --> Match{"write_file args.path match"}
  Match -->|"no"| Scan
  Match -->|"yes"| Res["findToolResult tool_call_id"]
  Res --> FailCheck{"selected and failed result"}
  FailCheck -->|"yes"| Empty["return undefined"]
  FailCheck -->|"no"| Include{"OK or selected undefined"}
  Include -->|"no"| Scan
  Include -->|"yes"| Append{"args.append and hasDraft"}
  Append -->|"yes"| Grow["append content"]
  Append -->|"no"| Reset["replace content"]
  Grow --> Sel{"isSelected"}
  Reset --> Sel
  Sel -->|"yes"| Done["return draft"]
  Sel -->|"no"| Scan
  Scan -->|"end no draft"| Fallback["toolCall.args.content"]
```

## Artifact detail 运行态补充

- `write-file:` artifact 不走普通 artifact fetch；它从 URL 中解析 `message_id/tool_call_id`，再从当前 thread messages 找对应 tool result 或 draft content。
- `.skill` artifact 被当作 markdown 代码内容读取，实际 fetch 路径会补 `/SKILL.md`，并在非静态站点下显示安装按钮。
- HTML/Markdown 才支持 preview toggle；HTML preview 会注入 `<base>` 和滚动恢复脚本，生成 Blob URL 后放入 sandbox iframe。
- 非代码文件当前直接 iframe 打开 artifact URL；下载按钮通过 `?download=true` 打开新窗口。
