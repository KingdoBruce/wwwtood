+++
title = "DigitalPlat 免费域名申请教程：GitHub 登录、Cloudflare 解析与避坑指南"
date = "2026-07-31T11:11:00+08:00"
draft = false
categories = ["建站"]
tags = ["DigitalPlat FreeDomain", "us.kg"]
featured = true
+++

DigitalPlat FreeDomain 提供 `dpdns.org`、`us.kg`、`qzz.io`、`xx.kg`、`qd.je` 等公共命名空间下的免费域名。

申请成功后，用户可以设置自定义 Nameserver，将 DNS 托管到 [Cloudflare](/tags/cloudflare/) 等第三方服务，再配置 A、AAAA、CNAME、MX、TXT 等记录。

它适合个人主页、[开源项目](/tags/开源项目/)、静态网站和部署练习，但不建议作为重要商业网站唯一的域名入口。

> 官方提供的后缀、申请数量、审核方式和免费政策可能随时调整，请以申请面板显示的信息为准。


![DigitalPlat 免费域名申请教程：GitHub 登录、Cloudflare 解析与避坑指南](/uploads/2026/07/14_36-dadff2e7.jpg)


## DigitalPlat FreeDomain 是什么？

DigitalPlat FreeDomain 是一个免费域名项目。它提供的地址通常采用以下形式：

```text
yourname.dpdns.org
yourname.us.kg
yourname.qzz.io
yourname.xx.kg
yourname.qd.je
```

从域名层级来看，它们属于 DigitalPlat 管理的公共命名空间，并不是用户直接向注册局购买的 `.com`、`.net` 或国家顶级域名。

不过，与普通网站平台赠送的固定子域名不同，DigitalPlat 支持用户设置外部权威 Nameserver。因此，你可以将域名添加到 [Cloudflare](/tags/cloudflare/)，并自行管理 DNS 记录、HTTPS、CDN 和网站部署。

DigitalPlat 本身主要负责域名申请和 Nameserver 委托，并不提供普通的 DNS 记录编辑器。A、CNAME、TXT 等记录需要在 Cloudflare或其他外部 DNS 服务商中设置。

## 当前支持哪些免费域名后缀？

根据 DigitalPlat 官方 GitHub 项目，目前列出的后缀包括：

* `.dpdns.org`
* `.us.kg`
* `.qzz.io`
* `.xx.kg`
* `.qd.je`

部分后缀可能暂时停止申请，也可能因为名额、风控或上游政策变化而调整。

因此，教程文章中不应保证某个后缀长期开放。实际申请时，应以 DigitalPlat 控制面板中的可选后缀为准。

## 适合哪些使用场景？

DigitalPlat 免费域名比较适合以下用途：

* 个人主页和作品集
* GitHub Pages、Cloudflare Pages 等静态网站
* 开源项目演示页面
* API、Webhook 或临时测试环境
* Docker、VPS 和网站部署练习
* DNS、HTTPS、CDN 配置学习
* 暂时不想购买正式域名的个人项目

它最大的价值是降低试错成本，让初学者能够免费体验完整的域名解析和网站部署流程。

以下项目不建议只使用免费域名：

* 企业官网
* 电商网站和支付页面
* 长期运营的内容品牌
* 依赖搜索流量的正式网站
* 邮件、登录和用户账户系统
* 不能中断访问的重要服务

重要项目至少应准备一个自己购买并可自由转移的正式域名。

## DigitalPlat 免费域名申请步骤

### 第一步：注册或登录账号

打开 DigitalPlat FreeDomain 控制面板：

```text
https://dash.domain.digitalplat.org/
```

根据页面提示创建账号或登录。

DigitalPlat 的登录和验证方式可能调整。部分时期可能使用 GitHub 账号辅助验证，但不应将“必须通过 GitHub 登录”写成永久固定规则。

建议使用长期可访问的邮箱和账号，并开启可用的安全验证方式。

### 第二步：搜索可用域名

进入域名申请页面后，输入准备使用的名称，例如：

```text
myproject
bruceblog
demoapi
```

然后从当前开放的后缀中选择：

```text
myproject.dpdns.org
myproject.us.kg
myproject.qzz.io
```

提交前应注意：

1. 不要申请知名品牌、银行、政府机构或其他组织的名称。
2. 不要使用容易被误认为官方网站或登录页面的名称。
3. 尽量选择与项目名称、用户名或网站内容相关的域名。
4. 避免一次申请大量无实际用途的域名。

部分名称可能进入人工审核，也可能因为风控、保留词或商标风险被拒绝。

### 第三步：在 Cloudflare 添加域名

登录 Cloudflare，选择“添加域”或“Add a domain”，然后输入刚刚申请的完整域名，例如：

```text
myproject.dpdns.org
```

Cloudflare 会分配两条 Nameserver，例如：

```text
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

实际 Nameserver 每个账号和域名都不同，必须复制 Cloudflare 页面中显示的地址。

### 第四步：回到 DigitalPlat 设置 Nameserver

返回 DigitalPlat 控制面板，打开对应域名的管理页面，将 Cloudflare 提供的两条 Nameserver 填入 NS 设置。

保存后等待委托信息生效。

DNS 和 Nameserver 变更不会总是立即完成，实际时间会受到缓存、TTL 和上游 DNS 更新速度影响。不要因为几分钟内未生效就重复删除和添加域名。

### 第五步：在 Cloudflare 配置 DNS

Cloudflare 确认域名状态正常后，即可添加 DNS 记录。

将域名指向服务器 IPv4 地址：

```text
类型：A
名称：@
内容：服务器 IPv4 地址
```

将 `www` 指向主域名：

```text
类型：CNAME
名称：www
目标：myproject.dpdns.org
```

连接 Cloudflare Pages 时，建议优先在 Pages 项目的“自定义域”设置中添加域名，再按照 Cloudflare 提示完成验证。

用于第三方服务验证时，通常需要添加 TXT 记录：

```text
类型：TXT
名称：第三方平台指定的名称
内容：第三方平台提供的验证码
```

## 常见问题与避坑提醒

### 1. 它不是自己购买的顶级域名

`myproject.dpdns.org` 可以独立配置 Nameserver 和 DNS，但它仍然位于 DigitalPlat 管理的公共命名空间下。

用户无法像普通 `.com` 域名一样，将整个后缀的所有权转移到其他注册商。

因此，更准确的描述是：

> 可独立委托 DNS 的免费公共域名，而不是用户自行注册并持有的顶级域名。

### 2. 免费不代表永久不变

域名后缀、账号限制、续期规则、审核方式和免费政策都可能调整。

使用前应确认：

* 是否需要续期
* 域名当前状态是否正常
* Nameserver 是否仍然有效
* 注册邮箱能否正常接收通知
* 控制面板是否有待处理的审核或安全提醒

不要把“[免费域名](/tags/免费域名/)”写成“永久免费且永不回收”。

### 3. Cloudflare 接入不等于域名归 Cloudflare 所有

Cloudflare 只负责权威 DNS、CDN、HTTPS 和安全服务。

域名的申请状态、命名空间和使用资格仍由 DigitalPlat 管理。即使 Cloudflare 显示域名已激活，DigitalPlat 仍可能依据使用政策暂停违规域名。

### 4. 不要用于钓鱼、仿冒和垃圾邮件

DigitalPlat 明确禁止以下用途：

* 仿冒登录页面和凭据收集
* 钓鱼、诈骗和恶意跳转
* 病毒、木马和恶意软件下载
* 垃圾邮件和批量骚扰
* 冒充政府、银行、学校或知名品牌
* 盗版、商标滥用和其他违法内容
* 扫描、攻击或绕过安全限制

存在安全风险或违规行为时，DigitalPlat 可以暂停域名、关闭 DNS 或终止账号，并且在紧急情况下不一定提前通知。

### 5. 不适合直接承担关键业务

DigitalPlat 官方条款要求用户自行准备数据备份、替代域名、故障切换和业务连续性方案。

重要项目建议采用以下结构：

```text
正式付费域名：主站和长期品牌入口
DigitalPlat 免费域名：测试、镜像或临时演示
GitHub：保存源代码
Cloudflare：管理 DNS、HTTPS 和 CDN
独立备份：保存数据库与网站文件
```

这样即使免费域名政策发生变化，也不会导致网站和用户入口完全丢失。

### 6. 不建议用作主要企业邮箱域名

免费公共域名可能受到整体后缀信誉、邮件服务商策略和反垃圾系统的影响。

个人测试可以配置 MX、SPF、DKIM 和 DMARC，但正式业务邮件仍建议使用自己购买的品牌域名。

## DigitalPlat 免费域名值得申请吗？

对于学习网站部署、搭建个人主页和测试开源项目，DigitalPlat FreeDomain 是一个实用的低成本入口。

它的优势包括：

* 无需先购买传统域名
* 可以设置外部 Nameserver
* 可以接入 Cloudflare
* 支持常见 DNS 记录
* 适合 GitHub Pages、Cloudflare Pages 和 VPS
* 官方项目和使用文档公开在 GitHub

它的限制也很明确：

* 域名位于公共命名空间下
* 政策和后缀可能调整
* 域名可能需要续期或重新审核
* 违规或高风险使用可能被立即暂停
* 不适合成为关键业务的唯一入口

免费降低的是建站成本，并不会消除安全、合规、备份和迁移责任。 

[免费领取 4 个开发者域名：Stackryze Domains 使用介绍](/posts/mian-fei-ling-qu-4-ge-kai-fa-zhe-yu/)
