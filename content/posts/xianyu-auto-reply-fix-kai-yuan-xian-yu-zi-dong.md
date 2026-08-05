+++
title = "xianyu-auto-reply-fix：开源闲鱼自动回复与自动发货管理系统部署教程"
date = "2026-07-29T16:09:00+08:00"
draft = false
categories = ["建站"]
tags = ["AI客服"]
featured = true
+++

`xianyu-auto-reply-fix` 是一个开源的闲鱼管理系统，基于 **FastAPI、SQLite 和 Playwright** 开发，提供多账号管理、关键词回复、[AI](/tags/ai/) 自动回复、自动发货、商品管理和运行日志等功能。

它更适合需要集中管理多个闲鱼账号、减少重复客服操作，或者希望研究浏览器自动化与 AI 客服系统的开发者。

> **注意：**该项目并非闲鱼官方产品，采用 AGPL-3.0 开源协议。请仅用于学习、研究和合规业务，不要用于刷量、骚扰、绕过平台限制或其他违规场景。

![xianyu-auto-reply-fix：开源闲鱼自动回复与自动发货管理系统部署教程](/uploads/2026/07/d6ddc941-6453-473b-8d51-501d0c08d4a3-873437be.jpg)

## 主要功能

### 多用户与多账号管理

系统支持用户注册、邮箱验证、图形验证码、权限控制和数据隔离。

每个用户可以添加多个闲鱼账号，并分别查看账号状态、启停监听任务及维护 Cookie，适合多人或多店铺协同管理。

### 关键词与 AI 自动回复

系统提供多种回复方式：

* 通用关键词回复
* 指定商品关键词回复
* 默认回复
* 图片关键词回复
* AI 上下文回复

回复优先级为：

```text
指定商品回复
> 商品专用关键词
> 通用关键词
> 默认回复
> AI 回复
```

对于价格、库存、发货时间等固定问题，可以优先使用关键词回复；只有未匹配到规则时，再交给 AI 处理，可以减少模型调用费用和错误回复。

### 自动发货

自动发货支持以下内容形式：

* 固定文本
* 卡密或批量数据
* API 返回内容
* 图片文件

系统提供防重复处理机制，适合虚拟资料、兑换码、课程链接等数字商品。

正式启用前，建议先使用测试商品验证触发条件，避免重复发货或错误匹配。

### 商品与订单管理

系统可以自动收集商品信息，并提供：

* 商品详情查看
* 商品规格配置
* 商品数据去重
* 订单状态管理
* 消息通知
* 在线客服
* 商品定时擦亮

这些功能可以把分散在多个账号中的商品、订单和咨询记录集中到一个 Web 后台中。

### 日志与运行监控

管理后台可以查看实时日志，并支持：

* `DEBUG`、`INFO`、`WARNING`、`ERROR` 日志级别
* 按日期生成日志文件
* 日志文件自动轮转
* 系统状态统计
* 安全统计
* `/health` 健康检查接口

遇到消息没有回复、Cookie 失效或容器启动失败时，可以先查看后台日志和账号连接状态。

## 部署前准备

Docker 部署建议准备：

* Docker 20.10 或更高版本
* Docker Compose 2.0 或更高版本
* 至少 2GB 内存
* 至少 10GB 可用存储空间

源码运行还需要：

* Python 3.11+
* [Node.js](/tags/node-js/) 16+
* Playwright Chromium
* Windows、Linux 或 macOS

对于不熟悉 Python 环境配置的用户，优先使用 Docker Compose。

## 使用 Docker Compose 部署

执行以下命令：

```bash
git clone https://github.com/GuDong2003/xianyu-auto-reply-fix.git
cd xianyu-auto-reply-fix
docker compose up -d
```

启动后访问：

| 功能       | 地址                             |
| -------- | ------------------------------ |
| Web 管理后台 | `http://localhost:9000`        |
| API 文档   | `http://localhost:9000/docs`   |
| 健康检查     | `http://localhost:9000/health` |

查看容器状态：

```bash
docker compose ps
```

查看实时日志：

```bash
docker compose logs -f
```

停止服务：

```bash
docker compose down
```

国内网络环境也可以使用仓库提供的配置：

```bash
docker compose -f docker-compose-cn.yml up -d --build
```

国内配置默认访问地址为：

```text
http://localhost:8000
```

## 本地源码运行

克隆项目并进入目录：

```bash
git clone https://github.com/GuDong2003/xianyu-auto-reply-fix.git
cd xianyu-auto-reply-fix
```

创建 Python 虚拟环境：

```bash
python -m venv venv
```

Linux 或 macOS 激活环境：

```bash
source venv/bin/activate
```

Windows 激活环境：

```powershell
venv\Scripts\activate
```

安装依赖：

```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

Linux 如果缺少浏览器系统依赖，可继续执行：

```bash
playwright install-deps chromium
```

启动服务：

```bash
python Start.py
```

本地运行默认访问：

```text
http://localhost:8090
```

## 首次登录后的安全设置

项目首次初始化且没有自定义管理员密码时，默认账号可能为：

```text
用户名：admin
密码：admin123
```

首次登录后应立即修改密码。

同时建议完成以下设置：

1. 不要直接把管理端口暴露到公网。
2. 公网访问时配置 HTTPS、反向代理和访问限制。
3. 为 `SECRET_ENCRYPTION_KEY` 设置随机且足够长的值。
4. 不要把 Cookie、API Key、[Token](/tags/token/) 或数据库上传到 GitHub。
5. 定期备份 `data/` 和必要的运行配置。

项目运行过程中可能产生以下目录：

```text
data/
logs/
browser_data/
update_backup/
```

其中可能包含数据库、日志、浏览器登录状态和 Cookie 相关信息，不应公开分享。

## 配置 AI 自动回复

AI 回复主要使用以下四个字段：

| 字段           | 作用       |
| ------------ | -------- |
| `model_name` | 模型名称     |
| `api_key`    | 模型服务密钥   |
| `base_url`   | API 接口地址 |
| `api_type`   | 接口类型     |

项目支持的接口类型包括：

* OpenAI-compatible
* OpenAI Responses
* DashScope
* [Gemini](/tags/gemini/)
* Anthropic
* Azure OpenAI

对于兼容 OpenAI Chat Completions 格式的第三方模型服务，通常只需要填写自定义 `base_url`、模型名称和 API Key。

建议先用测试账号验证：

* AI 是否能够正常返回内容
* 回复语气是否符合商品场景
* 是否会泄露系统提示词或敏感信息
* API 超时后是否会使用默认回复
* 模型调用费用是否在可接受范围内

## 基本使用流程

部署完成后，可以按照以下顺序配置：

1. 登录 Web 管理后台。
2. 修改默认管理员密码。
3. 添加闲鱼账号和 Cookie。
4. 配置关键词及默认回复。
5. 按需配置 AI 模型。
6. 添加自动发货规则。
7. 启动账号监听。
8. 通过日志观察消息连接和回复情况。

建议先启用关键词回复，再逐步增加 AI 回复和自动发货，不要在未测试的情况下直接管理正式账号。

## 常见问题

### Docker 容器启动失败

先查看日志：

```bash
docker compose logs -f
```

仍然无法启动时，可以重新构建：

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Playwright 提示缺少 Chromium

进入虚拟环境后执行：

```bash
playwright install chromium
```

### WebSocket 无法连接

重点检查：

* 闲鱼 Cookie 是否过期
* 服务器网络是否正常
* 防火墙是否拦截连接
* 账号是否触发登录验证
* 后台账号监听任务是否已经启用

### 端口被占用

Docker 部署可以修改 `docker-compose.yml` 中的端口映射。

源码运行可以修改 `API_PORT` 环境变量，或者调整 `global_config.yml` 中的端口配置。

## 技术架构

| 模块     | 使用技术                                    |
| ------ | --------------------------------------- |
| 后端     | FastAPI、Uvicorn、Python 异步编程             |
| 数据库    | SQLite 3                                |
| 前端     | Bootstrap 5、Vanilla JavaScript、Chart.js |
| 通信     | REST API、WebSocket、SSE                  |
| 浏览器自动化 | Playwright、DrissionPage                 |
| 日志     | Loguru                                  |
| 部署     | Docker、Docker Compose、可选 Nginx          |

SQLite 部署简单，适合个人或小规模使用；如果需要大量账号、高并发访问或多人长期协作，应先进行压力测试，并评估数据库和任务调度是否需要进一步改造。

## 使用注意事项

这个项目需要维护账号 Cookie 和浏览器状态，因此无法保证长期无人值守运行。

闲鱼登录策略、接口和页面结构发生变化后，自动回复或账号监听功能也可能失效。使用过程中应定期检查日志，并关注项目 Issues 和版本更新。

自动回复内容也应避免：

* 重复发送相同消息
* 向用户发送广告或无关内容
* 承诺不存在的库存或服务
* 自动处理高风险交易纠纷
* 绕过闲鱼平台规则

## 项目地址

* GitHub：[GuDong2003/xianyu-auto-reply-fix](https://github.com/GuDong2003/xianyu-auto-reply-fix)
* 部署文档：[deployment.md](https://github.com/GuDong2003/xianyu-auto-reply-fix/blob/main/docs/deployment.md)
* 配置说明：[configuration.md](https://github.com/GuDong2003/xianyu-auto-reply-fix/blob/main/docs/configuration.md)
* 使用指南：[usage.md](https://github.com/GuDong2003/xianyu-auto-reply-fix/blob/main/docs/usage.md)
* 常见问题：[faq.md](https://github.com/GuDong2003/xianyu-auto-reply-fix/blob/main/docs/faq.md)

> 项目功能、默认端口和配置方式可能随版本更新而变化，部署前请以 GitHub 仓库中的最新文档为准。
