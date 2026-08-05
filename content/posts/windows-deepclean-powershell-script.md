+++
title = "Windows 深度清理脚本怎么用？Light-Help 两个版本区别与风险说明"
date = "2026-08-05T22:53:00+08:00"
draft = false
featured = true
categories = ["软件"]
tags = ["Windows 深度清理脚本", "Light-Help", "PowerShell 清理缓存", "Windows 缓存清理", "开源工具"]
+++

> **内容说明：** 本文根据 Light-Help 项目公开源码整理，主要分析 DeepClean 两个脚本的清理逻辑和潜在风险。当前未提供完整本地实测数据，实际可释放空间取决于电脑中的缓存数量、软件使用情况和系统环境。

Light-Help 项目提供了两条 PowerShell 命令，用于扫描并清理 Windows 中的临时文件、缓存、崩溃转储和部分日志。

它的优点是无需安装额外清理软件，直接通过 Windows 自带的 PowerShell 即可运行。但“一行代码”并不代表它只是执行一个简单的系统命令：这条命令会从 GitHub 下载脚本，然后立即在本机执行。

![Windows 深度清理脚本怎么用？Light-Help 两个版本区别与风险说明](/uploads/2026/08/6b743b51-d8d3-4183-908d-5563b4323bfc-274638b8.jpg)

因此，在运行之前，最好先了解脚本会删除哪些目录，以及“极致清理版”和“v8.0 平衡保护版”究竟有什么差别。

## Light-Help DeepClean 是什么

Light-Help 是一个收集多种 PowerShell 辅助脚本的 GitHub 项目，其中 DeepClean 用于清理 Windows 用户目录和部分系统目录。

![Windows 深度清理脚本怎么用？Light-Help 两个版本区别与风险说明](/uploads/2026/08/QQ20260805-225616-ec25bf17.png)

项目目前提供两个版本：

| 版本                   | 主要特点                   | 风险程度        |
| -------------------- | ---------------------- | ----------- |
| DeepClean 极致清理版      | 扫描范围更广，没有针对常用软件设置排除名单  | 较高          |
| DeepClean v8.0 平衡保护版 | 增加常用浏览器、笔记和办公软件的路径排除规则 | 相对较低，但并非零风险 |

这两个命令本身都是“加载器”。它们会从 GitHub 主分支下载真正的清理脚本，保存到临时目录，再通过 [Windows PowerShell](/tags/windows-powershell/) 执行；加载器还使用了 `ExecutionPolicy Bypass` 参数绕过本次脚本执行策略。

![Windows 深度清理脚本怎么用？Light-Help 两个版本区别与风险说明](/uploads/2026/08/QQ20260805-225636-1b065e50.png)

## Windows 深度清理脚本会删除什么

根据目前公开的脚本内容，DeepClean 会从当前用户目录开始递归扫描文件夹。

![Windows 深度清理脚本怎么用？Light-Help 两个版本区别与风险说明](/uploads/2026/08/QQ20260805-225647-25cd9376.png)

当文件夹名称匹配以下关键词时，会被视为清理目标：

```text
Temp
Cache
CrashDumps
LogFiles
```

找到目标后，脚本会计算其中的文件容量，然后通过 `Remove-Item` 删除该目录下的内容。

它还会尝试清理以下系统路径：

```text
当前用户临时目录
C:\Windows\Temp
C:\Windows\Prefetch
C:\Windows\SoftwareDistribution\Download
```

其中包括用户临时文件、Windows 临时文件、预读取文件和 Windows Update 已下载的更新缓存。脚本只删除目标文件夹中的内容，不会删除目标文件夹本身。

需要注意，脚本判断目标的主要依据是**文件夹名称**，而不是逐个识别文件的来源、用途和有效期。

例如，一个第三方软件只要把重要的离线文件放在名为 `Cache` 的目录中，就可能进入清理范围。缓存通常可以重新生成，但缓存目录中也可能包含离线内容、下载资源、索引或尚未同步的数据。

## 两个版本有什么区别

### 极致清理版

极致清理版使用下面的命令：

```powershell
iwr -useb https://raw.githubusercontent.com/Cotton059/Light-Help/main/DeepClean_Tool.ps1 | iex
```

其中：

* `iwr` 是 `Invoke-WebRequest` 的别名，用于下载远程内容；
* `-useb` 表示使用基础解析模式；
* `iex` 是 `Invoke-Expression` 的别名，用于立即执行下载的文本。

该版本会递归扫描当前用户目录，只要目录名称包含目标关键词，就会将其加入清理列表。

它没有针对浏览器、笔记软件、云盘或办公软件设置专门的排除规则，因此清理范围更大，误删缓存或离线数据的可能性也更高。

原始说明提到，它可能导致部分云服务软件重新同步。更准确地说，实际影响取决于软件把哪些数据放在缓存目录中：轻则重新生成缩略图和索引，重则需要重新下载离线文件。

### v8.0 平衡保护版

v8.0 使用下面的命令：

```powershell
iwr -useb https://raw.githubusercontent.com/Cotton059/Light-Help/main/DeepClean_v8.0_Tool.ps1 | iex
```

相较于极致版，v8.0 增加了路径关键词保护列表。目前源码中包含：

```text
Chrome
Edge
Firefox
Brave
Notion
Obsidian
Evernote
OneNote
Microsoft
Adobe
Office
Code
Discord
```

扫描到路径中包含这些关键词时，脚本会跳过该目录及其子目录，避免继续查找其中的 `Cache`、`Temp` 等文件夹。

这种设计确实可以降低部分常用软件缓存被清空的概率，但它仍有几个限制。

第一，它是按路径文字匹配，而不是识别软件的真实数据结构。

第二，保护列表不可能覆盖所有软件，例如其他浏览器、网盘客户端、专业设计软件和开发工具未必都在名单中。

第三，`Microsoft` 这样的关键词范围很大，可能同时跳过一些原本可以安全清理的目录，导致清理不够彻底。

因此，v8.0 更适合作为相对保守的版本，但不应被理解为“完全不会影响软件数据”。

## 建议优先使用哪个版本

对普通用户来说，更建议优先考虑 v8.0 平衡保护版。

以下情况不建议直接使用极致清理版：

* 电脑中安装了多个云盘或同步软件；
* 使用 Notion、Obsidian 等工具保存离线数据；
* 浏览器中保存了大量离线网页或应用数据；
* 开发环境依赖本地包缓存；
* 不清楚软件数据保存在什么位置；
* 电脑中有尚未完成同步的重要文件。

即使使用 v8.0，也建议先退出浏览器、云盘、办公软件和开发工具，并确认重要资料已经完成同步或备份。

## 为什么不建议直接复制远程命令运行

下面这种写法虽然方便，但存在一个容易被忽略的问题：

```powershell
iwr -useb 远程脚本地址 | iex
```

它会下载并立即执行 GitHub 主分支当前返回的内容。用户看到文章时的源码，与实际运行时下载到的源码可能已经不同。

Light-Help 的加载器不仅会下载后续脚本，还会用以下方式启动它：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "脚本路径"
```

这并不等于脚本本身一定不安全，但意味着系统不会通过常规执行策略阻止此次运行。

更稳妥的做法是先把脚本下载到本地，查看内容后再执行。

## 更安全的运行方法

### 第一步：打开 PowerShell

按下：

```text
Windows + X
```

选择“终端”或“Windows PowerShell”。

建议先不要使用管理员权限。普通权限下，脚本无法清理部分系统目录，但风险相对更低。

只有确认需要清理系统临时目录时，再考虑以管理员身份运行。

### 第二步：下载脚本而不是立即执行

下面以 v8.0 加载器为例。

该命令只把文件下载到当前用户的“下载”目录，不会立即执行：

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/Cotton059/Light-Help/main/DeepClean_v8.0_Tool.ps1" `
  -OutFile "$HOME\Downloads\DeepClean_v8.0_Tool.ps1"
```

运行位置：PowerShell。

管理员权限：不需要。

执行结果：在下载目录生成一个 PowerShell 脚本文件。

### 第三步：查看脚本内容

可以使用记事本打开：

```powershell
notepad "$HOME\Downloads\DeepClean_v8.0_Tool.ps1"
```

不过这里还需要注意：下载到的 `DeepClean_v8.0_Tool.ps1` 只是加载器，它还会继续下载真正的 `DeepClean_v8.0.ps1`。

因此，最好连核心脚本也一并下载检查：

```powershell
Invoke-WebRequest `
  -Uri "https://raw.githubusercontent.com/Cotton059/Light-Help/main/DeepClean_v8.0.ps1" `
  -OutFile "$HOME\Downloads\DeepClean_v8.0.ps1"
```

然后打开查看：

```powershell
notepad "$HOME\Downloads\DeepClean_v8.0.ps1"
```

重点检查以下内容：

```text
$protectedSuites
$targetKeywords
$systemJunkPaths
Remove-Item
```

它们分别决定保护哪些路径、匹配哪些目录、清理哪些系统位置，以及最终执行什么删除操作。

### 第四步：确认后再运行

确认脚本内容没有发生异常变化后，可以在 PowerShell 中运行本地文件：

```powershell
& "$HOME\Downloads\DeepClean_v8.0.ps1"
```

首次运行时，脚本会询问是否开始扫描。扫描结束后，还会再次询问是否执行清理。

不过，两次确认的默认选项都是 `Y`。看到确认提示时直接按回车，就会继续执行。因此不要在未查看扫描结果的情况下连续按回车。

## 运行前需要做什么

运行前至少完成以下准备：

1. 保存正在编辑的文件；
2. 退出浏览器、云盘和办公软件；
3. 等待 OneDrive、Dropbox 等同步任务完成；
4. 备份重要的桌面、文档和项目目录；
5. 创建 Windows 系统还原点；
6. 确保系统盘仍有一定剩余空间，避免清理过程中系统异常。

还需要明确一点：系统还原点主要保护系统配置，并不等于完整备份个人文件。重要资料仍应单独复制到其他磁盘或可靠的备份位置。

## 清理后可能出现的情况

执行完成后，可能出现以下现象：

### 第一次启动软件变慢

浏览器、开发工具和其他软件可能需要重新建立缓存，因此第一次打开会比平时慢。

### 软件重新下载资源

如果被清理的是离线缓存，软件可能重新下载图片、网页资源、模型文件或其他数据。

### Windows Update 重新下载更新包

清空：

```text
C:\Windows\SoftwareDistribution\Download
```

后，尚未安装或需要重新验证的系统更新文件可能再次下载。

### 搜索、缩略图或索引重新生成

部分缓存被删除后，Windows 或第三方软件可能重新建立索引和预览数据。

### 释放空间没有预期中多

脚本只处理名称匹配的缓存和临时目录，并不会自动查找视频、安装包、虚拟机磁盘、旧备份等真正占用大量空间的个人文件。

如果磁盘空间主要被大型文件、游戏或虚拟机占用，运行该脚本可能只能释放少量空间。

## 它不能替代 Windows 存储管理

DeepClean 更适合处理散落在用户目录中的缓存文件，但它无法替代完整的磁盘空间分析。

如果系统盘空间不足，建议先打开：

```text
设置 → 系统 → 存储
```

检查“临时文件”“已安装的应用”“其他”“桌面”和“文档”等分类。

Windows 自带的“存储感知”可以定期处理部分临时文件，操作范围也更加透明。对于普通用户，建议先使用系统自带功能，确认仍有无法定位的缓存空间后，再考虑第三方脚本。

## 是否值得使用

从脚本设计来看，DeepClean 的价值在于自动扫描用户目录中名称包含 `Temp`、`Cache`、`CrashDumps` 和 `LogFiles` 的文件夹，省去手动逐个寻找缓存目录的过程。

但它的清理判断相对简单，并不能准确区分“可以随时删除的缓存”和“软件依赖的离线数据”。

因此：

* 熟悉 PowerShell、能阅读脚本并有备份的用户，可以在检查源码后尝试 v8.0；
* 普通用户应优先使用 Windows 自带的存储清理功能；
* 有大量云盘、开发环境或专业软件数据的电脑，不建议直接运行极致版；
* 生产电脑、公司电脑和保存重要项目的设备，不建议在没有完整备份时执行。

## 总结

Light-Help Windows 深度清理脚本确实可以自动清理多种缓存、临时文件、日志和系统更新下载内容，但能释放多少空间没有固定答案。

极致清理版扫描范围更大，也更容易影响第三方软件缓存；v8.0 通过关键词排除部分常用软件目录，风险相对较低，但保护名单并不完整。

比“一键运行”更重要的是先看清脚本内容。建议下载源码、检查目标目录、备份重要数据，再决定是否执行。对于不熟悉 PowerShell 的用户，Windows 自带的存储清理仍然是更稳妥的第一选择。
