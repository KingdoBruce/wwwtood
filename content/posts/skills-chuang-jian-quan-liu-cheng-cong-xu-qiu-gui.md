+++
title = "Skills 创建全流程：从需求规划到测试落地，零基础也能完成"
date = "2026-07-28T11:08:00+08:00"
draft = false
featured = true
categories = ["AI & Automation"]
tags = ["Skill Creator", "Agent Skills", "AI工作流", "AI自动化", "自定义Skill", "提示词工程"]
+++

很多人第一次接触 [Skills](/tags/skills/) 时，会认为它只是一个写了提示词的 Markdown 文件。

实际上，一个真正稳定、可复用的 Skill，更像是一份专门交给 [AI](/tags/ai/) 执行的标准作业流程。它不仅要告诉 AI“做什么”，还要说明什么时候启用、按照什么步骤执行、需要读取哪些资料，以及最终应该输出什么结果。

本文将完整梳理 Skills 创建流程，从前期规划、目录初始化、`SKILL.md` 编写，到验证与实际测试。即使没有开发经验，也可以按照步骤逐步完成。


![Image_2026728_11_11_46](/uploads/2026/07/Image_2026728_11_11_46-9bbd7f8a.jpg)


## 一、什么是 Skill？

Skill 是一个独立的文件夹，其中包含 AI 完成特定任务所需要的说明、脚本、参考资料和模板资源。

它可以把通用 AI 转变成更适合某项工作的专业助手，例如：

* 按固定格式撰写产品介绍
* 根据公司规范回复客户邮件
* 自动分析 Excel 或 CSV 数据
* 按统一标准生成网站文章
* 批量处理图片或 PDF 文件
* 调用特定 API 完成固定工作流
* 根据团队规范检查代码

一个 Skill 通常围绕一个明确任务设计，而不是试图解决所有问题。

---

# 第一阶段：前期规划

在创建文件之前，先把 Skill 的目标和使用方式规划清楚。

这一步看似没有写代码，却会直接决定 Skill 是否容易触发、执行是否稳定，以及后续是否方便维护。

## 1. 明确 Skill 的目标

建议从以下四个方面定义目标。

### 1.1 功能描述

首先说明这个 Skill 具体解决什么问题。

不要只写：

> 帮助用户处理内容。

这种描述过于宽泛，AI 很难判断应该在什么情况下调用它。

更清晰的写法是：

> 根据用户提供的原始资料，生成适合个人博客发布的中文 Markdown 文章，并补充标题、文章结构、[SEO](/tags/seo/) 关键词、标签和项目地址。

功能描述越具体，后续越容易设计执行流程。

### 1.2 适用场景

明确用户在什么情况下需要使用这个 Skill。

例如：

* 用户要求润色个人博客文章
* 用户提供视频文案，希望整理成教程
* 用户希望生成可直接复制的 Markdown 内容
* 用户希望补充 GitHub 项目地址
* 用户要求文章适合 [Google](/tags/google/) SEO 和 AI 搜索引用

适用场景也是 Skill 判断是否应该触发的重要依据。

### 1.3 预期输出

提前规定 Skill 完成任务后应该交付什么。

例如：

```text
1. 原文问题分析
2. 建议补充的信息
3. 优化后的文章标题
4. 可直接复制的 Markdown 正文
5. SEO 描述
6. Tags 标签
7. 项目地址
```

输出格式越明确，多次执行时的结果越稳定。

### 1.4 限制条件

同时还要说明 Skill 不应该做什么。

例如：

* 不虚构测试数据
* 不编造 GitHub Stars 数量
* 无法确认的信息需要明确标注
* 不堆砌 SEO 关键词
* 不在文章中保留明显错别字
* 不泄露 API Key、密码或个人隐私
* 未经确认不得执行删除、付款或生产环境修改

限制条件可以减少 AI 自由发挥过度造成的问题。

---

## 2. 分析实际需求

目标明确后，需要从用户、技术、性能和兼容性四个维度继续分析。

### 2.1 用户需求

先判断谁会使用这个 Skill，以及他们会如何提出请求。

建议至少准备 3～5 个真实示例。

例如，创建一个博客文章优化 Skill 时，用户可能会这样说：

```text
帮我把这段视频文案整理成博客文章。
```

```text
重新润色这篇文章，并补充 GitHub 项目地址。
```

```text
生成可以直接复制到 Hugo 网站中的 Markdown 内容。
```

```text
让文章更适合 Google SEO 和 AI 搜索引用。
```

这些真实表达可以帮助你完善 Skill 的触发描述。

### 2.2 技术需求

检查 Skill 是否需要额外工具或文件。

常见资源包括：

* Python 或 Bash 脚本
* API 接口
* [MCP](/tags/mcp/) 服务
* 浏览器搜索能力
* GitHub 项目资料
* 公司内部文档
* Markdown 模板
* 图片、Logo 或字体
* Excel、PDF、Word 处理工具

并不是每个 Skill 都需要脚本。

能够通过清晰文字说明完成的任务，优先写在 `SKILL.md` 中；只有重复、容易出错或需要固定结果的操作，才更适合使用脚本。

### 2.3 性能需求

提前考虑执行成本和效率，例如：

* 是否需要联网搜索
* 是否会读取大型文件
* 是否需要处理大量图片
* 是否会调用付费 API
* 是否需要批量执行
* 是否存在较长的运行时间
* 是否需要限制 [Token](/tags/token/) 消耗

Skill 内容也不宜无限扩张。应只保留 AI 真正需要的规则，把较长的资料放入 `references/`，需要时再读取。

### 2.4 兼容性需求

确认 Skill 将在哪些平台或环境中运行，例如：

* Codex
* [Claude](/tags/claude/) Code
* GitHub Copilot
* [Cursor](/tags/cursor/)
* [Gemini](/tags/gemini/) CLI
* Windows
* macOS
* Linux
* Docker
* 团队内部 Agent 平台

不同平台对 Skill 的安装路径、元数据和调用方式可能不同，因此不要默认一个 Skill 在所有环境中都能完全通用。

---

# 第二阶段：正式创建 Skill

规划完成后，就可以开始建立目录和编写内容。

## 3. Skill 命名规范

建议使用：

* 小写英文字母
* 数字
* 连字符 `-`

不要使用：

* 空格
* 中文文件夹名
* 下划线
* 大写字母
* 含义不清的缩写

正确示例：

```text
blog-content-optimizer
```

```text
fabric-email-writer
```

```text
github-project-researcher
```

不推荐：

```text
My Skill
```

```text
blog_skill
```

```text
新建技能
```

文件夹名称应该与 `SKILL.md` 中的 `name` 保持一致。

---

## 4. 使用 Skill Creator 初始化

如果当前环境中已经安装官方 `skill-creator`，建议优先使用初始化脚本，而不是手动建立所有文件。

标准命令格式：

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

例如，将 Skill 创建到 Codex 默认 Skills 目录：

```bash
scripts/init_skill.py my-skill \
  --path "${CODEX_HOME:-$HOME/.codex}/skills"
```

同时创建 `scripts/` 和 `references/`：

```bash
scripts/init_skill.py my-skill \
  --path "${CODEX_HOME:-$HOME/.codex}/skills" \
  --resources scripts,references
```

同时创建脚本、参考资料和静态资源目录：

```bash
scripts/init_skill.py my-skill \
  --path "${CODEX_HOME:-$HOME/.codex}/skills" \
  --resources scripts,references,assets
```

初始化脚本可以自动生成基础模板，减少目录名称、YAML 格式和必要文件写错的概率。

> 不同版本的 Skill Creator 所在路径可能不同。实际使用时，应以本机安装目录中的 `skill-creator` 文件为准。

---

## 5. 手动创建 Skill 目录

没有初始化脚本时，也可以手动创建。

### Windows PowerShell

```powershell
mkdir my-skill
cd my-skill

New-Item SKILL.md -ItemType File
mkdir scripts
mkdir references
mkdir assets

tree /F
```

### macOS 或 Linux

```bash
mkdir my-skill
cd my-skill

touch SKILL.md
mkdir scripts references assets

tree -a
```

如果系统没有安装 `tree`，可以使用：

```bash
find . -maxdepth 3 -print
```

或者：

```bash
ls -la
```

需要注意，`scripts/`、`references/` 和 `assets/` 都是可选目录。没有实际用途时，不需要为了结构完整而创建空文件夹。

---

## 6. 标准目录结构

一个较完整的 Codex Skill 可以采用以下结构：

```text
my-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
├── references/
└── assets/
```

各目录作用如下。

### `SKILL.md`

这是整个 Skill 的核心文件，必须存在。

它负责说明：

* Skill 名称
* Skill 的用途
* 什么时候应该触发
* 应该按照什么流程执行
* 应该读取哪些资源
* 最终输出什么结果
* 有哪些限制条件

文件名必须写成：

```text
SKILL.md
```

不建议写成：

```text
skill.md
```

部分系统区分大小写，错误命名可能导致 Skill 无法被识别。

### `agents/openai.yaml`

这是 Codex Skill 推荐使用的界面元数据文件，可用于展示：

* Skill 显示名称
* 简短说明
* 默认提示语
* 图标或界面相关信息

它主要服务于 Skill 列表和交互界面，不应代替 `SKILL.md` 中的核心执行规则。

### `scripts/`

用于保存可以重复执行的代码，例如：

```text
scripts/
├── clean_markdown.py
├── validate_output.py
└── export_result.py
```

适合放入脚本的任务通常具备以下特点：

* 操作步骤固定
* 需要重复执行
* 手动生成容易出错
* 结果必须保持一致
* 需要调用本地程序或处理文件

新增脚本后，应实际运行测试，不能只确认代码看起来正确。

### `references/`

用于保存参考资料，例如：

```text
references/
├── writing-rules.md
├── seo-checklist.md
├── api-documentation.md
└── company-style-guide.md
```

较长的背景资料不建议全部塞进 `SKILL.md`。

可以在 `SKILL.md` 中说明什么时候读取某份参考资料，让 AI 按需加载，从而减少上下文占用。

### `assets/`

用于保存最终任务可能使用的静态资源，例如：

```text
assets/
├── logo.png
├── article-template.md
├── report-template.docx
└── website-template/
```

它适合存放：

* 图片
* 图标
* Logo
* 文档模板
* 网页模板
* 示例文件
* 需要复制到输出结果中的资源

### `LICENSE` 或 `LICENSE.txt`

如果 Skill 准备公开发布或共享给团队，应明确授权方式。

常见许可证包括：

* MIT License
* Apache License 2.0
* GNU GPL
* 项目自定义许可证

对于仅在个人电脑内部使用的 Skill，许可证通常不是运行所必需的；但公开到 GitHub 前，建议补充清晰的授权文件。

---

# 第三阶段：编写 SKILL.md

## 7. YAML Frontmatter

`SKILL.md` 顶部需要包含 YAML 元数据。

基础格式：

```markdown
---
name: my-skill
description: Explain what this skill does and exactly when it should be used.
---
```

其中最重要的是 `description`。

它不仅是介绍文字，也是 AI 判断是否调用这个 Skill 的主要依据。

不推荐：

```yaml
description: 一个非常好用的内容处理工具。
```

推荐：

```yaml
description: Optimize Chinese personal-blog articles into structured Markdown content. Use when users ask to rewrite video transcripts, improve Google SEO readability, add verifiable GitHub project information, generate tags, or prepare copy-ready Markdown for a website.
```

一段有效的描述需要同时回答两个问题：

1. 这个 Skill 能做什么？
2. 用户提出什么请求时应该使用它？

---

## 8. 编写执行流程

`SKILL.md` 正文应该以明确、可执行的规则为主。

下面是一个简单示例：

```markdown
---
name: blog-content-optimizer
description: Optimize Chinese blog content into clear, credible and copy-ready Markdown. Use when the user provides rough notes, transcripts or existing articles and asks for rewriting, SEO improvement, GitHub project verification, tags or website publishing content.
---

# Blog Content Optimizer

## Workflow

1. Read the complete source material.
2. Correct spelling, command and terminology errors silently.
3. Identify vague, repetitive or overly promotional statements.
4. Determine what factual information is missing.
5. Verify time-sensitive claims and GitHub project information.
6. Rewrite the article in clear Chinese Markdown.
7. Preserve relevant SEO keywords naturally.
8. Add the verified project address at the end.
9. Generate comma-separated tags.

## Output

Return the following sections:

1. 原文存在的问题
2. 建议补充的信息
3. 中文优化版
4. Tags
5. 项目地址

## Rules

- Do not fabricate facts, statistics, Stars or test results.
- Do not stuff keywords.
- Do not mention spelling corrections in the final article.
- Mark information that cannot be verified.
- Keep headings descriptive and easy to quote.
- Prefer concrete steps and examples over marketing language.
```

这类写法比长篇介绍更有效，因为每一条都可以直接指导 AI 执行。

---

# 第四阶段：验证与测试

## 9. 运行基础校验

完成 Skill 后，可以使用 Skill Creator 提供的验证脚本检查格式。

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

例如：

```bash
scripts/quick_validate.py ~/.codex/skills/my-skill
```

验证工具通常可以发现：

* `SKILL.md` 缺失
* YAML 格式错误
* 缺少 `name`
* 缺少 `description`
* 文件夹命名不符合规范
* Skill 名称与目录不一致

出现错误后，根据提示修改，再重新运行验证命令。

---

## 10. 使用真实任务测试

通过格式验证，并不代表 Skill 已经真正可用。

至少准备 3～5 个测试请求，例如：

```text
把下面的视频文案整理成可以发布的 Markdown 教程。
```

```text
检查这篇文章中的 GitHub 项目是否真实，并补充项目地址。
```

```text
让文章更适合 Google SEO，但不要堆砌关键词。
```

```text
只修改错别字，不改变原文语气。
```

测试时重点观察：

* Skill 是否在正确场景触发
* 不相关请求是否错误触发
* 输出结构是否稳定
* 是否遗漏关键步骤
* 是否读取了正确的参考资料
* 是否出现虚构内容
* 脚本是否能够正常运行
* 多次执行的结果是否基本一致

---

## 11. 根据测试结果持续优化

Skill 通常不会一次完成。

更合理的优化循环是：

```text
实际使用
↓
发现遗漏或错误
↓
定位问题来源
↓
修改 SKILL.md、脚本或参考资料
↓
重新验证
↓
再次使用真实任务测试
```

例如：

* 经常没有补充项目地址
  → 在工作流程和输出格式中同时增加 GitHub 检查要求。

* 经常错误触发
  → 缩小 `description` 中的使用范围。

* 经常无法识别用户表达
  → 在 `description` 中增加常见触发场景。

* 输出格式不稳定
  → 提供固定模板或示例。

* 重复任务消耗较多 Token
  → 把固定操作改成脚本。

Skill 的价值并不在于文件数量，而在于它能否让同类任务以更稳定、更可预测的方式重复完成。

---

# 哪些情况适合使用 Skill Creator？

## 1. 创建新的 Skill

当你只有一个需求想法，还没有确定目录、执行步骤和输出结构时，可以让 Skill Creator 帮助完成：

* 需求梳理
* 使用场景分析
* 目录初始化
* `SKILL.md` 草稿
* 资源规划
* 验证与测试

## 2. 优化已有 Skill

如果已有 Skill 经常漏步骤、错误触发或输出不稳定，可以使用 Skill Creator：

* 优化 `description`
* 精简冗余内容
* 补充测试案例
* 重新规划脚本和参考资料
* 比较修改前后的执行结果

## 3. 团队协作

多人共同维护 Skills 时，Skill Creator 可以帮助团队统一：

* 目录结构
* 文件命名
* 输出格式
* 开发流程
* 测试标准
* 版本维护方式

## 4. 固定且重复的工作流

例如只需要几个固定命令或固定步骤的任务，也适合封装成 Skill：

* 项目初始化
* 文件格式转换
* 批量重命名
* 发布前检查
* 固定格式报告生成

不过，任务越简单，Skill 内容越应该保持精简，不需要为了显得完整而增加大量无用说明。

## 5. 高度定制的业务任务

当任务依赖公司内部规范、专业资料、固定模板或特殊流程时，Skill 可以将这些知识组织成可复用资源。

例如：

* 面料报价邮件规范
* 公司品牌文案规则
* 内部数据库查询方式
* 特定 API 调用流程
* 固定交付文件格式

---

# 创建 Skill 时的常见错误

## 错误一：目标范围过大

例如：

```text
帮助用户完成所有办公任务。
```

这种 Skill 几乎无法稳定触发，也很难测试。

应该拆分成：

```text
customer-email-writer
invoice-data-checker
weekly-report-generator
```

## 错误二：只写功能，不写触发场景

如果 `description` 没有说明什么时候使用，AI 可能无法正确调用。

## 错误三：把所有资料都写进 SKILL.md

过长的文件会占用更多上下文。

应该将详细资料拆分到 `references/`，需要时再读取。

## 错误四：创建大量无用目录

没有脚本就不需要建立空的 `scripts/`；没有静态资源也不需要建立 `assets/`。

## 错误五：脚本没有实际运行

AI 生成的脚本即使语法看起来正确，也可能存在依赖、路径或参数问题，必须实际执行测试。

## 错误六：只验证格式，不测试效果

格式正确只能证明 Skill 可以被读取，不能证明它能完成真实任务。

## 错误七：在文件中写入敏感信息

不要把以下内容直接写入 Skill：

* API Key
* 登录密码
* Cookie
* 私钥
* 客户隐私数据
* 生产环境凭据

敏感信息应通过安全的环境变量或密钥管理工具提供。

---

# 总结

一个标准的 Skills 创建流程，可以归纳为六个步骤：

```text
明确目标
↓
收集真实使用案例
↓
规划 scripts、references 和 assets
↓
初始化并编写 SKILL.md
↓
运行格式验证和真实任务测试
↓
根据实际结果持续迭代
```

对于零基础用户来说，最重要的不是一次写出复杂的 Skill，而是先选择一个明确、重复出现的小任务。

只要目标清晰、触发场景明确、输出格式固定，并通过真实任务不断测试优化，就可以逐步建立一套属于自己的 AI 工作流程。

---

## 相关项目

* [OpenAI Skills](https://github.com/openai/skills)
* [OpenAI Codex Skill Creator 示例](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md)
* [Anthropic Skills](https://github.com/anthropics/skills)
* [Anthropic Skill Creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)

> 注意：OpenAI 原 `openai/skills` 仓库目前已提示弃用，并引导开发者使用新的 OpenAI Plugins 体系。旧仓库仍可用于学习 Skill 的目录结构和设计思路，但正式使用前应查看最新官方文档。
