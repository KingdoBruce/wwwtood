+++
title = "CodexBar：在 macOS 菜单栏统一查看 AI 编程工具额度"
date = "2026-07-28T20:22:00+08:00"
draft = false
featured = true
categories = ["Software & Tools"]
tags = ["AI编程工具", "Cursor", "Gemini", "OpenRouter"]
+++

同时使用 [Codex](/tags/codex/)、[Claude](/tags/claude/)、[Cursor](/tags/cursor/)、Gemini 和 [GitHub Copilot](/tags/github-copilot/) 时，最麻烦的事情之一，就是不知道每个平台还剩多少额度，以及下一次什么时候重置。

**CodexBar** 是一款免费开源的 macOS 菜单栏应用，可以把多个 [AI](/tags/ai/) 编程工具的使用额度、重置倒计时、余额和服务状态集中显示在桌面顶部。

不用反复打开不同网站，抬眼看一下菜单栏，就能了解当前 AI 工具的使用情况。


![CodexBar：在 macOS 菜单栏统一查看 AI 编程工具额度](/uploads/2026/07/af426cc6-39ea-412e-ba01-110e5c877a14-ce6ecd10.jpg)


## CodexBar 能做什么？

CodexBar 主要解决三个问题：

* 查看不同 AI 服务的当前使用额度
* 显示会话、每周或每月额度的重置时间
* 提醒用户某个服务是否出现故障或额度不足

部分服务还可以显示：

* 剩余积分或账户余额
* API 调用费用
* [Token](/tags/token/) 使用量
* 最近一段时间的使用趋势
* 服务故障和运行状态

具体能够显示哪些数据，取决于对应服务是否提供相关接口。

## 支持哪些 AI 工具？

CodexBar 官方目前列出了 63 个服务提供商，常见的包括：

* [OpenAI Codex](/tags/openai-codex/)
* OpenAI API
* Claude
* Cursor
* Gemini
* GitHub Copilot
* [Grok](/tags/grok/)
* GroqCloud
* OpenRouter
* LiteLLM
* [DeepSeek](/tags/deepseek/)
* ElevenLabs
* Deepgram
* MiniMax
* Kiro
* Zed
* Vertex AI
* AWS Bedrock

不同服务的连接方式并不完全相同，可能需要使用 OAuth、API Key、浏览器登录状态、本地 CLI 或应用配置文件。

## 两种菜单栏显示方式

CodexBar 提供两种主要显示模式。

### 独立图标模式

每个 AI 服务在菜单栏中显示一个独立状态项。

这种方式适合只使用两三个 AI 工具的用户，可以直接看到每个平台的剩余额度。

### 合并图标模式

将多个服务合并到一个菜单栏图标中，再通过提供商切换器查看不同平台。

当启用的 AI 工具较多时，这种模式可以减少菜单栏占用空间。

CodexBar 本身没有 Dock 图标，主要通过菜单栏运行，界面比较简洁。

## 动态条形图标有什么用？

CodexBar 会使用动态条形图标表示当前额度。

用户不需要每次点击菜单，就能通过图标大致判断：

* 当前额度是否充足
* 使用量是否接近上限
* 是否需要等待下一次重置
* 服务是否出现异常

对于长时间使用 AI 编程助手的开发者，这种显示方式比频繁检查网页控制台更方便。

## 如何安装 CodexBar？

CodexBar 桌面应用要求：

* macOS 14 Sonoma 或更高版本

使用 Homebrew 安装：

```bash
brew install --cask codexbar
```

也可以前往 GitHub Releases 页面下载安装包。

安装完成后，打开：

```text
Settings → Providers
```

启用自己正在使用的 AI 服务，并根据提示完成登录或授权。

## 使用时需要注意什么？

CodexBar 会复用已有的 OAuth 登录、浏览器 Cookie、API Key、本地 CLI 登录状态或配置文件，不会要求用户把所有平台密码直接保存到应用中。

不过，部分功能可能需要：

* 访问浏览器 Cookie
* 读取钥匙串信息
* 读取本地项目或日志文件
* 配置 API Key
* 开启文件访问权限

因此，在启用某个提供商之前，建议先查看该服务对应的数据来源和权限说明。

此外，不同 AI 平台开放的数据并不一致，所以并不是所有提供商都能同时显示额度、费用、Token 和重置时间。

## CodexBar 适合哪些人？

CodexBar 比较适合以下用户：

* 同时使用多个 AI 编程助手
* 经常遇到 Codex 或 Claude 额度限制
* 需要管理多个 API 账户
* 希望提前安排高消耗编程任务
* 不想频繁打开不同平台的控制台
* 想在菜单栏快速查看 AI 服务状态

如果你只偶尔使用一个 AI 工具，CodexBar 的作用可能不明显。

但对于每天同时使用 Codex、Claude、Cursor、Gemini 等工具的人来说，它可以减少检查额度和切换网页的时间。

## 总结

CodexBar 并不会增加 AI 工具的额度，它真正解决的是“额度不可见”的问题。

它把分散在不同平台中的使用限制、重置倒计时、账户余额和服务状态集中到 macOS 菜单栏，让用户能够更合理地安排 AI 编程任务。

项目免费开源，采用 MIT 许可证，支持 Homebrew 安装，也提供适用于 macOS 和 Linux 的命令行工具。

## 项目地址

* GitHub：https://github.com/steipete/CodexBar
* 官方网站：https://codexbar.app/
* Releases：https://github.com/steipete/CodexBar/releases
