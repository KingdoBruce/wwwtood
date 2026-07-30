+++
title = "AI 编程如何减少 Token 消耗：覆盖 Agent 工作流的 7 个开源工具"
date = "2026-07-30T23:03:00+08:00"
draft = false
featured = true
categories = ["AI"]
tags = ["AI编程", "Token优化", "Coding Agent", "Claude Code", "Codex", "开源工具"]
+++

使用 [Claude](/tags/claude/) Code、[Codex](/tags/codex/)、[Cursor](/tags/cursor/) 等 [AI](/tags/ai/) 编程 Agent 时，[Token](/tags/token/) 消耗并不只取决于模型价格。

很多成本实际上来自重复扫描代码库、读取完整文件、加载无关上下文、分析冗长日志，以及生成没有实际价值的解释。要降低 AI 编程成本，重点不是单纯更换便宜模型，而是减少进入上下文窗口的无效信息。

下面这套方案覆盖代码探索、精准定位、规则管理、语义检索、日志过滤、回复压缩和仓库打包七个环节。

![AI 编程如何减少 Token 消耗：覆盖 Agent 工作流的 7 个开源工具](/uploads/2026/07/23_08_01-d99a75e0.jpg)

## 1. 使用 codebase-memory-[mcp](/tags/mcp/) 建立代码库索引

### 常见问题

[AI Agent](/tags/ai-agent/) 每次进入项目后，都可能重新执行以下操作：

* 扫描目录结构
* 搜索函数和类
* 分析调用关系
* 判断模块之间的依赖
* 重新理解 API 路由和业务流程

大型项目中，这类重复探索会消耗大量输入 Token。

### 解决方案

`codebase-memory-mcp` 会通过 Tree-sitter 分析代码，并将函数、类、调用链、路由和跨服务关系整理成持久化知识图谱。Agent 后续可以直接查询代码结构，而不必反复读取大量文件。

### 适合场景

* 长期维护的代码仓库
* 多模块或多服务项目
* 经常切换 AI 编程会话
* 需要分析函数调用链的项目

> 它更接近“代码结构记忆”，不能完全代替项目决策记录和开发文档。

---

## 2. 使用 Serena 进行符号级代码定位和修改

### 常见问题

Agent 可能只需要修改一个函数，却先读取整个几千行文件。这样不仅浪费 Token，还容易让无关代码干扰判断。

### 解决方案

Serena 是一个面向 AI 编程 Agent 的 MCP 工具包，可以按照函数、类、方法和引用关系查找代码，并进行符号级编辑、重构和调试。

例如，Agent 可以直接执行：

* 查找某个函数
* 查找函数的所有调用位置
* 在指定方法后插入代码
* 修改某个类，而不是重写整个文件

### 适合场景

* 单个文件代码较长
* 需要跨文件重构
* 希望 Agent 精确修改代码
* 不想让 Agent 大范围读取和重写文件

---

## 3. 使用 [AGENTS.md](/tags/agents-md/) 固化项目规则

### 常见问题

每次开始新会话时，都需要重复告诉 Agent：

* 项目使用什么技术栈
* 哪些目录不能修改
* 应该运行哪些测试
* 代码采用什么命名规范
* 修改完成后如何验证
* 不要生成哪些无关内容

这些重复提示不仅浪费时间，也会增加输入 Token。

### 解决方案

在项目根目录创建 `AGENTS.md`，将长期有效的项目规则统一写进去。

`AGENTS.md` 不是独立软件，而是一种面向编程 Agent 的开放指令格式，可以理解为“写给 AI Agent 的 README”。

```md
# AGENTS.md

## 项目技术栈

- Python 3.12
- FastAPI
- SQLite
- Playwright

## 修改规则

- 修改前先定位相关函数，不要扫描整个仓库
- 不要修改 `vendor/` 和生成文件
- 优先复用已有组件和工具函数
- 不要添加需求之外的功能
- 不要输出大段原理说明

## 验证命令

- 运行测试：`pytest`
- 运行类型检查：`mypy app`
- 修改前端后检查移动端布局
```

建议只写稳定、明确、可以执行的规则。内容过长反而会让每次请求都携带更多上下文。

---

## 4. 使用 grepai 搜索任务相关代码

### 常见问题

传统的 `grep` 只能根据关键词搜索。

例如搜索“用户登录流程”时，实际函数可能叫 `validateCredentials`、`createSession` 或 `verifyToken`。Agent 为了找到这些代码，可能需要搜索多个关键词并逐个读取文件。

### 解决方案

`grepai` 是一个语义代码搜索工具，可以根据代码含义查找相关函数，并支持调用方、被调用方和依赖关系追踪。

```bash
grepai search "用户登录和身份验证流程"
grepai trace callers "Login"
```

它不会直接压缩整个上下文，而是帮助 Agent 更快找到与任务真正相关的代码，减少无效文件读取。

### 适合场景

* 不清楚功能代码位于哪个目录
* 项目命名不统一
* 需要理解完整业务流程
* 只想把相关代码交给 AI

---

## 5. 使用 RTK 过滤终端和日志输出

### 常见问题

AI Agent 执行测试、Git、Docker 或构建命令时，终端可能返回数千行内容，其中真正有价值的只有：

* 一条错误信息
* 一个失败的测试
* 几行调用栈
* 少量警告

这些原始输出会直接占用上下文窗口，并在后续对话中持续消耗 Token。

### 解决方案

RTK 是一个命令行代理工具，会压缩常见开发命令的输出，隐藏成功日志、进度条和重复信息，只保留错误、摘要和关键结果。

项目 README 宣称，在部分常见开发命令中可减少 60%～90% 的输出 Token，但实际效果取决于命令类型和日志内容。

### 适合场景

* 测试输出很长
* Docker 日志较多
* Git diff 内容庞大
* 构建工具输出大量成功信息

RTK 主要减少的是**工具返回给 Agent 的内容**，并不能解决代码检索产生的 Token 浪费。

---

## 6. 使用 Caveman 压缩 Agent 最终回复

### 常见问题

代码修改完成后，Agent 经常继续输出：

* 重复描述用户需求
* 大段修改原理
* 不必要的客套话
* 多种用户没有要求的备选方案
* 冗长的下一步建议

这些内容通常不会提高代码质量，却会增加输出 Token。

### 解决方案

Caveman 是一个面向 [Claude Code](/tags/claude-code/)、Codex、Cursor、[Gemini](/tags/gemini/) CLI 等工具的 [Skill](/tags/skill/) 或插件，用更短的表达保留错误信息、命令和关键结论。

普通回复：

```text
我已经完成了相关修改。主要问题是组件在每次渲染时都会创建新的对象引用，因此建议使用 useMemo 对对象进行缓存。
```

压缩后：

```text
每次渲染都会创建新对象引用。使用 `useMemo` 缓存。
```

需要注意，Caveman 主要压缩**输出 Token**，不会自动减少 Agent 读取的代码和上下文。项目维护者也说明，在原本已经很简短的任务中，额外 Skill 指令可能无法带来明显节省。

---

## 7. 使用 Repomix 打包和过滤代码仓库

### 常见问题

直接将整个项目上传给 [ChatGPT](/tags/chatgpt/)、Claude 或其他 AI，通常会同时包含：

* 依赖目录
* 构建产物
* 缓存文件
* 测试快照
* 大型日志
* 无关文档
* 可能泄露的配置和密钥

这些内容既浪费 Token，也会增加信息泄露风险。

### 解决方案

Repomix 可以将代码仓库整理成一个适合 AI 阅读的文件，同时支持：

* 按规则排除目录和文件
* 自动遵守 `.gitignore`
* 统计各文件 Token 数量
* 检查潜在敏感信息
* 使用 Tree-sitter 提取主要代码结构

```bash
npx repomix@latest
```

只保留函数、类和关键结构：

```bash
npx repomix@latest --compress
```

Repomix 的 `--compress` 模式主要保留函数和类的签名，减少实现细节，因此更适合架构分析和初步定位，不一定适合需要逐行排查的复杂 Bug。

---

## 推荐的低成本组合

大多数个人开发者不需要同时安装全部工具。

### 小型项目

```text
AGENTS.md + Repomix
```

适合临时把项目交给 AI 分析。

### 中型项目

```text
AGENTS.md + Serena 或 grepai + RTK
```

同时减少代码读取、重复提示和终端日志。

### 长期维护的大型项目

```text
codebase-memory-mcp + Serena + AGENTS.md + RTK
```

代码结构查询、精准编辑、行为约束和日志过滤可以形成完整工作流。

Caveman 属于可选项，主要用于压缩最终回复，不应把它当作输入上下文优化工具。

## 总结

AI 编程中的 Token 优化不能只靠一句“回答简洁一点”。

真正有效的方法是分别处理不同来源的浪费：

| Token 浪费来源   | 对应方案                |
| ------------ | ------------------- |
| 重复探索代码结构     | codebase-memory-mcp |
| 读取和修改完整文件    | Serena              |
| 重复输入项目规则     | AGENTS.md           |
| 搜索大量无关代码     | grepai              |
| 终端和测试日志过长    | RTK                 |
| Agent 最终回复冗长 | Caveman             |
| 上传整个代码仓库     | Repomix             |

这些工具的功能存在一定重叠，也会带来安装、索引和维护成本。正确做法不是全部堆上，而是先观察 Token 主要浪费在哪个环节，再选择对应工具。

## GitHub 项目地址

* codebase-memory-mcp
  https://github.com/DeusData/codebase-memory-mcp

* Serena
  https://github.com/oraios/serena

* AGENTS.md
  https://github.com/agentsmd/agents.md

* grepai
  https://github.com/yoanbernabeu/grepai

* RTK
  https://github.com/rtk-ai/rtk

* Caveman
  https://github.com/JuliusBrussee/caveman

* Repomix
  https://github.com/yamadashy/repomix
