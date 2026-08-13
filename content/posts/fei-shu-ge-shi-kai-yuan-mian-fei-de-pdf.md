+++
title = "飞鼠格式是什么？开源免费的 PDF、文档与音视频格式转换工具"
date = "2026-08-13T22:37:00+08:00"
draft = false
description = "内容说明： 本文根据 FlyingMouse Format 官方 GitHub 资料整理，主要介绍功能、适用场景和已知限制，并非完整实测文章。"
featured = true
categories = ["软件"]
tags = ["飞鼠格式", "文件格式转换工具", "PDF转Word", "NCM转MP3", "开源工具"]

[download]
enabled = true
url = "https://github.com/LaoFeng-mouse/flyingmouse-format"
format = "EXE"
size = "617 MB"
source = ""
code = ""
+++

飞鼠格式（FlyingMouse Format）是一款开源文件转换工具，主要解决 PDF、Office 文档、图片、音视频等格式互转问题。

它比较特别的地方，是除了常见格式外，还支持 NCM、mflac、mgg、KGMA 等部分音乐客户端文件转换。大部分普通文件处理在本地完成，适合不想频繁使用在线转换网站的用户。

## 飞鼠格式支持哪些文件？

目前项目说明列出的主要能力包括：

* JPG、PNG、[WebP](/tags/webp/)、HEIC、RAW 等图片转换；
* Word、Excel、PPT、WPS、TXT、Markdown；
* PDF 转 Word、Excel、图片、TXT；
* 图片 OCR 文字识别；
* 音频、视频格式互转；
* NCM、mflac、mgg、KGMA 等音乐格式；
* EPUB、MOBI 等部分电子书格式；
* 批量文件转换。

项目整合了 [FFmpeg](/tags/ffmpeg/)、LibreOffice、Poppler、Tesseract、pdf2docx 等组件，本质上是把多个转换工具集中到一个图形界面中。

![飞鼠格式是什么？开源免费的 PDF、文档与音视频格式转换工具](/uploads/2026/08/e8e87015-aa07-40ef-8976-83f4abb86d33-ccf60f28.jpg)

## PDF 转 Word 能保留排版吗？

飞鼠格式使用 pdf2docx 处理 PDF 转 Word，项目说明中提到会尽量保留段落、表格、图片、字体和布局，扫描版 PDF 还可以通过 OCR 识别文字。

但这里不要理解成“复杂 PDF 一定可以完整还原”。

遇到多栏排版、复杂表格、特殊字体或大量公式时，转换结果仍然需要实际测试。

## 支持部分加密音乐格式转换

飞鼠格式支持处理：

* 网易云音乐 NCM；
* QQ 音乐 mflac、mgg；
* 酷狗 KGMA；
* 部分 mmp4、musicex 文件。

可以转换为 MP3、FLAC、WAV、M4A 等常见格式。

![飞鼠格式是什么？开源免费的 PDF、文档与音视频格式转换工具](/uploads/2026/08/home-7fe14b6c.png)

不过并非所有音乐格式都完全离线处理。例如部分新版 QQ 音乐 musicex 文件，可能需要联网获取解密所需信息。

另外，只建议转换自己合法获得并有权处理的文件。

## 是否完全离线？

普通文档、图片、PDF、音视频转换主要在本地完成，不需要把文件上传到在线转换服务器。

这一点比较适合处理合同、报价单、内部 Excel 等不方便上传第三方网站的文件。

但部分音乐解密功能可能需要联网，所以不能简单理解成“所有功能完全离线”。

## 支持哪些系统？

目前官方提供：

* [Windows](/tags/windows/) 10 / 11 x64；
* Windows 7 SP1 兼容版；
* macOS Apple Silicon；
* macOS Intel。

Windows 7 使用较旧的 Electron 环境，安全维护已经停止，更建议在 Windows 10 / 11 上使用。

另外，目前 Windows 安装包没有数字签名，安装时可能出现 SmartScreen 提示。

## 适合哪些用户？

如果你经常处理 PDF、Office 文档、图片、视频、OCR，或者偶尔需要转换 NCM 等音乐文件，飞鼠格式的优势比较明显。

它最大的价值不是某一种转换能力特别突出，而是把多个常见文件处理功能放到一个工具里，减少来回安装不同软件的麻烦。

如果只是偶尔转换一张图片，则没有太大必要专门安装。

## 使用前需要注意

目前主要限制包括：

1. 复杂 PDF 转 Word 不保证完整还原；
2. 部分电子书转换仍属于实验功能；
3. 某些 QQ 音乐格式需要联网；
4. 音乐客户端格式可能随版本变化；
5. Windows 安装包目前没有代码签名。

## 总结

飞鼠格式适合经常处理多种文件格式、又希望尽量在本地完成转换的用户。

它覆盖 PDF、Office、图片、OCR、音视频和部分音乐客户端格式，功能范围比较广。

如果你主要看重 **PDF 转 Word、本地文件转换和 NCM 等音乐格式处理**，可以从官方 GitHub 下载后根据自己的文件实际测试。
