+++
title = "Codex 省额度工具包（新手版）"
date = "2026-07-21T18:13:00+08:00"
draft = false
categories = ["AI"]
tags = ["Codex", "Skills"]
featured = true
+++

这套文件不会增加 Codex 额度，也不会改变收费标准。它通过限制无关扫描、无关修改、完整测试和重复解释，减少不必要的 Token 与 credits 消耗。

## 工具包下载

[点击下载 Codex 省额度工具包（新手版）](https://iezyw.lanzouv.com/iUlBr3xtimta)

> 下载完成后，请先解压 ZIP 压缩包，再按照下方步骤安装。

![Codex-](/uploads/2026/07/Codex--5ecf67e2.jpg)

## 最简单的安装方法

### 第一步：解压

解压下载的 ZIP 文件。

### 第二步：复制到项目根目录

把解压后的以下内容复制到你的项目最外层目录：

* `.agents` 文件夹
* `AGENTS.md`
* `PROJECT_STATUS.md`
* `prompts` 文件夹

项目根目录通常是能够看到 `package.json`、`README.md`、`.git` 或源代码文件夹的位置。

复制完成后的结构应类似：

```text
你的项目/
├─ .agents/
│  └─ skills/
│     ├─ project-navigation/
│     ├─ minimal-code-change/
│     ├─ targeted-testing/
│     ├─ diagnose-before-fixing/
│     └─ website-small-task/
├─ prompts/
├─ AGENTS.md
├─ PROJECT_STATUS.md
├─ package.json
└─ src/
```

Windows 默认可能隐藏以点号开头的文件夹。即使看不到 `.agents`，只要复制成功即可。可以在资源管理器中开启“查看 → 显示 → 隐藏的项目”。

## 第三步：编辑 PROJECT_STATUS.md

用记事本或 VS Code 打开 `PROJECT_STATUS.md`，只填写你知道的内容。不知道的地方可以保留。

也可以在 Codex 中粘贴：

```text
请读取当前项目，并只查看项目根目录、package.json、README.md 和主要源码目录。不要扫描整个仓库。然后帮我填写 PROJECT_STATUS.md，控制在100行以内，不修改其他文件。
```

## 第四步：重新打开项目

如果 Codex 已经打开这个项目，请关闭当前 Codex 会话并重新打开项目，使它重新发现 `AGENTS.md` 和 Skills。

官方支持在 CLI、IDE 扩展和 ChatGPT/Codex 桌面应用中使用 Skills。项目级 Skills 放在项目根目录的 `.agents/skills` 中。

## 第五步：第一次验证

在 Codex 中粘贴：

```text
请不要修改任何文件。告诉我：
1. 你读取到了哪些 AGENTS.md；
2. 你发现了哪些项目 Skills；
3. 用5行以内总结当前工作规则。
```

能看到五个 Skill 名称，说明安装成功。

## 日常怎么使用

打开 `prompts` 文件夹，根据任务复制对应模板：

* `01-修改小功能.txt`：增加小功能或修改页面
* `02-修复报错.txt`：解决报错、502、Docker、Nginx、Cloudflare 等问题
* `03-只分析不修改.txt`：担心 Codex 乱改时先分析
* `04-继续未完成项目.txt`：继续上一次工作
* `05-检查本次修改.txt`：提交前检查
* `06-让Codex填写项目资料.txt`：第一次安装后使用

把方括号中的内容替换成你的实际需求即可。

## Skill 如何手动调用

在支持 Skill 选择的界面中，可以使用 `/skills` 查看 Skills，或在提示词中输入 `$` 后选择 Skill。

也可以直接复制：

```text
请使用 $project-navigation、$minimal-code-change 和 $targeted-testing。
```

排查报错时复制：

```text
请使用 $diagnose-before-fixing。
```

如果界面没有自动补全 `$技能名称`，直接用自然语言写出 Skill 名称也可以；Codex 也会根据 Skill 的 description 自动判断是否调用。

## 最省额度的使用习惯

1. 一次只完成一个明确功能。
2. 指定允许读取和允许修改的目录。
3. 小修改不运行完整构建和全部测试。
4. 长对话使用 `/compact`，不同功能使用新会话。
5. 复杂任务先用 Plan 模式，确认方案后再修改。
6. 不要同时启动多个 agent 处理同一问题。
7. 不要安装大量重复 Skills；本工具包的五个已足够大多数小项目。
8. 每完成一个阶段，让 Codex 更新 `PROJECT_STATUS.md`。
9. 重要修改前先提交 Git，避免反复回滚。
10. 普通任务优先使用较轻量模型，疑难问题再切换更强模型。

## 哪些内容需要你自己修改

`AGENTS.md` 是通用规则，通常不用改。

`PROJECT_STATUS.md` 建议填写：

* 项目要做什么
* 使用什么框架
* 当前完成到哪里
* 下一步是什么
* 哪些文件不能改

如果项目有特殊测试命令，也应写进去。

## 卸载方法

删除项目根目录中的以下内容即可：

```text
.agents/
AGENTS.md
PROJECT_STATUS.md
prompts/
```

如果原项目本来就有同名文件，请不要直接删除，应恢复安装前的备份。
