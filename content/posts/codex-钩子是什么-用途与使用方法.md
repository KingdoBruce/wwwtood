+++
title = "Codex 钩子是什么？用途与使用方法"
date = "2026-07-24T17:55:00+08:00"
draft = false
featured = true
tags = ["ChatGPT", "Codex", "钩子"]
+++

在 ChatGPT 的 [Codex](/tags/codex/) 设置中，你可能会看到一个名为“钩子”的页面。

这里的钩子，英文叫 **Hooks**。它不是聊天记忆，也不是定时任务，而是一套给 Codex 使用的自动触发机制。


![2a132536-a6ab-45c9-bcc5-2c945898f266](/uploads/2026/07/2a132536-a6ab-45c9-bcc5-2c945898f266-c989dc4e.png)


简单理解就是：

> 当 Codex 执行到某个步骤时，自动运行你提前设置好的脚本。

例如，Codex 准备执行命令时，可以先检查命令是否危险；修改代码后，可以自动运行测试；会话结束时，也可以自动保存日志或整理交接信息。

---

## 钩子可以做什么？

钩子常见的用途包括：

* 执行命令前检查危险操作；
* 防止用户误贴 API Key；
* 修改代码后自动运行测试；
* 检查代码格式是否符合规范；
* 会话开始时加载项目说明；
* 上下文压缩前保存重要信息；
* 会话结束时生成日志或清理临时文件。

Codex 官方支持多个生命周期节点，包括 `SessionStart`、`PreToolUse`、`PostToolUse`、`UserPromptSubmit`、`PreCompact`、`Stop` 和 `SessionEnd` 等。([OpenAI Developers][1])

---

## 常见钩子类型

### `SessionStart`

在 Codex 会话开始、恢复或清空后触发。

适合自动加载：

* 项目开发规范；
* 环境说明；
* 当前任务进度；
* 必须遵守的注意事项。

### `PreToolUse`

在 Codex 调用工具之前触发。

例如，Codex 准备执行 Bash 命令时，可以先检查：

```bash
rm -rf
```

如果脚本判断命令危险，就可以阻止执行。`PreToolUse` 能拦截 Bash、文件修改和部分 [MCP](/tags/mcp/) 工具调用。([OpenAI Developers][1])

### `PostToolUse`

在命令或工具执行结束后触发。

适合：

* 检查命令返回结果；
* 自动记录日志；
* 发现测试失败后提醒 Codex；
* 修改文件后运行格式检查。

需要注意，`PostToolUse` 是在操作已经执行后运行，因此它无法撤销已经产生的文件修改或其他副作用。([OpenAI Developers][1])

### `UserPromptSubmit`

在用户的提示词正式提交给模型前触发。

可以用来：

* 检查提示词中是否包含密码或密钥；
* 自动补充开发规范；
* 对不清楚的需求增加提醒；
* 阻止某些不符合要求的提示词。

该钩子能够读取即将提交的 `prompt` 内容，并可以添加额外上下文或阻止提交。([OpenAI Developers][1])

### `SessionEnd`

当主会话正式结束时触发。

适合：

* 保存最后的工作记录；
* 清理临时文件；
* 记录会话结束状态；
* 生成简单的交接信息。

不过它属于结束后的辅助操作，无法继续控制已经结束的对话。([OpenAI Developers][1])

---

# 钩子配置放在哪里？

Codex 可以从以下位置读取钩子：

```text
~/.codex/hooks.json
~/.codex/config.toml
项目目录/.codex/hooks.json
项目目录/.codex/config.toml
```

前两种属于用户级配置，会影响你打开的多个项目。

后两种属于项目级配置，只对当前项目生效。项目级钩子只有在该项目被信任后才会加载。([OpenAI Developers][1])

对于普通用户，更推荐使用：

```text
项目目录/.codex/hooks.json
```

这样配置不会影响其他项目，也方便随项目一起管理。

---

# 一个最简单的钩子示例

下面创建一个非常基础的钩子：

> 每次 Codex 会话开始时，提醒它先阅读项目规范。

## 第一步：创建目录

在项目根目录创建：

```text
.codex
```

目录结构如下：

```text
你的项目/
├─ .codex/
│  ├─ hooks.json
│  └─ hooks/
│     └─ session_start.py
├─ AGENTS.md
└─ 其他项目文件
```

---

## 第二步：创建脚本

创建文件：

```text
.codex/hooks/session_start.py
```

写入下面的内容：

```python
import json
import sys


def main() -> None:
    # Codex 会通过标准输入传入钩子事件信息。
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        pass

    result = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "开始处理项目之前，请先阅读项目根目录中的 "
                "AGENTS.md，并遵守其中的开发规范。"
            ),
        }
    }

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

Codex 的命令型钩子会通过标准输入接收一个 JSON 对象，其中通常包含当前目录、会话编号、事件名称和模型信息。([OpenAI Developers][1])

---

## 第三步：创建 hooks.json

在：

```text
.codex/hooks.json
```

中写入：

```json
{
  "description": "当前项目的 Codex 自动化钩子",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "python .codex/hooks/session_start.py",
            "statusMessage": "正在加载项目开发规范",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

这里各项含义如下：

```text
SessionStart
```

表示在会话开始时运行。

```text
matcher
```

表示哪些启动方式能够触发钩子。

```text
command
```

表示需要运行的脚本。

```text
statusMessage
```

表示运行钩子时显示的提示。

```text
timeout
```

表示脚本最长允许运行多少秒。

---

# Windows 用户需要注意

在 Windows 中，如果 `python` 命令不能使用，可以改成：

```json
"command": "py .codex/hooks/session_start.py"
```

或者使用 Python 的完整路径：

```json
"command": "C:\\Python312\\python.exe .codex\\hooks\\session_start.py"
```

项目可能从子目录启动，正式使用时最好通过项目根目录定位脚本，避免相对路径失效。官方文档也建议项目钩子尽量从 Git 根目录解析脚本位置。([OpenAI Developers][1])

---

# 如何启用和检查钩子？

保存文件后，重新打开 Codex。

然后在 Codex CLI 中输入：

```text
/hooks
```

你可以在这里：

* 查看已经发现的钩子；
* 查看钩子来自哪个配置文件；
* 信任新钩子；
* 禁用某个钩子；
* 重新启用钩子。

出于安全原因，普通命令钩子在首次运行前需要用户检查并信任。钩子内容发生改变后，Codex 会重新要求确认。([OpenAI Developers][1])

因此，看到“未找到钩子”，只是表示当前没有安装或配置可用钩子，并不是程序发生故障。

---

# 再举一个实用例子：修改代码后提醒运行测试

创建：

```text
.codex/hooks/post_edit.py
```

写入：

```python
import json
import sys


def main() -> None:
    data = json.load(sys.stdin)
    tool_name = data.get("tool_name", "")

    if tool_name == "apply_patch":
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "代码文件刚刚发生修改。继续任务前，请检查 Git diff，"
                    "并运行与本次修改相关的测试。"
                ),
            }
        }

        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

然后把 `hooks.json` 修改为：

```json
{
  "description": "当前项目的 Codex 自动化钩子",
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "python .codex/hooks/session_start.py",
            "statusMessage": "正在加载项目规范",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "apply_patch",
        "hooks": [
          {
            "type": "command",
            "command": "python .codex/hooks/post_edit.py",
            "statusMessage": "正在检查代码修改",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

这样 Codex 修改文件后，钩子会提醒它检查差异并运行测试。

---

# 如何关闭钩子？

临时禁用单个钩子，可以在 Codex 中输入：

```text
/hooks
```

然后选择对应钩子并禁用。

要彻底关闭所有生命周期钩子，可以打开：

```text
~/.codex/config.toml
```

加入：

```toml
[features]
hooks = false
```

Codex 的钩子功能默认启用，上面的配置会关闭所有钩子。([OpenAI Developers][1])

---

# 使用钩子需要注意什么？

钩子本质上可以执行本地脚本，因此不要随意信任来历不明的钩子。

尤其要检查：

* 是否包含删除文件的命令；
* 是否上传本地代码；
* 是否读取环境变量和 API Key；
* 是否自动运行网络请求；
* 是否安装未知软件；
* 是否使用管理员权限；
* 是否修改 Git 仓库以外的文件。

多个符合条件的命令钩子可能同时运行，而且一个钩子不一定能阻止另一个钩子开始执行。官方因此要求非托管钩子在首次运行及修改后重新接受信任检查。([OpenAI Developers][1])

---

# 总结

Codex 钩子可以理解为一套自动化规则：

```text
发生某个事件
        ↓
自动运行指定脚本
        ↓
检查、提醒、补充信息或阻止操作
```

它最适合用来完成：

* 自动加载项目规范；
* 阻止危险命令；
* 修改后自动检查；
* 自动运行测试；
* 保存日志和项目状态。

普通用户不配置钩子，也可以正常使用 Codex。只有当你希望 Codex 的工作流程更加固定、安全和自动化时，才需要使用它。
