+++
title = "Windows AI 工具反复报错？安装 PowerShell 7，减少无效重试和 Token 浪费"
date = "2026-08-02T22:02:00+08:00"
draft = false
featured = true
categories = ["AI"]
tags = ["PowerShell 7", "Windows PowerShell", "AI Token", "AI Agent", "Windows 11", "WinGet", "VS Code", "Cursor", "Codex"]
+++

在 Windows 上使用 [Codex](/tags/codex/)、[Claude](/tags/claude/) Code、[Cursor](/tags/cursor/) 或其他 [AI](/tags/ai/) 编程工具时，你可能遇到过这种情况：

```text
执行命令
→ PowerShell 报错
→ AI 修改命令
→ 再次报错
→ AI 继续猜测和重试
```

每次重新读取错误、分析原因和修改命令，都会额外消耗 [Token](/tags/token/)。

这并不一定是 AI 能力有问题。其中一个常见原因是：**[AI Agent](/tags/ai-agent/) 生成的命令与当前 PowerShell 版本或终端环境不兼容。**

Windows 10 和 Windows 11 通常仍然自带 Windows PowerShell 5.1，而不少现代开发工具和 AI Agent 更适合在 PowerShell 7 中运行。

> 注意：安装 PowerShell 7 不能解决所有命令错误，但可以减少一部分由 PowerShell 版本、命令参数和运行环境不一致引起的无效重试。

![Windows AI 工具反复报错？安装 PowerShell 7，减少无效重试和 Token 浪费](/uploads/2026/08/23_08_32301_1-85cb7eaa.jpg)

## 一、检查当前 PowerShell 版本

在 PowerShell 中运行：

```powershell
$PSVersionTable
```

重点查看：

```text
PSVersion
PSEdition
```

如果显示类似下面的内容：

```text
PSVersion  5.1
PSEdition  Desktop
```

说明当前窗口运行的是系统自带的 Windows PowerShell 5.1。

## 二、使用 WinGet 安装 PowerShell 7

以管理员身份打开 PowerShell，然后运行：

```powershell
winget install --id Microsoft.PowerShell --source winget
```

安装过程中，WinGet 会自动下载并安装适合当前系统的 PowerShell 7。

如果提示已经安装，可以执行升级命令：

```powershell
winget upgrade --id Microsoft.PowerShell --source winget
```

## 三、为什么安装后仍然显示 PowerShell 5.1？

PowerShell 7 不会覆盖 Windows PowerShell 5.1。

两者的启动程序不同：

| 版本                     | 启动程序             |
| ---------------------- | ---------------- |
| Windows PowerShell 5.1 | `powershell.exe` |
| PowerShell 7           | `pwsh.exe`       |

因此，安装完成后继续在原来的窗口运行：

```powershell
$PSVersionTable
```

可能仍然显示 5.1，这是正常现象，并不代表安装失败。

请关闭原来的终端窗口，重新打开终端，然后执行：

```powershell
pwsh
```

再次检查版本：

```powershell
$PSVersionTable
```

正常情况下会看到：

```text
PSVersion  7.x
PSEdition  Core
```

还可以直接检查：

```powershell
pwsh --version
```

## 四、将 Windows Terminal 默认终端改为 PowerShell 7

只安装 PowerShell 7 还不够。为了避免以后仍然打开 Windows PowerShell 5.1，建议修改默认终端。

操作步骤：

1. 打开 Windows Terminal。
2. 点击顶部的下拉箭头。
3. 进入“设置”。
4. 找到“默认配置文件”。
5. 选择“PowerShell”，不要选择“Windows PowerShell”。
6. 保存设置并重新打开终端。

注意区分：

```text
PowerShell           → 通常是 PowerShell 7
Windows PowerShell   → 系统自带的 PowerShell 5.1
```

## 五、让 VS Code 默认使用 PowerShell 7

在 VS Code 中按下：

```text
Ctrl + Shift + P
```

搜索并选择：

```text
Terminal: Select Default Profile
```

然后选择：

```text
PowerShell
```

重新创建终端：

```text
Terminal: Create New Terminal
```

在新终端中运行：

```powershell
$PSVersionTable
```

确认当前版本已经是 PowerShell 7。

## 六、让 AI Agent 明确调用 PowerShell 7

有些 AI 工具不会自动使用 Windows Terminal 的默认配置，而是直接调用系统里的 `powershell.exe`。

这时可以在 AI 工具的终端或 Shell 设置中，将执行程序改为：

```text
pwsh.exe
```

PowerShell 7 的常见安装路径是：

```text
C:\Program Files\PowerShell\7\pwsh.exe
```

也可以在终端中查找实际路径：

```powershell
Get-Command pwsh
```

如果 AI 工具支持项目规则或长期指令，可以加入：

```text
在 Windows 环境执行终端命令时，优先使用 PowerShell 7（pwsh），不要默认调用 Windows PowerShell 5.1（powershell.exe）。
```

## 七、快速验证是否配置成功

运行以下命令：

```powershell
pwsh --version
```

然后运行：

```powershell
$PSVersionTable.PSVersion
```

再检查程序路径：

```powershell
Get-Command pwsh
```

只要能够正常显示 PowerShell 7 的版本号和安装路径，说明安装基本完成。

## 常见问题

### 安装 PowerShell 7 后，可以删除 PowerShell 5.1 吗？

不建议。

PowerShell 7 与 Windows PowerShell 5.1 可以同时存在。部分旧版 Windows 管理模块和脚本仍可能依赖 PowerShell 5.1。

### 为什么 AI 工具仍然调用 PowerShell 5.1？

常见原因包括：

* AI 工具固定调用了 `powershell.exe`；
* VS Code 默认终端尚未修改；
* 安装后没有重新启动终端；
* AI 工具保留了旧的终端会话；
* Shell 配置仍然指向 Windows PowerShell。

应在对应工具中明确选择 `pwsh.exe`。

### 安装 PowerShell 7 就一定能减少 Token 消耗吗？

不能保证。

它主要减少因旧版 PowerShell、命令参数或终端环境不一致造成的报错和重复尝试。权限不足、路径错误、依赖缺失、网络异常和代码本身的问题，仍然需要单独排查。

## 总结

对于经常在 Windows 上使用 AI 编程工具的人，推荐完成下面三项设置：

```text
安装 PowerShell 7
→ 将默认终端改为 PowerShell 7
→ 确认 AI Agent 调用的是 pwsh.exe
```

真正关键的不是“电脑里装了 PowerShell 7”，而是**AI 工具实际执行命令时使用了 PowerShell 7**。

正确配置终端环境，可以减少部分无意义的报错、猜测和重复执行，也能避免 Token 浪费在本可提前解决的兼容性问题上。

## PowerShell 官方项目

* GitHub：[PowerShell/PowerShell](https://github.com/PowerShell/PowerShell)
* Windows 安装文档：[在 Windows 上安装 PowerShell](https://learn.microsoft.com/powershell/scripting/install/install-powershell-on-windows)
