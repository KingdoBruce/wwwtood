+++
title = "Codex + Obsidian 长期记忆配置：让 AI 跨项目记住工作进度和关键决策"
date = "2026-07-28T19:42:00+08:00"
draft = false
featured = true
categories = ["AI"]
tags = ["Codex", "Codex长期记忆", "Codex永久记忆", "Obsidian", "Obsidian第二大脑", "AI智能体", "AI Agent", "AGENTS.md", "Codex CLI", "本地知识库", "AI工作流", "AI记忆系统"]
+++

[Codex](/tags/codex/) 每次开始新任务时，最麻烦的问题之一，就是需要重新解释项目背景、工作习惯和之前做过的决定。

解决这个问题的一种方法，是把 **[Obsidian](/tags/obsidian/) 作为 Codex 的外部长期记忆库**，将项目规划、关键决策、工作流程和每日复盘记录保存在本地 Markdown 文件中。

需要说明的是，这种方案并不是给 Codex 增加真正意义上的“永久大脑”，而是建立一套：

> **任务前读取历史信息，任务后更新工作记录的本地记忆工作流。**

目前 Codex 已经提供本地 Memories 功能，相关文件默认保存在 `~/.codex/memories/`，并可通过 `/memories` 控制当前对话是否读取或生成记忆。Obsidian 方案的价值，则在于记忆内容更加透明、可编辑、可分类，也更方便跨项目和跨工具使用。

![9d9898f00](/uploads/2026/07/9d9898f00-af395397.jpg)

## 一、Codex + Obsidian 的工作原理

整个流程可以分为四步：

1. 在 Obsidian 中建立固定的记忆库目录。
2. 使用 `AGENTS.md` 告诉 Codex 应该读取哪些笔记。
3. 每次任务开始前，读取相关项目状态和历史决策。
4. 任务完成后，将结果、问题和下一步计划写回 Obsidian。

Codex 会在执行任务前读取 `AGENTS.md`。你既可以在 `~/.codex/AGENTS.md` 中设置全局规则，也可以在具体项目目录中添加项目级规则。

## 二、推荐的 Obsidian 记忆库结构

可以在 Obsidian Vault 中建立下面的目录：

```text
Codex-Memory/
├── 00_INDEX.md
├── 01_GOALS/
│   └── long-term-goals.md
├── 02_PROJECTS/
│   ├── website.md
│   └── automation.md
├── 03_DECISIONS/
│   └── decision-log.md
├── 04_WORKFLOWS/
│   └── working-rules.md
├── 05_PREFERENCES/
│   └── user-preferences.md
└── 06_DAILY/
    └── 2026-07-28.md
```

各目录可以分别保存：

* `00_INDEX.md`：记忆库入口和目录说明。
* `01_GOALS`：长期目标和当前重点。
* `02_PROJECTS`：不同项目的背景、进度和待办事项。
* `03_DECISIONS`：重要选择、原因和最终结论。
* `04_WORKFLOWS`：代码规范、发布流程和操作步骤。
* `05_PREFERENCES`：常用格式、表达习惯和工具偏好。
* `06_DAILY`：每日任务总结和复盘记录。

不要让 Codex 每次读取整个 Obsidian 仓库。更合理的方式是先读取索引，再根据当前任务加载相关笔记，这样可以减少无关上下文和 [Token](/tags/token/) 消耗。

## 三、配置 Codex 的 [AGENTS.md](/tags/agents-md/)

在全局 Codex 目录或项目根目录中创建：

```text
AGENTS.md
```

Windows 用户通常可以放在：

```text
C:\Users\你的用户名\.codex\AGENTS.md
```

示例内容：

```md
# Codex 长期记忆规则

## Obsidian 记忆库

记忆库路径：

D:\Obsidian\Codex-Memory

## 开始任务前

1. 首先读取 `00_INDEX.md`。
2. 根据当前任务判断所属项目。
3. 读取对应的 `02_PROJECTS` 项目文件。
4. 检查 `03_DECISIONS` 中是否存在相关历史决策。
5. 只读取与当前任务直接相关的笔记，不要扫描整个仓库。

## 完成任务后

1. 更新对应的项目状态。
2. 将重要决策写入 `03_DECISIONS/decision-log.md`。
3. 将当天完成内容写入 `06_DAILY/YYYY-MM-DD.md`。
4. 记录遇到的问题、解决方案和下一步计划。
5. 不要保存密码、API Key、Cookie 或其他敏感信息。

## 记忆写入原则

只保存未来仍然有价值的信息，包括：

- 长期目标
- 项目背景
- 技术选择
- 关键决策及原因
- 可复用工作流程
- 用户明确表达的长期偏好

不要保存临时聊天、重复内容和一次性任务信息。
```

## 四、设置每日复盘

仅在 `AGENTS.md` 中写入“每天凌晨复盘”，并不会让 Codex自动执行。

要实现定时复盘，还需要使用：

* Windows 任务计划程序
* Linux 或 macOS 的 Cron
* 支持定时任务的 [AI](/tags/ai/) Agent
* 已经包含夜间整理功能的 Obsidian AI 项目

每天执行的复盘任务可以使用下面的提示词：

```text
读取今天的项目记录和每日笔记。

请完成以下工作：

1. 总结今天完成的主要任务。
2. 提取值得长期保存的关键决策。
3. 更新对应项目的当前状态。
4. 合并重复或已经失效的信息。
5. 将复盘结果写入今天的每日笔记。
6. 不要写入密码、Token、Cookie 或其他敏感数据。
```

部分开源项目已经实现了夜间整理、索引更新和跨项目记忆功能，但不同项目的自动化程度并不相同。例如，`codex-obsidian-memory-loop` 明确定位为手动复盘工作流，而不是后台自动监控系统。

## 五、原生 Codex Memory 与 Obsidian 的区别

| 方案                | 主要特点              | 适合场景             |
| ----------------- | ----------------- | ---------------- |
| Codex 原生 Memories | 自动从历史对话生成本地记忆     | 希望简单开启、减少手动维护    |
| Obsidian 记忆库      | 内容透明、可编辑、可分类      | 项目管理、知识沉淀、跨工具复用  |
| AGENTS.md         | 固定 Codex 的读取和执行规则 | 编码规范、项目流程、记忆读取入口 |
| 定时复盘脚本            | 自动整理每日记录          | 长期项目和持续知识维护      |

更实用的方式不是二选一，而是组合使用：

* 使用 Codex Memories 保存自动生成的上下文。
* 使用 Obsidian 保存经过确认的重要知识。
* 使用 `AGENTS.md` 定义读取和写回规则。
* 使用定时任务完成每日整理。

## 六、使用时需要注意的问题

### 不要保存敏感信息

不要把下面的信息写入记忆库：

* API Key
* 登录密码
* Cookie
* 私钥
* 客户隐私资料
* 未脱敏的内部数据

Codex 官方也建议在共享 Codex 目录或记忆文件前检查其中是否包含敏感内容。

### 不要无限追加笔记

记忆库并不是越大越好。

如果所有对话和日志都永久保存，Codex 检索时反而更容易读到过期信息。建议定期执行：

* 删除重复记录
* 标记失效决策
* 合并相似笔记
* 更新项目当前状态
* 保留决策发生的时间和原因

### 重要操作仍需人工确认

Codex 可以参考历史记录，但涉及删除文件、修改生产环境、付款、发布和权限调整时，仍然应该由用户最终确认。

## 七、适合使用这套方案的人

这套 Codex + Obsidian 长期记忆工作流，比较适合：

* 同时维护多个代码项目的开发者
* 经常使用 Codex 处理重复任务的人
* 希望沉淀项目决策和踩坑记录的个人用户
* 使用多个 AI 编程工具的团队
* 希望将 Obsidian 打造成 AI 第二大脑的人

它真正解决的问题，不是让 Codex 永远记住所有聊天，而是让重要信息以本地文件的形式保存下来，并在需要时被准确读取。

## 相关开源项目

### Obsidian Mind

面向 [Claude](/tags/claude/) Code、[Codex CLI](/tags/codex-cli/) 和 [Gemini](/tags/gemini/) CLI 的持久化 Obsidian 记忆库，包含笔记整理、索引和会话上下文功能。

GitHub：

https://github.com/breferrari/obsidian-mind

### Obsidian Second Brain

提供 Codex [Agent Skills](/tags/agent-skills/)、笔记检索、每日记录、夜间整理和知识库维护功能，配置相对完整，但安装步骤也更多。

GitHub：

https://github.com/eugeniughelbur/obsidian-second-brain

### Codex Obsidian Inspiration & Memory Loop

一套较轻量的 Codex + Obsidian 工作流模板，适合手动整理灵感、项目记录和可复用知识。

GitHub：

https://github.com/Alizeeyi/codex-obsidian-memory-loop
