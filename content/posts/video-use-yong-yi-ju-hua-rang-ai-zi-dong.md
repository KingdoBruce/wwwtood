+++
title = "Video-use：用一句话让 AI 自动剪辑视频的开源技能"
date = "2026-08-04T22:11:00+08:00"
draft = false
description = "Video-use 是一个可接入 Claude Code、Codex 等 AI Agent 的开源视频剪辑 Skill。它能够根据自然语言指令分析原始素材，完成语音转录、口误与停顿删除、片段拼接、统一调色、字幕渲染、动画叠加和成片质量检查，并通过 `project.md` 保存项目进度，适合快速制作口播、教程、访谈和知识分享视频。"
featured = true
categories = ["AI & Automation"]
tags = ["Video-use", "AI 视频剪辑", "开源视频剪辑工具", "AI 自动剪视频"]
+++

把原始素材放进文件夹，再告诉 AI“把这些素材剪成一条教程视频”，Video-use 就能协助完成素材分析、片段筛选、调色、字幕、动画叠加和视频渲染。

Video-use 是 Browser Use 团队开源的 AI 视频剪辑 Skill，可接入 Claude Code、Codex 等具备终端操作能力的 AI Agent。截至 2026 年 8 月，GitHub 已获得约 1.89 万颗 Star。

## Video-use 可以做什么？

它主要适合已经拥有拍摄素材，希望通过自然语言快速完成剪辑的用户。

![Video-use：用一句话让 AI 自动剪辑视频的开源技能](/uploads/2026/08/acac708a-8226-4374-a7b8-dddf4fafc240-0b7e708d.jpg)

核心功能包括：

* 自动识别语音内容，删除“嗯”“啊”等语气词、口误和多余停顿
* 根据单词边界和静音区间选择剪辑点，减少截断语句的问题
* 为不同片段统一调色，支持暖色电影感、中性高对比和自定义 FFmpeg 参数
* 在每个剪辑点加入 30ms 音频淡入淡出，降低爆音和声音跳变
* 自动生成并硬编码字幕，字幕样式可以自定义
* 通过 HyperFrames、Remotion、Manim 或 PIL 添加动画图层
* 在输出前检查剪辑点、字幕遮挡、音频爆音和动画错位
* 将项目记录保存到 `project.md`，方便下次继续修改

项目采用“转录 → 内容整理 → AI 决策 → 生成剪辑表 → 渲染 → 自动检查”的工作流程。遇到问题时，会修正后重新渲染，最多进行三轮质量检查。

## 它是如何剪辑视频的？

Video-use 并不是把视频的每一帧都交给大模型分析。

它首先使用 ElevenLabs Scribe 获取逐词时间戳、说话人和音频事件，再将多个素材整理成体积较小的 `takes_packed.md`。AI 主要通过这份带时间轴的文字记录理解素材，只在需要判断停顿、动作或剪辑点时生成画面与波形预览。

确认剪辑方案后，Video-use 会生成：

```text
edit/
├── project.md
├── takes_packed.md
├── edl.json
├── transcripts/
├── animations/
├── clips_graded/
├── master.srt
├── verify/
├── preview.mp4
└── final.mp4
```

其中：

* `edl.json` 保存剪辑决策
* `master.srt` 保存最终时间轴字幕
* `preview.mp4` 用于预览
* `final.mp4` 是最终成片
* `project.md` 保存项目进度和修改记录

目前主要通过 `helpers/render.py` 完成片段提取、拼接、动画叠加和字幕渲染，并不是原文提到的 `make_video.py`。

## 安装前需要准备什么？

Video-use 本身采用 MIT 许可证开源，但完整使用还需要准备：

* Claude Code、Codex 或其他支持 Skill 和终端操作的 AI Agent
* Python 环境
* FFmpeg 和 FFprobe
* ElevenLabs API Key，用于语音转录
* Node.js，仅在使用 HyperFrames 或 Remotion 动画时需要
* yt-dlp，可选，用于下载在线视频素材

需要注意，Video-use 并不是完全离线运行。它当前依赖 ElevenLabs Scribe 完成逐词转录，因此可能产生 API 使用费用。

## 基本使用方法

安装并注册 Skill 后，进入保存视频素材的文件夹：

```bash
cd /path/to/your/videos
claude
```

使用 Codex 时，可以改为：

```bash
cd /path/to/your/videos
codex
```

然后直接输入剪辑要求：

```text
把这些素材剪成一条 60 秒的产品介绍视频，
删除口误和长停顿，使用暖色调，
添加中文字幕和简单的重点文字动画。
```

AI 会先分析素材并提出剪辑方案，得到确认后才会开始处理，不会直接修改原始文件。最终结果会保存在素材目录下的 `edit/final.mp4`。

## 适合哪些使用场景？

Video-use 比较适合：

* 知识分享和口播视频
* 软件教程和产品演示
* 多段素材合并
* Vlog 和旅行视频
* 访谈内容整理
* 需要反复修改的长期视频项目

它的优势不是完全替代专业剪辑师，而是把转录、粗剪、字幕、基础调色、动画叠加和质量检查整合到一个自然语言工作流中。

对于经常制作教程、口播或知识类内容的创作者，可以先让 Video-use 完成耗时的基础剪辑，再进行人工审片和细节调整。

## 项目地址

* GitHub：[browser-use/video-use](https://github.com/browser-use/video-use)
* 开源协议：MIT License
