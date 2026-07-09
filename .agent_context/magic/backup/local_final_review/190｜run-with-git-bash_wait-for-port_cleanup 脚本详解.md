<title>190｜run-with-git-bash、wait-for-port、cleanup 脚本详解</title>

<callout emoji="✅">
**本章目标：**继续拆 Docker、Provisioner、脚本和测试细模块。
</callout>

| 模块点 | 说明 |
|-|-|
| run-with-git-bash.cmd | Windows 下用 Git Bash 跑 bash 脚本。 |
| wait-for-port.sh | 等待服务端口 ready。 |
| cleanup-containers.sh | 清理容器。 |
| start-daemon.sh/start-daemon | 后台启动辅助。 |
| check.sh | shell 版检查入口。 |

```mermaid
flowchart TD
  Windows[Windows shell] --> GitBash[run with git bash]
  GitBash --> ShellScripts[serve docker deploy]
  Start[service start] --> Wait[wait for port]
  Wait --> Ready[service ready]
  CleanupReq --> Cleanup[cleanup containers]
  Cleanup --> Docker[docker remove/stop]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```