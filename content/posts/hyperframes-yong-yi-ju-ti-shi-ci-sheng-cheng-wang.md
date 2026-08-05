+++
title = "HyperFrames：用一句提示词生成网页动画，并渲染为 MP4 视频"
date = "2026-07-28T12:07:00+08:00"
draft = false
featured = true
categories = ["AI"]
tags = ["AI视频生成", "AI编程助手", "Codex", "短视频制作", "开源视频工具"]
+++

做产品演示、工具介绍或数据动画时，传统视频软件往往需要手动调整时间轴、关键帧和字幕，制作过程比较繁琐。

**HyperFrames** 提供了另一种思路：使用 HTML、CSS 和 JavaScript 编写视频画面，再将网页动画逐帧渲染成 MP4 文件。

它尤其适合配合 [Claude](/tags/claude/) Code、[Codex](/tags/codex/) 等 [AI](/tags/ai/) 编程助手使用。你只需要描述视频主题、画面风格和动画效果，AI 就可以帮助生成对应的网页动画代码，然后通过 HyperFrames 完成预览和视频导出。


![2026728_12_09_15](/uploads/2026/07/2026728_12_09_15-bcf2b426.jpg)


## HyperFrames 是什么？

HyperFrames 是 HeyGen 开源的 HTML 视频渲染框架。

它可以把 HTML 页面、CSS 样式、图片、视频素材和可控制的网页动画，转换为帧数稳定、结果可复现的 MP4 视频。

简单理解就是：

> 用写网页的方式制作视频，再把网页动画渲染成 MP4。

HyperFrames 本身并不是 Sora、Veo 这类直接生成真实画面的文生视频模型。所谓“一句话生成视频”，通常是让 AI 编程助手根据提示词生成 HTML、CSS 和 JavaScript，再调用 HyperFrames 完成渲染。

## HyperFrames 可以做什么？

### 1. 制作产品宣传视频

可以用网页布局展示产品界面、功能卖点、价格方案和操作流程，适合制作 SaaS 产品介绍视频。

### 2. 生成动态数据视频

网页中的图表、数字、进度条和排行榜都可以加入动画，用于制作数据报告、业务汇报和社交媒体内容。

### 3. 制作文字与字幕动画

通过 CSS 或 GSAP 控制文字进入、缩放、渐变和切换效果，适合知识类短视频、教程和信息卡片。

### 4. 输出标准 MP4 文件

动画完成后，可以通过命令行直接渲染为 MP4，方便上传到抖音、视频号、[YouTube](/tags/youtube/) 或其他视频平台。

## 为什么适合 AI 编程助手？

传统视频编辑依赖时间轴操作，而 HyperFrames 的视频内容本质上是代码。

这意味着 AI 可以直接修改：

* 视频尺寸和时长
* 文字内容与页面布局
* CSS 动画和转场效果
* 图片、视频和音频素材
* 字幕、图表和品牌样式

例如，你可以直接告诉 AI：

```text
使用 HyperFrames 创建一段 10 秒的产品介绍视频。

要求：
1. 画面比例为 16:9
2. 深色科技风格
3. 开头显示产品名称
4. 中间依次展示三个核心功能
5. 结尾显示网站地址
6. 添加平滑的文字进入和页面切换动画
7. 最后渲染为 MP4
```

AI 会根据要求生成视频页面，再通过 HyperFrames 进行预览和导出。

## 基本使用流程

### 第一步：安装 HyperFrames Skill

官方提供了适用于 AI 编程助手的 Skill，可以通过下面的命令安装：

```bash
npx skills add heygen-com/hyperframes
```

### 第二步：让 AI 生成视频页面

在 [Claude Code](/tags/claude-code/)、Codex 或其他支持 Skill 的 AI 工具中，描述视频主题、时长、比例和动画要求。

### 第三步：浏览器预览

HyperFrames 使用普通 HTML 作为视频内容，因此可以先在浏览器中查看动画效果，再继续修改。

### 第四步：渲染 MP4

准备好 HTML 文件后，可以运行：

```bash
npx hyperframes render index.html
```

HyperFrames 会逐帧录制网页动画，并输出 MP4 视频文件。

## 适合哪些用户？

HyperFrames 比较适合：

* 想用 AI 批量制作短视频的人
* 熟悉 HTML、CSS 或 JavaScript 的开发者
* 需要制作产品演示视频的独立开发者
* 想自动生成数据动画和信息视频的内容创作者
* 不想反复拖动传统视频时间轴的用户

不过，它更擅长制作网页动画、产品演示、字幕和动态图表，并不适合直接生成复杂的真人电影画面。

## 总结

HyperFrames 把网页开发和视频制作连接在了一起。

你可以先用一句提示词让 AI 生成 HTML 动画，再使用 HyperFrames 将动画稳定地渲染为 MP4。对于产品介绍、数据展示、教程动画和批量短视频制作来说，这种工作方式比传统手动剪辑更容易自动化和重复使用。

## 项目地址

* GitHub：https://github.com/heygen-com/hyperframes
* 官方网站：https://hyperframes.heygen.com/
