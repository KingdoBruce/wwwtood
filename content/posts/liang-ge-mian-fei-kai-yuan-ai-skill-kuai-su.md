+++
title = "两个免费开源 AI Skills：快速制作电影感项目演示视频"
date = "2026-07-28T15:04:00+08:00"
draft = false
categories = ["AI"]
tags = ["Archify", "Codex", "AI视频制作", "电影感动画", "开源AI工具"]
+++

制作一个像样的项目演示视频，通常需要完成脚本、录屏、动画、架构图、音效和剪辑等多个步骤。

现在可以借助两个开源 [AI](/tags/ai/) [Skills](/tags/skills/)，简化其中最耗时间的两个环节：

* **video-shotcraft**：生成电影感产品演示和项目开场动画
* **Archify**：将代码仓库或系统描述转换成技术架构图

它们可以配合 [Claude](/tags/claude/) Code、[Codex](/tags/codex/) 等 AI 编程助手使用，比较适合开发者制作产品发布视频、GitHub 项目介绍、SaaS 功能演示和技术方案展示。

## video-shotcraft：生成电影感项目演示视频

video-shotcraft 是一个面向 [Claude Code](/tags/claude-code/) 和 Codex 的 AI 视频制作 Skill。

它基于 [Remotion](/tags/remotion/) 工作流，将项目页面、产品截图和功能素材组合成具有镜头运动、节奏切换和音效设计的演示视频。

项目内提供了：

* 106 个镜头设计方案
* 161 个动态效果预览
* 可直接修改的 Remotion 视频模板
* 页面截图与界面展示方案
* 2.5D 镜头移动效果
* 节奏同步剪辑与音效设计方法

使用时，可以让 AI 分析项目特点，生成分镜方案，再通过 Remotion 渲染为视频。

它适合制作：

* GitHub 开源项目介绍
* SaaS 产品发布视频
* 网站首页功能演示
* 软件更新宣传片
* 应用功能预告片

需要注意的是，video-shotcraft 提供的示例项目和默认模板包含作者自己的产品界面。

正式制作时，应替换以下内容：

* 产品截图
* 网站页面
* 项目名称
* 功能演示素材
* 配色与视觉元素
* 音效和背景音乐

不要直接使用默认素材，否则最终视频可能更像原项目的宣传片，而不是你自己的项目演示。

## Archify：把代码仓库转换成架构图

Archify 是一个面向 [Cursor](/tags/cursor/)、Claude Code、[Codex CLI](/tags/codex-cli/) 和 [OpenCode](/tags/opencode/) 的技术架构可视化 Skill。

你可以向它提供：

* 一个代码仓库
* 一段系统结构说明
* 服务之间的调用关系
* 产品业务流程
* 数据流和生命周期描述

Archify 会将这些信息整理成可交互的技术架构图。

目前支持的主要图表类型包括：

* 系统架构图
* 工作流程图
* 时序关系图
* 数据流图
* 生命周期图

生成结果可以导出为：

* HTML
* PNG
* SVG
* WebM
* 社交媒体分享图

与普通静态架构图相比，Archify 更强调结构验证、节点关系、上下游路径和架构变更对比，适合用于技术文档、项目汇报和代码评审。

> 注意：Archify 当前没有把“自动解析 Mermaid 代码”列为支持范围。更稳妥的方式是直接提供代码仓库或用自然语言描述系统结构。

## 两个 Skill 如何组合使用

可以按照下面的流程制作一条完整的项目演示视频：

```text
分析项目
   ↓
整理核心功能和演示重点
   ↓
使用 Archify 生成项目架构图
   ↓
准备网站截图和功能录屏
   ↓
使用 video-shotcraft 设计分镜与动画
   ↓
替换默认项目素材
   ↓
通过 Remotion 渲染视频
   ↓
检查字幕、节奏、音效和项目名称
```

Archify 负责把项目结构讲清楚，video-shotcraft 负责把项目展示得更有电影感。

例如，一条开源项目介绍视频可以这样安排：

1. 使用 video-shotcraft 制作项目 Logo 或首页的开场动画。
2. 展示项目解决的问题和核心功能。
3. 插入 Archify 生成的系统架构图。
4. 展示真实页面截图或功能操作过程。
5. 用简短总结说明项目适用场景。
6. 在结尾展示 GitHub 项目地址。

## 安装方式

两个项目都属于命令行工具，需要先准备 [Node.js](/tags/node-js/)、Git 和相应的 AI 编程助手。

Archify 可以使用 [Skills CLI](/tags/skills-cli/) 安装：

```bash
npx skills add tt-a1i/archify -g
```

安装完成后，可以向 AI 助手输入：

```text
Use archify to map this repository's runtime architecture.
```

video-shotcraft 可以通过仓库说明中的 Skills CLI、克隆仓库或手动链接方式安装。

对于不熟悉命令行的用户，可以直接把 GitHub 仓库地址交给 Claude Code、Codex 或其他具有终端操作能力的 AI 助手，并要求它：

```text
请阅读这个项目的 README，检查本地环境，完成安装并运行示例。
遇到错误时先分析原因，再逐步修复，不要跳过依赖检查。
```

## 使用建议

第一次使用时，不建议直接让 AI 生成完整视频。

更稳定的流程是：

1. 先生成视频脚本。
2. 确认需要展示的功能。
3. 准备真实项目截图。
4. 单独生成架构图。
5. 再制作分镜和动画。
6. 最后统一渲染成片。

这样可以避免出现界面与项目无关、架构图信息错误、镜头节奏混乱以及默认模板没有替换等问题。

## 总结

video-shotcraft 和 Archify 解决的是项目演示中的两个不同问题：

* **video-shotcraft**：让产品展示更有镜头感和视觉节奏。
* **Archify**：让系统架构和技术流程更容易理解。

它们不会自动替代完整的视频制作流程，但可以明显减少架构图绘制、镜头设计和动画开发中的重复工作。

对于需要经常发布 GitHub 项目、SaaS 产品、开发工具或技术方案的开发者，这套组合值得尝试。

## 项目地址

* video-shotcraft：https://github.com/Vincentwei1021/video-shotcraft
* Archify：https://github.com/tt-a1i/archify
