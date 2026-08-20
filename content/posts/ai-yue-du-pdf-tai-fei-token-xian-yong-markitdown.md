+++
title = "AI 阅读 PDF 太费 Token？先用 MarkItDown 转成 Markdown"
date = "2026-08-05T13:27:00+08:00"
draft = false
description = "直接上传长篇 PDF 可能夹带页眉、页脚和复杂排版信息，增加 AI 的解析难度。本文介绍微软开源工具 MarkItDown 的安装与使用方法，演示如何先将 PDF 转成 Markdown，再进行内容清理、章节拆分、AI 总结和知识库导入，同时说明扫描件、复杂表格和多栏论文的转换限制。"
categories = ["AI & Automation"]
tags = ["AI读取PDF", "AI节省Token", "Markdown文档转换", "AI知识库"]
+++

直接把几十页甚至上百页的 PDF 上传给 [AI](/tags/ai/)，虽然方便，但不一定是最高效的处理方式。

PDF 本质上是一种面向打印和页面展示的格式。除了正文，它还可能包含页眉、页脚、页码、分栏、坐标定位、重复标题、隐藏文本和复杂表格等信息。AI 在解析文档时，可能需要额外处理这些排版结构，从而增加上下文长度和处理难度。

一种更适合长文档的工作流是：

> 先把 PDF 转成 Markdown，再让 AI 总结、问答或提取信息。


![AI 阅读 PDF 太费 Token？先用 MarkItDown 转成 Markdown](/uploads/2026/08/13_28_58-d3b95c03.jpg)


## 为什么 Markdown 更适合交给 AI？

Markdown 是结构清晰的纯文本格式，可以用简单符号保留文档中的重要层级，例如：

* 标题和章节
* 正文段落
* 有序列表和无序列表
* 表格
* 链接
* 代码块

与 PDF 相比，Markdown 通常会去掉大量只服务于页面展示的布局信息，让 AI 更容易识别文章结构。

这样做可能带来几个好处：

1. **减少无关排版信息**

   页码、重复页眉和定位信息可能在转换时被简化，输入内容更加干净。

2. **方便拆分长文档**

   可以按照一级标题、二级标题或者章节拆分 Markdown，分批交给 AI，避免一次提交整本 PDF。

3. **便于搜索和引用**

   Markdown 可以直接使用文本编辑器搜索，也适合导入 [Obsidian](/tags/obsidian/)、知识库或 RAG 系统。

4. **方便检查转换结果**

   在发送给 AI 之前，可以手动删除目录、版权页、重复页脚和无关章节。

需要注意的是，转换成 Markdown **不代表一定会减少 [Token](/tags/token/)**。最终消耗仍取决于转换后的文字长度、表格复杂度、OCR 结果以及你发送给 AI 的具体内容。

## MarkItDown 是什么？

MarkItDown 是微软开源的一款 Python 工具，可以把多种文件转换成 Markdown，主要面向文本分析、内容索引和大语言模型处理场景。

目前项目支持的格式包括：

* PDF
* Word：DOCX
* PowerPoint：PPTX
* Excel：XLSX、XLS
* HTML
* CSV、JSON、XML
* EPUB
* ZIP 压缩包
* 图片和音频等文件

不同格式可能需要安装对应的可选依赖。项目也提供了插件机制，可扩展 OCR 等能力。

## 安装 MarkItDown

电脑需要先安装 Python，然后在终端中运行：

```bash
pip install "markitdown[all]"
```

`[all]` 会安装全部常用格式所需的依赖。

如果只需要转换 PDF，也可以只安装 PDF 相关组件：

```bash
pip install "markitdown[pdf]"
```

## 将 PDF 转换成 Markdown

进入 PDF 所在目录，运行：

```bash
markitdown document.pdf -o document.md
```

其中：

* `document.pdf` 是原始 PDF 文件
* `document.md` 是转换后生成的 Markdown 文件

转换完成后，可以使用 [VS Code](/tags/vs-code/)、Obsidian、Typora 或普通文本编辑器打开 `.md` 文件。

## 使用 Python 批量处理

需要集成到脚本或自动化流程时，可以使用 Python API：

```python
from markitdown import MarkItDown

converter = MarkItDown()
result = converter.convert("document.pdf")

with open("document.md", "w", encoding="utf-8") as file:
    file.write(result.text_content)
```

这段代码会读取 `document.pdf`，并将转换结果保存为 `document.md`。

## 推荐的 AI 阅读 PDF 工作流

处理较长的 PDF 时，可以按照下面的步骤操作：

### 第一步：转换格式

```bash
markitdown document.pdf -o document.md
```

### 第二步：检查转换结果

重点检查：

* 标题层级是否正确
* 表格是否错位
* 页眉、页脚是否重复
* 是否存在乱码
* 图片中的文字是否被遗漏
* 多栏排版顺序是否正确

### 第三步：删除无关内容

可以删除：

* 封面和版权声明
* 重复目录
* 每页重复出现的页眉和页脚
* 与问题无关的附录
* 大量无意义的 OCR 字符

### 第四步：按章节交给 AI

不要一次粘贴整个文档，可以先让 AI 读取目录，再按章节处理。

例如：

```text
下面是文档的第一章。请提取核心观点、关键数据和结论。
不要补充原文中没有的信息，并保留重要术语。
```

处理技术文档时，也可以使用：

```text
请根据下面的 Markdown 内容回答问题。
引用结论时注明对应的章节标题；无法从原文确认的信息，请明确说明。
```

## 哪些 PDF 适合使用 MarkItDown？

MarkItDown 更适合：

* 文字型电子书
* 产品说明书
* 普通研究报告
* 合同和规章制度
* Word 导出的 PDF
* 结构相对简单的论文
* 需要导入 AI 知识库的资料

## 哪些 PDF 可能转换效果不好？

以下类型需要谨慎检查：

* 扫描版 PDF
* 双栏或多栏论文
* 大量公式的学术文档
* 表格特别复杂的财务报告
* 图片中包含大量文字的文件
* 页面结构非常复杂的杂志
* 依赖图表位置才能理解的资料

MarkItDown 的 PDF 转换并不能保证完整还原复杂版式。项目维护者也曾说明，部分 PDF 的基础转换能力相对有限；对于复杂表格、扫描文件和学术排版，转换后可能需要手动整理，或者改用带版面识别和 OCR 能力的工具。

因此，不建议转换完成后直接删除原始 PDF。涉及合同、财务数据、论文公式或法律文件时，应同时对照原文核验。

## 总结

将 PDF 转成 Markdown，并不是单纯更换文件后缀，而是把面向页面展示的文档，整理成更适合 AI 阅读和检索的结构化文本。

对于文字较多、结构清晰的 PDF，这种方式可以减少排版干扰，并方便拆分章节、清理内容、建立知识库和进行多轮问答。

实际使用时可以记住三个步骤：

> PDF 转 Markdown → 清理无关内容 → 按章节交给 AI

这样通常比直接上传整份长 PDF 更容易控制上下文，也更方便检查 AI 的回答是否来自原文。

## 项目地址

* GitHub：[Microsoft MarkItDown](https://github.com/microsoft/markitdown)
* Python 软件包：[MarkItDown on PyPI](https://pypi.org/project/markitdown/)
