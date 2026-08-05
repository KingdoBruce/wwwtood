+++
title = "PPT Master：免费开源的 AI PPT 工具，生成真正可编辑的 PowerPoint"
date = "2026-07-27T09:27:00+08:00"
draft = false
featured = true
categories = ["AI"]
tags = ["AI", "MCP", "AI PPT 工具"]
+++

现在的 [AI](/tags/ai/) PPT 工具很多，但不少工具生成的只是图片、网页截图，或者套用固定模板拼出来的页面。

看起来像 PPT，真正需要修改时却很麻烦：文字不能单独调整、图表无法重新编辑、排版稍微改动就容易错位。

最近我发现了一个很实用的开源项目——**PPT Master**。

它最大的特点，是能够根据文档、资料或主题，生成真正的 `.pptx` 文件。PPT 里的文字、图形、配色和部分图表都可以继续在 PowerPoint、WPS、Keynote 等软件中修改，而不是把整页内容做成一张无法编辑的图片。


![QQ20260727-092725](/uploads/2026/07/QQ20260727-092725-cada564a.jpg)


截至本文整理时，这个项目在 GitHub 上已经获得约 **3.3 万颗 Star**，并且仍在持续更新。

## PPT Master 是什么？

PPT Master 是一套运行在 AI 编程工具中的 PPT 生成工作流。

安装完成后，可以在 [Claude Code](/tags/claude-code/)、[Codex](/tags/codex/)、Cursor、VS Code Copilot 等支持读取文件和执行命令的 AI 工具中，直接用自然语言告诉它：

> 根据这份产品资料，生成一套 12 页的中文产品介绍 PPT。

AI 会自动分析内容、规划页面结构、设计视觉风格，并导出可以继续编辑的 PowerPoint 文件。

它不是传统意义上的在线 PPT 网站，也不是打开网页后输入一句话就能生成的 SaaS 服务，而是一套需要部署在本地、配合 AI Agent 使用的开源工具。

## 它有什么特别之处？

### 1. 生成真正可编辑的 PPTX

这是 PPT Master 最有价值的地方。

项目通过 SVG 和 PowerPoint 原生 DrawingML 结构生成 PPT，最终导出的文字、形状、颜色和图形，可以作为 PowerPoint 对象继续调整。

生成完成后，你仍然可以：

* 修改标题和正文；
* 更换字体与颜色；
* 移动图标和形状；
* 调整版式和间距；
* 修改图表文字；
* 添加公司 Logo；
* 替换图片和品牌元素。

拿到的不是一套“看起来像 PPT 的图片”，而是一份真正可以修改和交付的演示文稿。

### 2. 支持多种内容来源

PPT Master 可以根据主题直接制作内容，也可以读取已有资料重新整理，例如：

* Markdown 文档；
* Word 文档；
* PDF 文件；
* HTML 网页；
* EPUB 文件；
* Jupyter Notebook；
* 已有的 PPTX 文件；
* 本地图片和项目资料。

你可以把产品介绍、项目方案、行业报告或会议资料放进项目目录，让 AI 根据原始材料生成 PPT。

### 3. 支持多种内容结构与视觉风格

PPT Master 将内容逻辑和视觉风格分开处理。

内容结构可以选择：

* 金字塔汇报；
* 故事叙述；
* 教程说明；
* 产品展示；
* 工作简报。

视觉上则可以选择瑞士极简、编辑杂志、柔和圆角、暗黑科技等不同方向，也可以根据企业品牌要求自定义风格。

因此，它不仅适合普通工作汇报，也可以用于：

* 产品介绍；
* 项目方案；
* 商业计划书；
* 行业分析；
* 教学课件；
* 公司培训；
* 商业路演；
* 咨询报告；
* 年度总结。

### 4. 支持动画、旁白和视频导出

项目支持页面转场和元素动画，还可以根据演讲者备注生成语音旁白，并将音频嵌入 PPT。

之后可以通过 PowerPoint 将整套演示文稿导出为带旁白和转场的视频。

### 5. 不只可以制作 PPT

除了常见的 16:9 和 4:3 演示文稿，PPT Master 还支持生成多种内容尺寸：

* 小红书 3:4 图文；
* 微信朋友圈 1:1 图片；
* Instagram 方形内容；
* 短视频竖屏封面；
* 微信公众号头图；
* A4 海报和宣传页。

这些内容最终仍可以导出为带有可编辑元素的 PPTX 文件。

## PPT Master 使用方法

下面以 Windows 系统为例介绍。

### 第一步：安装 Python

PPT Master 需要 Python 3.10 或更高版本。

安装 Python 时，一定要勾选：

```text
Add python.exe to PATH
```

安装完成后，打开 PowerShell，输入：

```bash
python --version
```

能够看到 Python 版本号，就说明安装成功。

### 第二步：下载项目

熟悉 Git 的用户，可以在 PowerShell 中执行：

```bash
git clone https://github.com/hugohe3/ppt-master.git
cd ppt-master
```

不熟悉 Git，也可以直接打开 GitHub 项目页面，点击：

```text
Code → Download ZIP
```

下载完成后解压到本地文件夹。

### 第三步：安装依赖

进入项目目录后执行：

```bash
pip install -r requirements.txt
```

如果系统提示找不到 `pip`，可以改用：

```bash
python -m pip install -r requirements.txt
```

安装完成后，可以执行下面的命令检查环境：

```bash
python -c "import pptx; import fitz; print('All core dependencies OK')"
```

如果显示：

```text
All core dependencies OK
```

说明核心环境已经配置完成。

### 第四步：使用 AI 工具打开项目

接下来使用支持 Agent 功能的 AI 工具打开 `ppt-master` 文件夹，例如：

* Codex；
* Claude Code；
* Cursor；
* VS Code Copilot；
* 其他能够读取文件并执行终端命令的 AI Agent。

打开后，可以先输入一条简单的测试指令：

```text
请创建一份 3 页的测试 PPT。

主题：人工智能如何提高工作效率。

页面结构：
1. 封面
2. 主要应用场景
3. 总结

使用简洁、现代的商务风格，生成中文内容，并导出为可编辑的 PPTX 文件。
```

执行完成后，生成的 PPT 文件通常会保存在：

```text
exports
```

目录中。

## 推荐提示词

正式制作 PPT 时，可以直接使用下面的提示词：

```text
请使用 PPT Master，根据我提供的资料制作一套完整的中文演示文稿。

具体要求：

1. PPT 主题：填写你的主题
2. 使用场景：工作汇报 / 产品介绍 / 商业路演
3. 目标受众：填写听众身份
4. 页面数量：10—12 页
5. 页面比例：16:9
6. 视觉风格：现代、简洁、专业
7. 内容要求：
   - 先整理资料并生成清晰的大纲；
   - 每页只表达一个核心观点；
   - 避免大段文字；
   - 重要数据尽量使用图表或信息图；
   - 保持整套 PPT 的字体、配色和间距统一；
   - 为每一页添加简洁的演讲者备注。
8. 输出要求：
   - 导出真正可编辑的 PPTX 文件；
   - 文字、形状和图表保持可修改；
   - 检查是否存在文字溢出、元素重叠和页面错位；
   - 完成后告知 PPTX 文件的保存位置。
```

如果已经准备好了 Word、PDF 或 Markdown 文件，可以补充：

```text
请优先读取项目目录中的资料，不要虚构资料中没有出现的数据。
```

## 如何修改生成结果？

PPT 生成后，不需要整套重新制作。

假如某一页出现问题，可以直接告诉 AI：

```text
第 3 页标题和图表发生重叠，请重新调整这一页的版式，其他页面不要修改。
```

也可以继续提出更具体的要求：

```text
将第 5 页改为左右分栏布局。
```

```text
第 7 页文字太多，请压缩内容并增加一张信息图。
```

```text
将整套 PPT 修改为深色科技风，但不要改变原来的内容结构。
```

PPT Master 支持针对单独页面进行重新生成和修复，不一定每次都要从头开始。

## 使用时需要注意什么？

### PPT Master 本身免费，但 AI 模型不一定免费

PPT Master 使用 MIT 开源协议，项目本身可以免费使用。

但是，它需要配合 Claude Code、Codex、Cursor 或其他 AI 模型工作，因此可能产生模型订阅费或 API 调用费用。

### 它不是完全零门槛的一键工具

第一次使用时，需要完成：

* 安装 Python；
* 下载项目；
* 安装依赖；
* 配置 AI 编程工具；
* 必要时配置模型或图片 API。

对于完全没有接触过本地部署的用户来说，前期需要一点学习成本。

### 最终效果仍然取决于资料和提示词

AI 能够提高制作效率，但无法代替内容判断。

如果提供的资料过于简单，或者没有明确告诉 AI 使用场景、受众和页面重点，生成结果也容易显得空泛。

建议提前准备：

* 完整的原始资料；
* 明确的汇报对象；
* 大概的页面数量；
* 企业配色和 Logo；
* 参考 PPT 或视觉案例；
* 希望重点表达的数据。

## 总结

PPT Master 最值得关注的地方，并不是“AI 可以自动做 PPT”，而是它解决了 AI PPT 工具普遍存在的一个问题：

**生成之后还能不能继续编辑。**

它输出的是原生可编辑的 PowerPoint 文件，而不是简单的图片或网页截图。对于经常需要制作工作汇报、产品介绍、项目方案、行业报告和商业路演的人来说，这种可编辑性非常重要。

虽然前期需要安装环境，并配合 Codex、Claude Code、Cursor 等 AI 工具使用，但完成配置后，就可以把它变成一套长期使用的本地 AI PPT 工作流。

如果你平时经常制作 PPT，这个项目值得收藏和尝试。

## 项目地址

GitHub：

```text
https://github.com/hugohe3/ppt-master
```

项目主页：

```text
https://hugohe3.github.io/ppt-master/
```

中文说明：

```text
https://github.com/hugohe3/ppt-master/blob/main/README_CN.md
```

Windows 安装指南：

```text
https://github.com/hugohe3/ppt-master/blob/main/docs/windows-installation.md
```
