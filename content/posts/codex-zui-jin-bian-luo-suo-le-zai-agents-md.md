+++
title = "Codex 最近变“啰嗦”了？在 AGENTS.md 加上这句提示词试试"
date = "2026-07-27T22:04:00+08:00"
draft = false
featured = true
categories = ["AI & Automation"]
tags = ["Codex", "AI编程助手", "OpenAI Codex", "AI编程效率", "提示词优化"]
+++

最近使用 [Codex](/tags/codex/) 时，你可能会遇到这样的情况：

以前只需要一句话，Codex 就能直接修改代码、运行测试并完成任务；现在却经常输出大量过程说明，需要反复确认和引导，真正的代码修改反而变慢了。

遇到这种情况，可以尝试在 Codex 的 `AGENTS.md` 文件中加入下面这句指令：

```text
DO NOT send optional commentary.
```

它的意思很简单：

> 不要发送非必要的过程说明。

## 这句提示词能解决什么问题？

Codex 在执行任务时，可能会主动输出以下内容：

* 接下来准备检查哪些文件
* 为什么选择某种实现方式
* 还可以继续做哪些可选优化
* 是否需要运行额外测试
* 大量并非必须的解释和总结

这些内容并不一定有错，但在需求已经非常明确时，过多的过程播报会让交互显得拖沓，也会占用额外的输出 [Token](/tags/token/)。

加入这条指令后，Codex 通常会更倾向于：

* 直接读取代码并开始修改
* 减少不必要的进度说明
* 只保留与结果有关的信息
* 缩短最终回复
* 降低无效输出带来的 Token 消耗

简单理解就是：

> 需求明确时，直接做事，不要边做边反复解释。


![026727_22_11_38](/uploads/2026/07/026727_22_11_38-341c13f8.jpg)


## 正确添加到哪个文件？

正确的文件名是：

```text
AGENTS.md
```

Codex 官方支持通过 `AGENTS.md` 为项目添加长期指令。每次开始任务前，Codex 会读取适用范围内的规则，并将其作为项目上下文的一部分。

### 方法一：只对当前项目生效

在项目根目录创建：

```text
你的项目/
├── AGENTS.md
├── package.json
├── src/
└── README.md
```

然后在 `AGENTS.md` 中写入：

```md
# Codex Instructions

DO NOT send optional commentary.
```

这种方式只会影响当前项目，适合先测试实际效果。

### 方法二：让所有项目默认生效

在 Codex 的全局目录中创建：

```text
~/.codex/AGENTS.md
```

Windows 通常对应：

```text
C:\Users\你的用户名\.codex\AGENTS.md
```

写入：

```md
# Global Codex Instructions

DO NOT send optional commentary.
```

全局文件适合保存个人长期偏好，例如回复风格、代码习惯和默认工作方式。项目目录中的 `AGENTS.md` 则更适合保存当前仓库的技术规范。Codex 会按照目录层级加载这些指令，距离当前工作目录更近的规则优先级更高。

## 更实用的完整写法

只写一句话虽然简单，但容易被理解成“完全不要解释”。为了避免 Codex 省略必要的错误信息，可以改成下面这种更明确的版本：

```md
# Response Style

DO NOT send optional commentary.

Start working directly when the task is clear.
Do not provide routine progress updates.
Do not explain self-evident code.
Do not add unnecessary comments to generated code.
Report only blockers, important decisions, test results, and the final outcome.
```

对应的中文含义是：

* 任务明确时直接开始执行
* 不要发送常规进度播报
* 不要解释一眼就能看懂的代码
* 不要生成没有实际价值的代码注释
* 只报告阻塞问题、重要决策、测试结果和最终结果

这种写法比单独一句 `DO NOT send optional commentary.` 更稳定，因为它明确规定了哪些内容可以省略，哪些关键信息仍然必须保留。

## 它为什么可能让 Codex 感觉更快？

这条指令并不会直接提升模型的推理能力，也不会真正修改 Codex 模型。

它主要减少的是可见输出中的冗余内容。

对于需要多次读取文件、调用工具和修改代码的任务，Codex 可能会在工具调用之间发送进度说明。减少这些非必要文本后，交互过程会更紧凑，用户感受到的等待时间和 Token 消耗也可能有所下降。

OpenAI 的 Codex 提示指南同样建议：代码本身足够清楚时，不要添加重复解释功能的注释；只有复杂逻辑确实需要说明时，才使用简短注释。

## 这条指令不能解决哪些问题？

需要注意，`DO NOT send optional commentary.` 并不是官方发布的“Codex 降质修复代码”。

它无法直接解决以下问题：

* 项目上下文过长或包含过时信息
* `AGENTS.md` 中存在互相冲突的规则
* 当前模型或推理强度选择不合适
* 任务描述过于模糊
* 依赖、测试环境或项目本身存在问题
* Codex 没有获得读取或执行命令所需的权限

目前可以确认的是，这句话已经出现在 Codex 用户反馈和部分开源项目的 `AGENTS.md` 中，但相关效果主要来自用户实践，并不代表 OpenAI 官方承诺它能够恢复模型质量。

## 使用建议

建议先把它添加到某一个项目根目录的 `AGENTS.md` 中，而不是直接加入全局配置。

测试几次真实任务后，重点观察：

1. Codex 是否减少了无意义的过程说明；
2. 是否仍然能够报告报错和测试结果；
3. 是否出现回复过于简略、遗漏重要信息的情况；
4. 实际代码质量有没有改善。

如果发现 Codex 连关键问题也不再说明，可以将规则改成：

```text
Avoid optional commentary, but always report blockers, failed checks, security risks, and important implementation decisions.
```

这样既能减少“唠嗑”，又不会隐藏真正需要关注的信息。

## 总结

`DO NOT send optional commentary.` 的核心作用，不是让 Codex 突然变得更聪明，而是限制它输出不必要的过程说明。

对于需求明确、希望 Codex 直接修改代码的用户，这条规则可能带来三个实际变化：

* 回复更短
* 过程更直接
* 可见输出消耗的 Token 更少

如果 Codex 最近只是变得啰嗦、频繁汇报进度，这条指令值得尝试；如果问题是代码错误增多、理解需求失败或任务无法完成，则还需要继续检查模型设置、项目上下文、权限以及 `AGENTS.md` 中是否存在冲突规则。

## 项目地址与参考资料

* [OpenAI Codex GitHub 项目](https://github.com/openai/codex)
* [Codex 官方 AGENTS.md 使用说明](https://developers.openai.com/codex/agent-configuration/agents-md)
* [Codex 官方提示词指南](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
