+++
title = "Graphify：把整个项目变成一张 AI 能看懂的知识图谱"
date = "2026-07-24T13:45:00+08:00"
draft = false
cover = "/uploads/2026/07/94a061f4-539f-4fef-9e98-11d51d5dc4a1-b4597ea7.png"
featured = true
categories = ["AI"]
tags = ["Graphify", "AI", "知识图谱"]
+++

使用 Codex、Claude Code 或 Cursor 分析大型项目时，AI 往往需要反复搜索文件、读取代码，既慢又容易浪费上下文。

**Graphify** 的作用，就是把项目中的代码、文档、配置、PDF 和图片整理成一张“知识图谱”。图谱会记录文件、函数、类、调用关系和模块之间的联系，让 AI 不必每次从头翻阅整个项目。

## 它有什么用？

安装 Graphify 后，可以帮助 AI：

* 快速理解项目结构；
* 查找函数和类之间的关系；
* 分析修改代码会影响哪些位置；
* 查看两个模块之间的调用路径；
* 减少反复读取大量无关文件。

代码分析主要在本地通过 Tree-sitter 完成，不需要把源代码上传给第三方模型。Graphify 生成的每条关系还会标记为“源码中直接提取”或“工具推断”，方便判断结果是否可靠。

## 最简单的安装方法

先安装 `uv`，然后在终端执行：

```bash
uv tool install graphifyy
graphify install
```

注意：Python 安装包的名称是 **graphifyy**，有两个字母 `y`，但安装后的命令仍然是 `graphify`。

安装完成后，打开 Codex、Claude Code 或 Cursor，在项目目录中输入：

```text
/graphify .
```

Graphify 会自动分析当前项目，并生成：

```text
graphify-out/
├── graph.html
├── GRAPH_REPORT.md
└── graph.json
```

其中：

* `graph.html`：可以在浏览器中查看项目关系图；
* `GRAPH_REPORT.md`：项目结构和重点说明；
* `graph.json`：供 AI 后续查询的完整知识图谱。

## 如何使用？

生成图谱后，可以让 AI 查询：

```text
请使用 Graphify 解释这个项目的核心结构。
```

也可以在终端中使用：

```bash
graphify explain "UserService"
```

查询两个模块之间的关系：

```bash
graphify path "UserService" "Database"
```

Graphify 更适合文件较多、结构较复杂的项目。对于只有几个文件的小项目，直接让 AI 阅读代码通常已经足够。

## 项目地址

https://github.com/Graphify-Labs/graphify
