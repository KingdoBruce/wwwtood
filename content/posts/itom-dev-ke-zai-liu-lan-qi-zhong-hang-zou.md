+++
title = "ITom Dev：可在浏览器中行走的开源 3D WebGL 作品集"
date = "2026-08-03T19:57:00+08:00"
draft = false
description = "ITom Dev 是 Tomasz Szmajda 开源的沉浸式 3D WebGL 开发者作品集。项目使用 React、Vite、Three.js、React Three Fiber 和 GSAP，将个人介绍、项目案例与联系方式放进可交互探索的手绘 3D 走廊。本文介绍项目特点、本地部署方法、浏览器设置、二次开发建议，以及 MIT 代码许可证与个人素材版权之间的区别。"
cover = "/uploads/2026/08/93e00659-200d-4b46-8155-bdbb1a458471-cc83081f.jpg"
featured = true
categories = ["Web & Hosting"]
tags = ["Vite", "WebGL", "GLSL", "开源作品集"]
+++

ITom Dev 是一个开源的沉浸式 3D 开发者作品集。它没有采用常见的卡片式简历页面，而是把个人介绍、项目案例和联系方式放进了一条可以交互探索的手绘走廊中。

访问者可以在浏览器里移动视角，进入 Gallery、Studio、About 和 Contact 等不同房间，查看作者的项目、个人介绍与联系方式。项目由 Tomasz “ITom” Szmajda 开发，源码已经公开在 GitHub。

## 项目特色

ITom Dev 最特别的地方，是把传统作品集的信息结构改造成了一个可探索的 3D 空间。

主要特点包括：

* 手绘铅笔风格的墙面、门、走廊和作品画框
* 可在浏览器中移动和切换房间
* 使用 WebGL 实时渲染 3D 场景
* 使用 GSAP 控制转场和交互动画
* 根据设备性能调整分辨率、抗锯齿和纹理加载
* 为搜索引擎提供独立的语义化 HTML 内容
* 支持桌面端和移动端访问

![ITom Dev：可在浏览器中行走的开源 3D WebGL 作品集](/uploads/2026/08/QQ20260803-200045-18147cd1.jpg)

它比较适合用来制作：

* 前端开发者个人作品集
* 创意设计师个人网站
* WebGL 项目展示页面
* 互动式个人简历
* 数字艺术展览或品牌展示网站

## 主要技术栈

项目主要使用以下前端技术：

* React
* Vite
* Three.js
* React Three Fiber
* GSAP
* WebGL
* GLSL Shader

![ITom Dev：可在浏览器中行走的开源 3D WebGL 作品集](/uploads/2026/08/QQ20260803-195943-60f953f4.jpg)

其中，React Three Fiber 用于在 React 中组织和管理 Three.js 场景，GSAP 负责页面动画与交互过渡，WebGL 和 GLSL Shader 则用于实现实时渲染和特殊视觉效果。

![ITom Dev：可在浏览器中行走的开源 3D WebGL 作品集](/uploads/2026/08/QQ20260803-195954-27848691.jpg)

## 本地部署教程

### 1. 准备运行环境

建议先安装：

* Git
* [Node.js](/tags/node-js/) 20 或更高版本
* npm

可以通过下面的命令检查版本：

```bash
git --version
node --version
npm --version
```

### 2. 克隆 GitHub 仓库

```bash
git clone https://github.com/ITomPoland/portfolio-itom.git
cd portfolio-itom
```

### 3. 安装项目依赖

```bash
npm install
```

### 4. 启动开发服务器

```bash
npm run dev
```

启动成功后，根据终端提示打开本地地址，通常为：

```text
http://localhost:5173
```

### 5. 测试生产版本

项目包含较多高清纹理和 WebGL 资源，开发模式下第一次加载可能需要等待几秒。

需要测试接近正式部署环境的性能时，可以运行：

```bash
npm run build
npm run preview
```

官方 README 也建议在测试性能时使用生产构建，而不是只观察开发模式下的加载速度。

## 浏览器设置建议

![ITom Dev：可在浏览器中行走的开源 3D WebGL 作品集](/uploads/2026/08/QQ20260803-200033-95deb485.jpg)

由于项目依赖 WebGL 实时渲染，建议在 Chrome、Edge 或其他现代浏览器中开启硬件加速。

以 Chrome 为例：

1. 打开浏览器设置。
2. 进入“系统”。
3. 开启“使用图形加速功能”。
4. 重启浏览器。

如果电脑显卡性能较弱，或者浏览器关闭了硬件加速，可能出现加载缓慢、动画掉帧或纹理显示异常。

## 二次开发需要修改哪些内容

这个项目可以作为 3D 作品集的技术基础，但不建议直接修改几段文字后上线。

至少需要替换以下内容：

* 作者姓名和个人介绍
* 头像与个人照片
* 项目封面和案例图片
* 联系方式与社交账号
* 房间中的介绍文字
* 品牌名称和 Logo
* 3D 纹理与手绘素材
* 网站标题、描述和 [SEO](/tags/seo/) 信息

还需要检查代码中是否存在作者自己的统计工具、接口地址、Sanity 配置、社交链接或部署环境变量。

## 许可证与素材版权

项目程序代码采用 MIT License，可以在遵守许可证要求的前提下使用、修改和发布。

但需要特别注意：MIT 许可证主要适用于仓库中的程序代码，并不代表作者的所有素材都可以自由使用。

GitHub README 明确说明，作者的个人素材、3D 纹理、图片和文案仍归 Tomasz Szmajda 所有，未经明确授权不得复制或重新发布。

因此，二次开发时应当：

* 保留 MIT License 要求的版权与许可证声明
* 替换作者的个人图片
* 替换原有项目案例
* 替换手绘纹理和品牌素材
* 重写所有个人介绍与页面文案

比较稳妥的做法是学习它的场景结构、交互方式和性能优化思路，再使用自己的视觉素材重新设计。

## 是否适合普通个人网站

ITom Dev 的视觉效果很有辨识度，但它并不适合所有个人网站。

比较适合：

* 希望展示 WebGL 或创意前端能力的开发者
* 需要突出交互设计能力的设计师
* 有时间优化纹理、模型和移动端性能的用户
* 希望把作品集本身作为项目案例的人

不太适合：

* 只需要快速上线一份在线简历的人
* 以文章阅读和搜索流量为主的博客
* 主要面向低性能移动设备的项目
* 不熟悉 React、Three.js 或 WebGL 的初学者

如果网站主要目标是获得搜索流量或让招聘人员快速查看经历，可以保留一个普通 HTML 作品列表或简历页面，3D 场景作为增强版入口。这样既能展示创意，也能避免所有信息都依赖 WebGL Canvas。

## 项目地址

* GitHub 源码：[ITomPoland/portfolio-itom](https://github.com/ITomPoland/portfolio-itom)
* 在线演示：[ITom Dev Interactive 3D Portfolio](https://itomdev.com/)
