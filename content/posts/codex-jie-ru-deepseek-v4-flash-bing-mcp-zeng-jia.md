+++
title = "Codex 接入 DeepSeek V4 Flash，并通过 MCP 增加图片理解能力"
date = "2026-08-04T19:53:00+08:00"
draft = false
description = "本文介绍如何在 Codex 中接入 DeepSeek V4 Flash，并通过 GLM-4.6V Vision MCP 增加图片、截图和界面分析能力。文章梳理了配置备份、自定义模型、视觉 MCP、自动识图 Skill 和功能验证流程，同时说明配置覆盖、接口兼容和 API Key 安全等注意事项。"
categories = ["AI"]
tags = ["Codex接入DeepSeek", "GLM-4.6V", "Vision MCP Server", "Codex Skill教程", "AI编程工具", "多模态AI工作流"]
+++

[DeepSeek](/tags/deepseek/) V4 Flash 本身主要面向文本、编程和 Agent 任务。如果希望在 [Codex](/tags/codex/) 中使用 DeepSeek，同时让它能够分析截图、界面、报错图片或设计稿，可以采用下面这套组合方案：

```text
Codex
  ├─ DeepSeek V4 Flash：负责推理、编程和工具调度
  ├─ Vision MCP：负责读取和分析图片
  └─ Skill：判断何时自动调用视觉工具
```

这并不是给 DeepSeek 模型本身增加视觉参数，而是让它在需要查看图片时，调用一个独立的视觉模型完成识图，再根据识图结果继续处理任务。

![Codex 接入 DeepSeek V4 Flash，并通过 MCP 增加图片理解能力](/uploads/2026/08/23_08_01_2-c9214eb7.jpg)

## DeepSeek V4 Flash 是什么

DeepSeek 在 2026 年 4 月发布了 DeepSeek V4 Preview，其中包括：

* DeepSeek V4 Pro：面向复杂推理和高难度 Agent 任务
* DeepSeek V4 Flash：速度更快、调用成本更低
* 最高支持约 100 万 [Token](/tags/token/) 上下文

2026 年 7 月 31 日，官方进一步更新了 `DeepSeek-V4-Flash-0731`。通过 DeepSeek API 使用 `deepseek-v4-flash` 模型名时，会自动指向当前更新版本。

V4 Flash 的主要优势不是在所有测试中超过旗舰模型，而是兼顾了价格、速度、长上下文和工具调用能力，更适合日常编程、代码修改以及 Agent 工作流。

> 模型评分会受到测试集、推理参数和评测平台影响，不建议只根据单一排行榜判断模型强弱。

## 第一步：备份 Codex 配置

在修改配置之前，先备份 Codex 的全局配置目录。

### [Windows PowerShell](/tags/windows-powershell/)

```powershell
Copy-Item "$HOME\.codex" "$HOME\.codex-backup" -Recurse
```

### macOS 或 Linux

```bash
cp -R ~/.codex ~/.codex-backup
```

重点需要保留的内容通常包括：

```text
~/.codex/config.toml
~/.codex/skills/
```

不同版本的 Codex 可能还会使用项目目录中的：

```text
项目目录/.codex/config.toml
项目目录/.codex/skills/
```

不要把包含 API Key 的配置文件提交到公开 GitHub 仓库。

## 第二步：让 Codex 使用 DeepSeek

[Codex CLI](/tags/codex-cli/) 支持通过 `config.toml` 配置模型和模型提供商，但第三方服务需要提供 Codex 所需的兼容接口。

DeepSeek API 支持 OpenAI 风格的接口，不过 Codex 对第三方模型的兼容性还取决于：

* Codex 当前版本
* DeepSeek API 接口类型
* Responses API 与流式输出兼容情况
* Tool Call 参数是否能够正确转换

因此，实际接入时可能需要直接配置 DeepSeek，也可能需要借助兼容代理层。

配置结构可参考：

```toml
model = "deepseek-v4-flash"
model_provider = "deepseek"

[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com"
env_key = "DEEPSEEK_API_KEY"
```

API Key 建议通过环境变量保存。

### Windows PowerShell

```powershell
[Environment]::SetEnvironmentVariable(
  "DEEPSEEK_API_KEY",
  "你的 DeepSeek API Key",
  "User"
)
```

设置完成后重新打开终端。

### macOS 或 Linux

```bash
export DEEPSEEK_API_KEY="你的 DeepSeek API Key"
```

然后启动 Codex：

```bash
codex
```

如果出现接口格式、Responses API 或 Tool Call 不兼容的问题，说明当前 DeepSeek 接口不能直接满足 Codex 的全部请求，需要增加一个兼容转换层，而不是反复修改 API Key。

## 第三步：配置视觉理解 [MCP](/tags/mcp/)

DeepSeek V4 Flash 主要负责文本推理。图片分析可以交给 GLM-4.6V 或 GLM-4.6V-Flash。

Z.[AI](/tags/ai/) 官方提供了 Vision [MCP Server](/tags/mcp-server/)，可为支持 MCP 的 AI 客户端增加：

* 图片内容分析
* 截图报错识别
* 网页界面理解
* 表格和图表分析
* 视频内容理解
* 视觉定位与界面操作辅助

其中，GLM-4.6V-Flash 当前提供免费调用选项，但免费额度、速率限制和开放政策可能调整，正式使用前应查看最新价格页面。

MCP 配置通常写入：

```text
~/.codex/config.toml
```

结构示例：

```toml
[mcp_servers.vision]
command = "你的 Vision MCP 启动命令"
args = ["对应的启动参数"]
enabled = true

[mcp_servers.vision.env]
ZAI_API_KEY = "建议改用环境变量，不要直接填写在公开文件中"
```

实际的 `command`、`args` 和环境变量名称，应以所使用的 Vision MCP 项目说明为准。

配置完成后，重启 Codex，并检查 MCP 是否已经加载：

```text
/mcp
```

也可以直接测试：

```text
请分析这张图片，告诉我图片中的报错原因，并给出修改步骤。
```

如果 DeepSeek 能够返回视觉 MCP 的识别结果，说明工具链已经接通。

## 第四步：封装自动识图 [Skill](/tags/skill/)

只配置 MCP 后，模型不一定会在每次遇到图片时主动调用它。

可以再创建一个 Skill，明确告诉 Codex：

* 哪些任务需要调用视觉 MCP
* 应该先读取图片还是先询问用户
* 得到识图结果后如何继续处理
* 哪些情况下不应该调用视觉工具

Skill 可以放在：

```text
~/.codex/skills/image-understanding/
```

例如创建：

```text
~/.codex/skills/image-understanding/SKILL.md
```

参考内容：

```md
# Image Understanding

当用户要求分析图片、截图、界面、设计稿、图表或图片中的错误信息时：

1. 优先调用 Vision MCP 获取图片内容。
2. 不要根据文件名猜测图片内容。
3. 提取图片中的文字、界面状态、关键元素和异常信息。
4. 将视觉结果与当前代码或任务上下文结合。
5. 给出可以执行的修改方案。
6. 图片无法读取时，明确说明失败原因，不要虚构识别结果。
```

这样，当用户输入类似下面的任务时，DeepSeek 就更容易自动调用视觉工具：

```text
查看这张报错截图，找到项目无法启动的原因。
```

```text
分析这个网页截图，并根据现有项目修改页面布局。
```

```text
读取图片中的配置内容，判断 MCP 是否启用成功。
```

## 第五步：验证是否真正生效

建议分别测试三个层级。

### 1. 测试 DeepSeek

```text
请告诉我当前使用的模型提供商和模型名称。
```

确认请求是否确实发送到了 DeepSeek，而不是仍在使用 Codex 默认模型。

### 2. 测试 Vision MCP

```text
调用视觉工具分析这张图片，并列出图片中的主要文字。
```

确认 MCP 能被单独调用。

### 3. 测试自动识图 Skill

```text
这张图片为什么运行失败？
```

不要主动写“请调用 MCP”，观察 Skill 是否会自动判断并使用视觉工具。

只有以上三个测试都成功，才能说明“DeepSeek + Codex + Vision MCP + Skill”的完整链路已经生效。

## 配置容易丢失的原因

需要注意，Codex 的全局配置、项目配置和不同客户端可能使用不同的配置层级。

以下操作可能导致自定义配置失效：

* 替换整个 `config.toml`
* 恢复旧版 Codex 配置
* 在桌面端和 CLI 之间切换配置
* 删除或重建 `~/.codex` 目录
* 使用脚本覆盖原有配置文件
* 把 MCP 配置写在了错误的用户目录
* 在项目配置和全局配置中重复定义同名 MCP

曾有用户报告 Codex Desktop 在特定环境中重写全局配置，并移除手动添加的 MCP 项目。因此，修改前备份是必要的，但这不代表所有版本都会自动清除配置。

更加稳妥的做法是：

```text
1. 先备份 ~/.codex
2. 先配置并验证 MCP
3. 再创建自动识图 Skill
4. 最后添加 DeepSeek 模型配置
5. 每完成一步都单独测试
```

不要一次覆盖整个配置文件。应把 DeepSeek 配置合并到现有配置中，保留原来的 MCP、Skill 和其他设置。

## 这套方案适合哪些任务

配置完成后，可以用于：

* 让 DeepSeek 根据报错截图修复代码
* 分析网页界面并修改前端样式
* 读取软件配置截图
* 从图表中提取数据
* 检查页面排版和视觉问题
* 分析图片中的终端输出
* 根据设计稿生成或调整代码

它的核心价值不是让 DeepSeek 直接变成多模态模型，而是利用 MCP 将文本模型、视觉模型和 Codex 的文件操作能力组合起来。

## 相关项目与官方资料

* [OpenAI Codex](/tags/openai-codex/)：
  https://github.com/openai/codex

* DeepSeek 官方 GitHub：
  https://github.com/deepseek-ai

* DeepSeek V4 Flash 模型页面：
  https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731

* Z.AI Vision MCP Server 文档：
  https://docs.z.ai/devpack/mcp/vision-mcp-server
