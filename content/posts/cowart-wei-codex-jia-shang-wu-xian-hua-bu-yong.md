+++
title = "Cowart：为 Codex 加上无限画布，用标注直接修改 AI 图片"
date = "2026-08-04T19:44:00+08:00"
draft = false
description = "Cowart 是一款基于 tldraw 的开源 Codex 无限画布插件，支持在画布中生成图片、添加箭头和文字标注，并让 Codex 根据标注生成新的修改版本。本文介绍 Cowart 的核心功能、安装方法、图片生成与标注改图流程，以及使用时需要注意的限制。项目还支持 AI HTML 和 AI Slides，适合海报、电商图片、网页原型和视觉方案的连续迭代。"
featured = true
categories = ["AI & Automation"]
tags = ["Codex 无限画布", "Codex 插件", "AI 图片修改", "AI 图片标注", "tldraw", "开源 AI 工具", "AI 视觉创作"]
+++

Cowart 是一款面向 [Codex](/tags/codex/) 的开源无限画布插件。它基于 tldraw 构建，可以在 Codex 中打开可视化画布，用于整理创意、放置参考图、生成图片、添加箭头和文字标注，以及根据标注继续迭代图片。

与只在聊天框里反复修改提示词相比，Cowart 更适合需要多轮调整的视觉创作任务。

## Cowart 能做什么

Cowart 目前主要支持以下功能：

* 在 Codex 中打开 tldraw 无限画布
* 创建指定尺寸和比例的 [AI](/tags/ai/) 图片框
* 输入提示词并添加一张或多张参考图
* 让 Codex 将生成结果放入指定图片框
* 在图片上添加箭头、文字和图形标注
* 根据标注生成新的修改版本
* 在画布中保留原图、标注和不同版本
* 生成并嵌入单文件 HTML 页面
* 将图片和 HTML 内容整理成 AI Slides

画布数据默认保存在当前项目的 `canvas/` 目录中，而不是上传或写入 Cowart 插件仓库。

![Cowart：为 Codex 加上无限画布，用标注直接修改 AI 图片](/uploads/2026/08/23_08_01_1-2ea35768.jpg)

## 为什么无限画布更适合 AI 改图

使用普通聊天窗口修改图片时，经常需要重新描述：

* 哪个物体需要调整
* 修改位置在哪里
* 哪部分应该保留
* 颜色、大小和方向如何变化

描述越复杂，提示词越容易出现歧义。

Cowart 将这些空间信息直接放到图片上。你可以圈出需要修改的区域，画一条箭头，再写上“删除这里的台灯”或“将沙发换成深棕色皮革”。

Cowart 会将原图、箭头和标注文字导出为截图，再交给 Codex理解修改要求并生成一个干净的新版本。

需要注意的是，这种方式本质上仍然是 AI 重新生成图片，并不等同于 Photoshop 的像素级局部编辑。复杂场景中，未标注区域也可能出现细节变化。

## 使用示例：生成中古风家居海报

### 第一步：打开 Cowart 画布

安装完成后，在 Codex 中输入：

```text
Open the Cowart canvas for this project.
```

### 第二步：创建 AI 图片框

在画布工具栏中创建一个“AI 图片”框，并调整为需要的尺寸和比例。

例如，制作一张中古风家居海报，可以输入：

```text
生成一张中古风家居海报。

画面是一间温暖的客厅，包含深棕色木质家具、焦糖色皮沙发、
复古落地灯和米白色地毯。使用低饱和暖色调、柔和侧光和
杂志广告式构图，保留顶部标题区域，图片比例为 4:3。
```

Cowart 会将提示词、参考图以及图片框的尺寸信息交给 Codex，并用生成结果替换这个图片框。

### 第三步：直接标注需要修改的位置

生成图片后，可以在画布中：

* 圈出不需要的家具
* 用箭头指出需要移动的位置
* 写明需要替换的颜色或材质
* 标出需要保留的区域

例如：

```text
删除这个花瓶
沙发改为深棕色皮革
标题区域增加留白
窗外改成傍晚街景
```

选中带有标注的图片，点击“按标注修改”。

Cowart 会将标注截图发送给 Codex，并把新生成的图片放在原图旁边。原图和标注不会被删除，方便继续比较和迭代。

## 安装 Cowart

最简单的方法是把下面的内容直接发送给 Codex：

```text
请从 https://github.com/zhongerxin/cowart.git 安装 Cowart Codex 插件。

请将仓库克隆到 ~/plugins/cowart，
确认 .codex-plugin/plugin.json 文件存在，
然后将插件加入 personal marketplace。

依次运行：

codex plugin marketplace add ~
codex plugin add cowart@personal

安装完成后，请校验插件是否可用，
并告诉我是否需要新建 Codex 对话来加载 Skill 和 MCP 工具。
```

也可以手动安装：

```bash
mkdir -p ~/plugins
git clone https://github.com/zhongerxin/cowart.git ~/plugins/cowart
cd ~/plugins/cowart
npm install
npm run build

codex plugin marketplace add ~
codex plugin add cowart@personal
```

安装完成后，建议新建一个 Codex 对话，让 Cowart 的 [Skill](/tags/skill/) 和 [MCP](/tags/mcp/) 工具完整加载。

## 适合哪些使用场景

Cowart 比较适合：

* AI 海报与网站封面设计
* 电商产品图修改
* 室内设计方案对比
* UI 页面和网页原型迭代
* 图片版本管理
* 演示文稿视觉素材整理
* 需要频繁圈选和标注的改图任务

它的核心价值并不是让 AI 图片绝对精准，而是把“用文字描述位置”变成“直接在画面上指出位置”，降低人与 AI 之间的沟通成本。

## 使用前需要注意

1. Cowart 是 Codex 插件，需要先具备可使用插件和 MCP Widget 的 Codex 环境。
2. 图片生成和修改仍会消耗对应模型额度。
3. 标注越清晰，生成结果通常越容易接近期望。
4. 一次修改的内容不要过多，建议分成多轮完成。
5. 重要文字、Logo 和商品细节应在生成后人工检查。
6. 当前项目采用 MIT 开源许可证，但生成图片所涉及的素材版权仍需自行确认。

## 项目地址

* GitHub：[zhongerxin/Cowart](https://github.com/zhongerxin/cowart)
* 底层画布框架：[tldraw/tldraw](https://github.com/tldraw/tldraw)
