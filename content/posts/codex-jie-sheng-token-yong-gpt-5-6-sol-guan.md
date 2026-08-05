+++
title = "Codex 如何节省 Token：用 GPT-5.6 Sol 管理、Luna 执行是否可行？"
date = "2026-08-04T19:38:00+08:00"
draft = false
description = "通过让 GPT-5.6 Sol 负责需求分析、架构决策和代码审查，再将明确的代码修改、测试和批量任务交给 GPT-5.6 Luna，可以降低 Codex credits 消耗。本文验证了自定义 Subagent 的官方配置方式，并给出可直接使用的 luna-worker.toml、调用提示词及避免多 Agent 反而浪费 Token 的注意事项。"
categories = ["AI"]
tags = ["Codex节省Token", "GPT-5.6 Sol", "GPT-5.6 Luna", "AI编程成本优化", "Codex多Agent工作流"]
+++

# [Codex](/tags/codex/) 如何节省 [Token](/tags/token/)：用 GPT-5.6 Sol 管理、Luna 执行是否可行？

可以，但不能简单理解成“所有写代码任务都交给 Luna Max”。

更准确的做法是把 [Codex](/tags/codex/) 工作流拆成两个角色：

* **GPT-5.6 Sol 负责决策**：分析需求、拆解任务、确定架构、处理复杂问题和最终审查。
* **GPT-5.6 Luna 负责执行**：修改指定文件、补充测试、修复明确 Bug、批量重构和运行检查。

这种方式类似让 Sol 当项目负责人，让 Luna 处理边界清晰的开发任务。

![Codex 如何节省 Token：用 GPT-5.6 Sol 管理、Luna 执行是否可行？](/uploads/2026/08/2321_08-37e15658.jpg)

## 为什么这样可以降低 Codex 消耗？

Codex 目前按照输入 [Token](/tags/token/)、缓存输入 Token 和输出 Token 计算 credits。

按照 OpenAI 当前公布的费率：

| 模型            |            输入 Token |            输出 Token |
| ------------- | ------------------: | ------------------: |
| GPT-5.6 Sol   | 125 credits / 100 万 | 750 credits / 100 万 |
| GPT-5.6 Terra |  50 credits / 100 万 | 300 credits / 100 万 |
| GPT-5.6 Luna  |   5 credits / 100 万 |  30 credits / 100 万 |

相同 Token 数量下，Luna 的 credits 消耗大约只有 Sol 的 **1/25**。

因此，把大量代码读取、修改和测试工作交给 Luna，通常能够显著降低总体消耗。

但实际节省比例不会固定为 96%，因为还要计算：

* Sol 拆解和审查任务产生的 Token；
* 父 Agent 向子 Agent 传递上下文的 Token；
* 子 Agent 返回结果的 Token；
* Luna 执行失败后的重试成本；
* 多个 Agent 重复读取代码产生的开销。

## 哪些任务适合交给 Luna？

GPT-5.6 Luna 更适合目标清楚、结果容易验证的任务，例如：

* 修改指定文件中的明确问题；
* 根据已有接口补充实现；
* 编写或补充单元测试；
* 修复已经定位的 Bug；
* 批量替换 API 或函数名称；
* 处理 ESLint、TypeScript 和格式错误；
* 运行测试并汇总失败信息；
* 修改文档和代码注释。

以下任务更适合保留给 Sol：

* 从模糊需求中设计完整功能；
* 决定系统架构或数据模型；
* 跨多个模块排查复杂问题；
* 处理安全、并发和性能问题；
* 审查大范围重构；
* 判断多个技术方案之间的取舍。

## 创建 Luna Worker

个人通用 Agent 可以放在：

```text
~/.codex/agents/luna-worker.toml
```

仅对当前项目生效时，建议放在项目目录：

```text
.codex/agents/luna-worker.toml
```

推荐配置：

```toml
name = "luna_worker"
description = "负责执行边界清晰、可以通过测试或 Diff 验证的代码修改任务。"

model = "gpt-5.6-luna"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"

developer_instructions = """
你是一个专门负责执行明确代码任务的开发 Agent。

工作要求：

1. 只处理父 Agent 明确委托的任务，不自行扩大范围。
2. 开始修改前，先确认目标文件、预期行为和验证方式。
3. 优先读取与任务直接相关的文件，不扫描整个代码仓库。
4. 采用最小修改原则，不重构无关代码。
5. 不修改未被明确要求处理的配置、依赖或公共接口。
6. 修改完成后运行最相关的测试、类型检查或构建命令。
7. 如果任务信息不足、存在架构决策或影响范围不明确，停止修改并返回父 Agent。
8. 最终返回：
   - 修改了哪些文件；
   - 每项修改的原因；
   - 执行了哪些验证；
   - 测试是否通过；
   - 尚未解决的风险。
9. 不创建新的子 Agent，不继续向下委托任务。
"""
```

这里建议默认使用 `high`，而不是直接设置成 `max`。

简单修改使用 `medium` 或 `high` 通常更节省；只有复杂逻辑、难以复现的 Bug 或大量边界条件检查，才值得使用 `max`。

## 可直接交给 Codex 的配置提示词

```text
请为当前 Codex 环境创建一个自定义执行 Agent。

要求：

1. 如果是个人通用配置，在 ~/.codex/agents/ 下创建 luna-worker.toml。
2. 如果当前项目已经使用 .codex 目录，则优先创建项目级配置：
   .codex/agents/luna-worker.toml。
3. Agent 名称设置为 luna_worker。
4. 模型设置为 gpt-5.6-luna。
5. model_reasoning_effort 默认设置为 high，不要直接使用 max。
6. sandbox_mode 设置为 workspace-write。
7. Agent 只负责边界明确、可通过测试或 Diff 验证的任务，例如：
   - 修改指定代码；
   - 修复已定位 Bug；
   - 补充测试；
   - 处理类型和格式错误；
   - 运行测试并汇总结果。
8. 遇到架构决策、需求不明确、跨模块影响或安全问题时，不要擅自处理，返回父 Agent 决策。
9. 禁止该 Agent 再创建子 Agent。
10. 创建完成后：
    - 输出文件完整路径；
    - 检查 TOML 语法；
    - 显示完整配置内容；
    - 使用 git diff -- .codex/agents/luna-worker.toml 展示 Diff；
    - 如果文件位于用户主目录而不在 Git 仓库中，则使用适合当前系统的命令展示新旧差异；
    - 不要修改其他文件。
```

## 如何调用这个 Agent？

配置完成后，可以在 Codex 中明确要求分工：

```text
先由主 Agent 分析问题、确定修改方案和验收条件。

方案确定后，将边界清晰的代码修改交给 luna_worker 执行。

luna_worker 完成后，主 Agent 必须检查 Diff、测试结果和潜在回归风险。

不要让 luna_worker 负责架构决策，也不要让多个 Agent 重复扫描整个仓库。
```

针对具体任务，可以这样写：

```text
请先分析这个 Bug 的根因，不要立即修改代码。

确认根因后，把最小修复任务交给 luna_worker：
- 只修改与该 Bug 直接相关的文件；
- 补充回归测试；
- 运行相关测试；
- 返回修改摘要和测试结果。

最后由主 Agent 审查 Diff，确认没有扩大修改范围。
```

## 使用时需要注意

### 1. 不要把所有任务都开到 Max

更高的推理强度会消耗更多 Token。推荐按任务分级：

* 简单替换、格式修复：`medium`
* 常规代码修改、补测试：`high`
* 复杂逻辑和难复现问题：`max`

### 2. 不要让多个 Agent 重复读取整个项目

多 Agent 不一定天然省 Token。

如果 Sol 和 Luna 都重新扫描整个仓库，可能出现上下文重复、工具调用增加和 Token 反而上升的问题。

应由 Sol 提供明确范围：

```text
只检查 src/auth/session.ts 和 tests/session.test.ts
```

而不是：

```text
检查整个项目并修复登录问题
```

### 3. 必须设置验收条件

委托任务时至少说明：

* 修改目标；
* 允许修改的文件；
* 不允许修改的范围；
* 需要运行的测试；
* 什么结果算完成。

任务越明确，Luna 的成功率越高，也越不容易因为反复重试浪费 Token。

## 最终结论

“Sol 负责规划和审查，Luna 负责执行”的 Codex 工作流是可行的，也有官方自定义 Subagent 配置支持。

它真正节省的不是 Token 数量本身，而是把大量执行阶段的 Token 从高费率模型转移到低费率模型。

不过，不建议固定使用 Luna Max。更实用的配置是：

```text
Sol：复杂分析、架构决策、最终审查
Terra：代码探索、较复杂的辅助分析
Luna Medium/High：明确修改、测试和批量任务
Luna Max：少量复杂但范围明确的任务
```

这样比“Sol + Luna Max 处理所有执行任务”更稳定，也更容易控制实际 credits 消耗。
