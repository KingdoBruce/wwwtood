+++
title = "Caveman Skill 是什么？让 Claude Code、Codex 少说废话并减少输出 Token"
date = "2026-08-13T22:13:00+08:00"
draft = false
description = "内容说明：本文根据 Caveman 官方 GitHub 仓库、公开 Benchmark 和项目说明整理，未进行本站独立 Token 对照测试。文中的“平均减少约 65%”来自项目方测试结果，并不代表所有模型和任务都能获得相同效果。"
featured = true
categories = ["AI"]
tags = ["Caveman Skill", "AI Skills", "Codex", "Claude Code", "AI 减少 Token"]
+++

用 [Claude](/tags/claude/) Code、[Codex](/tags/codex/) 这类 AI 编程 Agent 时，经常会遇到一个问题：明明只需要代码、命令或结论，AI 却先解释一大段，执行完还要再总结一次。

Caveman 就是为这种场景准备的 [Skill](/tags/skill/)。它不会让模型变聪明，也不会减少模型内部推理，而是尽量压缩最终回复，只保留代码、命令、结果和必要说明。

## Caveman 能减少多少 Token？

Caveman 官方 Benchmark 对 10 个编程任务进行了对比，项目给出的结果是：

**普通回复平均约 1214 Token，启用 Caveman 后约 294 Token，平均减少约 65%。**


![Caveman Skill 是什么？让 Claude Code、Codex 少说废话并减少输出 Token](/uploads/2026/08/6813_22_16_44-85fdfd84.jpg)


但这里需要注意两点：

1. 这是项目方测试结果，不是本站实测；
2. 它主要减少的是 **Output Token**，不是模型内部的 Reasoning / Thinking Token。

因此，更准确的理解是：

> Caveman 让 AI “少说话”，而不是让 AI “少思考”。

## 它主要删掉哪些内容？

Caveman 会尽量减少：

* 客套和铺垫；
* 重复解释；
* 执行过程复述；
* 已完成内容的再次总结；
* “如果需要我还可以……”之类的结尾。

例如你问：

```text
查询 Ollama 已安装模型
```

普通 AI 可能先解释 Ollama 是什么，而 Caveman 模式更倾向直接给出：

```bash
ollama list
```

对于频繁使用 Codex、Claude Code 的人，这种交互方式会更干脆。

## Caveman 怎么安装？

### [Windows](/tags/windows/)

在 PowerShell 中运行：

```powershell
irm https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.ps1 | iex
```

### macOS / Linux / WSL

```bash
curl -fsSL https://raw.githubusercontent.com/JuliusBrussee/caveman/main/install.sh | bash
```

以上属于“下载脚本后直接执行”的安装方式。比较在意安全的话，建议先到 GitHub 查看 `install.ps1` 或 `install.sh` 内容，再决定是否运行。

安装后可使用：

```text
/caveman
```

项目还提供不同压缩程度，例如：

```text
/caveman lite
/caveman full
/caveman ultra
```

## 哪些场景适合使用？

Caveman 更适合目标明确的任务，例如：

* 查询命令；
* 修复报错；
* 修改代码；
* 运行测试；
* 查看执行结果；
* 让 Agent 完成重复性编程任务。

例如让 Codex：

```text
修复这个 Bug，运行测试，只告诉我修改内容和测试结果。
```

这种任务本身并不需要大量解释，Caveman 的价值比较明显。

## 哪些情况不适合？

如果你正在：

* 学习陌生技术；
* 分析复杂架构；
* 排查安全问题；
* 比较多个方案；
* 希望理解 AI 的判断过程；

就不建议把输出压缩得太狠。

因为有些“解释”并不是废话，而是理解问题的重要信息。

因此比较合理的用法是：

**执行任务时开启，学习和分析时关闭。**

## Caveman 值不值得装？

如果你经常使用 Claude Code、Codex、[Cursor](/tags/cursor/) 等 AI Agent，而且已经受够每次执行完任务后的“小作文”，Caveman 值得尝试。

它最大的价值不是让模型能力变强，而是让回复更接近终端工具：

**问命令就给命令，问报错就给原因，任务完成就告诉结果。**

至于能省多少 Token，要看具体模型和任务。官方“平均约 65%”可以作为参考，但不能直接理解成安装后固定节省 65%。

## 总结

Caveman Skill 的作用很简单：**减少 AI Agent 回复中的客套、复述和过度解释，提高有效信息密度。**

它主要减少输出 Token，不会直接减少模型内部推理 Token。

如果你希望 Codex、Claude Code 少写“小作文”，它是一个值得关注的轻量 Skill；如果你的目标是大幅降低模型推理成本，那 Caveman 并不能解决这个问题。
