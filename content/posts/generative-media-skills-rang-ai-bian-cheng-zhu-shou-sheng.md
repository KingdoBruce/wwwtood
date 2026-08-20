+++
title = "Generative Media Skills：让 AI 编程助手生成图片、视频和音频"
date = "2026-07-28T14:27:00+08:00"
draft = false
cover = "/uploads/2026/07/28_14_30_10_2-958887ea.jpg"
featured = true
categories = ["AI & Automation"]
tags = ["AI图片生成", "AI视频生成", "AI音频生成", "多模态AI", "Claude Code Skills", "Cursor Skills", "AI内容创作"]
+++

做 [AI](/tags/ai/) 内容创作时，图片、视频和音频通常需要分别打开不同的平台，不仅操作流程分散，提示词、素材和生成结果也不方便统一管理。

**Generative Media [Skills](/tags/skills/)** 是一套面向 [AI Agent](/tags/ai-agent/) 的多模态生成工具集，可接入 [Claude](/tags/claude/) Code、[Cursor](/tags/cursor/)、[Gemini](/tags/gemini/) CLI 等 AI 编程助手，用自然语言完成图片、视频和音频的生成与编辑。项目采用结构化参数调用生成服务，重点不是再做一个聊天界面，而是把多媒体生成能力直接加入现有的 AI 工作流。

![14_30_10_1](/uploads/2026/07/14_30_10_1-d555b165.jpg)

## 它能做什么？

Generative Media Skills 主要覆盖三类内容：

* **图片生成与编辑**：根据文字描述生成图片，也可用于修改、扩展和处理现有画面。
* **视频生成**：支持文字生成视频、图片生成视频等常见工作流。
* **音频生成**：可生成语音、音乐或其他音频内容。

项目还提供可复用的生成方案、基础调用模块和 [MCP](/tags/mcp/) Server，适合将多媒体生成能力接入自动化工作流，而不是每次都手动切换网站。

## 适合哪些人？

它比较适合以下使用场景：

1. 使用 [Claude Code](/tags/claude-code/)、Cursor 或 [Gemini CLI](/tags/gemini-cli/) 的内容创作者。
2. 需要批量生成封面图、短视频和配音的自媒体用户。
3. 想把图片、视频和音频生成接入自动化流程的开发者。
4. 需要统一管理生成提示词和媒体任务的小型内容团队。

例如，你可以直接告诉 AI：

> 为这篇文章生成一张科技风封面图，再制作一段 10 秒宣传视频，并生成中文旁白。

AI Agent 可以根据任务调用对应的媒体生成能力，减少在多个工具之间复制提示词和下载素材的步骤。

## 使用前需要注意

Generative Media Skills 本身更像一套 **AI Agent 技能和调用框架**，实际生成服务由 muapi.ai 提供，因此它并不等于完全离线、完全免费的本地生成软件。使用前应确认模型费用、生成额度、隐私政策以及不同模型的输出限制。

## 总结

Generative Media Skills 的价值，不是简单把图片、视频和音频功能放在一起，而是让 AI 编程助手能够直接调用这些生成能力。

对于已经使用 Claude Code、Cursor 或 Gemini CLI 的用户，它可以减少软件切换和重复操作，让多媒体内容生成更接近一套完整的自动化工作流。

## GitHub 项目地址

`https://github.com/SamurAIGPT/Generative-Media-Skills`
