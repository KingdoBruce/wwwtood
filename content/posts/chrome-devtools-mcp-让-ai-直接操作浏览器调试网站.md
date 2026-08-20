+++
title = "Chrome DevTools MCP：让 AI 直接操作浏览器调试网站"
date = "2026-07-24T17:28:00+08:00"
draft = false
categories = ["AI & Automation"]
tags = ["Chrome DevTools MCP", "MCP", "AI插件"]
featured = true
+++

以前使用 Codex、Claude Code 或 Cursor 修改网页时，AI 通常只能查看代码，却不知道网页实际运行后是什么样子。

**Chrome DevTools MCP** 可以把 AI 编程助手连接到真实的 Chrome 浏览器，让 AI 像开发者一样打开网页、点击按钮、查看报错并分析网站性能。它由 Chrome DevTools 团队维护。


![ChatGPT_Image_2026724_17_29_59](/uploads/2026/07/ChatGPT_Image_2026724_17_29_59-dc331e0b.png)


## 它能做什么？

安装后，AI 可以直接：

* 打开并操作网页；
* 点击按钮、填写表单；
* 查看 Console 控制台报错；
* 分析接口和网络请求；
* 截取网页图片；
* 检查页面加载速度；
* 分析 LCP、INP、CLS 等性能指标；
* 修改代码后自动打开浏览器验证结果。

简单理解：

> 它相当于给 AI 安装了一双“浏览器眼睛”，让 AI 不再只看代码猜问题。

## 最简单的安装方法

使用前需要安装：

* 最新稳定版 Chrome；
* Node.js LTS；
* npm。

### Codex 安装

在终端执行：

```bash
codex mcp add chrome-devtools -- npx chrome-devtools-mcp@latest
```

### Claude Code 安装

```bash
claude mcp add chrome-devtools --scope user npx chrome-devtools-mcp@latest
```

### Cursor 安装

打开：

```text
Cursor Settings → MCP → New MCP Server
```

填入：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

这些都是项目官方提供的安装方式。

## 如何测试？

安装完成并重启 AI 编程工具，然后输入：

```text
使用 Chrome DevTools 检查 https://developers.chrome.com 的性能。
```

如果配置正确，AI 会自动打开 Chrome，并开始记录网页性能数据。浏览器通常要等 AI 第一次调用工具时才会自动启动。

## 适合哪些人？

它特别适合：

* 使用 AI 开发网站；
* 排查网页打不开或按钮失效；
* 检查手机端布局；
* 分析接口请求失败；
* 优化网站加载速度；
* 让 AI 自动验证修改结果。

需要注意，Chrome DevTools MCP 可以读取和操作浏览器中的网页内容，因此不要让它连接到包含隐私、密码或敏感账户信息的浏览器页面。

## 项目地址

https://github.com/ChromeDevTools/chrome-devtools-mcp
