+++
title = "不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程"
date = "2026-08-14T19:49:00+08:00"
draft = false
featured = true
categories = ["建站"]
tags = ["Google Workspace", "Workspace", "域名", "google", "域名注册", ".com域名"]
description = "通过 Google Workspace 的特定地区定价，可以用较低成本注册 .com 域名，再通过 Squarespace 完成域名验证与管理，最后将 Nameserver 切换到 Cloudflare，实现 DNS 托管、CDN 加速和 DNSSEC 安全配置。本文整理了从域名购买、邮箱验证、Cloudflare 接管，到正确取消 Workspace 订阅及常见问题补救的完整流程，适合个人站长、独立开发者和低成本建站用户参考。"
+++

最近折腾域名时发现了一条比较特别的购买路径：通过 **[Google](/tags/google/) Workspace** 注册 `.com` 域名，在特定地区的定价下，域名年费可能低至几十土耳其里拉，折合人民币大约 **10～15 元/年**。

相比常见注册商每年七八十元甚至上百元的价格，这个成本确实很有吸引力。

不过，这套方法比直接在域名平台注册稍微复杂一些，因为整个流程会涉及三个平台：

* **Google Workspace**：创建账号、购买域名
* **Squarespace**：管理域名、修改 Nameserver、设置 DNSSEC
* **[Cloudflare](/tags/cloudflare/)**：负责最终 DNS 托管和网站解析

本文整理一遍完整操作流程，并把实际操作中比较容易踩坑的地方一起写出来。


![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/26814_19_55_48-b4ac09c4.jpg)


> **注意：** Google、Squarespace 的地区价格、付款规则、试用政策以及域名价格都可能调整，请以实际结算页面为准。注册资料和付款信息建议按照平台要求真实填写，避免后续账号或域名验证出现问题。

---

## 一、这种方式到底能便宜多少？

先简单看看常见 `.com` 域名注册价格。

| 注册平台                        |          首年参考价格 |      续费参考价格 | 特点                        |
| --------------------------- | --------------: | ----------: | ------------------------- |
| GoDaddy                     |         活动时可能很低 |    约 150 元+ | 首年促销多，但续费通常较贵             |
| Namecheap                   |            价格较低 |     约 120 元 | 海外常见域名注册商                 |
| Spaceship                   |          约 80 元 |      约 80 元 | 价格相对透明                    |
| NameSilo                    |         约 100 元 |     约 100 元 | 通常包含 WHOIS 隐私保护           |
| Cloudflare Registrar        |          约 75 元 |      约 75 元 | 接近成本价，需要使用 Cloudflare DNS |
| **Google Workspace 特定地区定价** | **可能约 10～15 元** | **以实际页面为准** | 价格受地区、汇率和政策影响             |

普通 `.com` 域名一年通常需要几十元到上百元。

如果 Workspace 当前仍然提供较低的地区定价，那么单个域名一年可能只需要十几元。

对于手里有多个域名的人来说，累计下来差距还是比较明显的。

---

# 二、开始之前需要准备什么？

建议提前准备：

* 一张支持境外支付的 **Visa / Mastercard 信用卡**
* 一个可以正常接收邮件的备用邮箱
* 一个 Google Workspace 管理账号
* 一个 Cloudflare 账号
* 对应地区真实、有效且符合平台要求的注册及账单资料

尽量优先使用正常实体信用卡。

部分虚拟卡、临时支付卡可能触发 Google 的支付风控，导致付款失败或者需要额外验证。

整个流程中会频繁在：

`Google Workspace → Squarespace → Cloudflare`

三个后台之间切换。

因此第一次操作建议完整看完教程再开始。

---

# 三、为什么买 Google 域名却要进入 Squarespace？

这里先解释一个非常容易让人疑惑的问题。

Google 已经将原来的 **Google Domains 域名注册业务出售给 Squarespace**。

因此现在通过 Google Workspace 购买域名后：

* [域名注册](/tags/域名注册/)
* 域名验证
* Nameserver 修改
* DNSSEC 设置
* 域名管理

很多操作都会转到 **Squarespace Domains** 完成。

所以如果你看到网上旧教程还在 Google Domains 后台操作，那些截图很可能已经过时。

现在购买成功后跳转到 Squarespace 属于正常情况。

---

# 四、第一步：通过 Google Workspace 注册域名

进入：

`https://workspace.google.com/`

选择：

**开始免费试用**

然后按照页面提示完成注册。

---

## 1. 创建 Workspace 账号

这里并不要求你提前拥有 Gmail。

Google 会引导你创建一个新的 Workspace 管理账号。

例如最终可能得到：

```text
admin@yourdomain.com
```

这个账号非常重要。

后面登录：

* Google Workspace
* Google Admin
* Squarespace 域名后台

都有可能需要使用。

因此用户名和密码一定保存好。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-009-2498a553.webp)

---

## 2. 填写企业资料

根据页面要求填写：

* 企业名称
* 企业规模
* 所在地区
* 联系人信息
* 联系邮箱

企业规模如果只是自己使用，可以选择：

```text
只有您一人
```

或者类似选项。

需要注意：

> 不同国家和地区显示的域名价格可能不同，最终价格必须以 Google Workspace 实际付款页面为准。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-010-35a7aba3.webp)

---

## 3. 选择「获取新的自定义域名」

注册过程中 Google 会询问：

是否已经拥有域名？

这里选择类似：

```text
获取新的自定义域名
```

然后进入域名搜索页面。

---

## 4. 搜索想购买的域名

输入你准备注册的名字，例如：

```text
yourname.com
```

系统会自动检测域名是否已经被注册。

如果可以注册，就会显示当前地区对应的价格。

某些地区过去曾出现：

```text
75 TRY / 年
```

这样的 `.com` 定价。

按照当时汇率计算，大约相当于十几元人民币。

不过域名价格和汇率都会变化，因此实际金额请以结账页面为准。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-012-a60f6138.webp)

---

## 5. 填写域名注册信息

接下来需要填写域名所有人的联系资料。

通常包括：

* 姓名
* 公司
* 地址
* 国家
* 邮编
* 电话
* 联系邮箱

部分页面会提供类似：

```text
将我的联系信息设为不公开
```

的选项。

开启后，相当于启用 WHOIS 隐私保护。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-013-7bc64ae2.webp)

---

## 6. 创建域名管理员账号

接下来创建 Workspace 用户。

例如：

```text
admin@yourdomain.com
```

这个账号不仅是 Workspace 邮箱，同时也是后面管理域名的重要身份凭证。

建议直接使用：

```text
admin
```

或者你自己容易记住的用户名。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-014-ba7e663e.webp)

---

## 7. 选择 Workspace 套餐

Google 通常会提供 Workspace 商务套餐试用。

例如：

```text
14 天免费试用
```

这里需要特别注意：

### Workspace 费用和域名费用是两笔独立费用

也就是说：

```text
Workspace 服务费
+
域名注册费
```

不是同一个订阅。

Workspace 处于免费试用期时，Workspace 本身可能显示：

```text
0 元
```

但域名注册费用仍然需要正常支付。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-015-1cfb57a2.webp)

---

## 8. 添加付款方式

进入付款页面后添加信用卡。

确认：

* 域名
* 注册年限
* Workspace 套餐
* 域名金额
* 付款币种

全部正确后完成付款。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-016-7b1d620b.webp)

---

## 9. 跳过额外用户

Google 可能询问：

是否继续添加公司员工账号。

个人使用可以选择：

```text
暂时跳过
```

无需创建更多 Workspace 用户。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-017-1dab4997.webp)

---

# 五、第二步：完成 Squarespace 域名验证

域名购买完成之后，还有一个步骤非常重要：

**验证域名联系人邮箱。**

由于现在 Google Domains 已经迁移给 Squarespace，因此相关验证邮件通常会由 Squarespace 发出。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/QQ20260814-200141-c65b93db.png)

---

## 找到 Squarespace 验证邮件

检查注册时留下的联系邮箱。

你应该会收到类似域名验证的邮件。

点击：

```text
Verify Now
```

---

## 使用 Google 账号登录 Squarespace

页面可能要求：

```text
Continue with Google
```

这里建议使用前面创建的 Workspace 账号，例如：

```text
admin@yourdomain.com
```

完成登录。

![不到 11 元注册 .com 域名：Google Workspace 购买 + Squarespace 管理 + Cloudflare 托管完整教程](/uploads/2026/08/wp-022-303db5aa.webp)

---

## 完成邮箱验证

成功后进入：

```text
Squarespace
→ Domains
```

应该能够看到刚刚购买的域名。

然后完成：

```text
Email Successfully Verified
```

邮箱验证。

> 域名联系人验证不要拖太久。如果注册商要求在规定时间内完成验证，长期未验证可能会影响域名正常状态。

到这里，域名注册环节基本完成。

---

# 六、第三步：先别急着取消 Workspace

如果你的目的只是买域名，并不准备长期使用 Workspace，第一反应可能是：

> 域名已经付款了，那现在是不是可以马上取消 Workspace？

建议暂时不要。

更加稳妥的顺序是：

```text
购买域名
↓
完成 Squarespace 邮箱验证
↓
进入 Squarespace 域名后台
↓
修改 Nameserver
↓
Cloudflare 激活成功
↓
确认 DNS 正常
↓
再处理 Workspace 订阅
```

原因是修改域名 Nameserver 时，Squarespace 可能再次要求进行 Google 账号身份验证。

如果提前关闭相关 Workspace 服务，可能增加验证失败的概率。

---

# 七、第四步：把域名托管到 Cloudflare

完成域名购买以后，就可以将 DNS 托管到 Cloudflare。

---

## Cloudflare 后台操作

进入：

`https://dash.cloudflare.com/`

然后：

```text
添加域
```

输入刚刚购买的域名。

例如：

```text
yourdomain.com
```

点击继续。

---

## 选择 Free 免费计划

对于普通博客、个人网站和小型网站：

```text
Free
```

基本就够用了。

Cloudflare 会自动扫描当前域名的 DNS 记录。

确认以后继续。

---

## 获取两个 Cloudflare Nameserver

Cloudflare 会分配两个名称服务器，例如：

```text
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

每个人获得的地址不同。

**不要照抄示例。**

必须使用自己 Cloudflare 页面中实际显示的两个 Nameserver。

这个页面暂时不要关闭。

---

# 八、第五步：在 Squarespace 修改 Nameserver

重新进入 Squarespace。

找到：

```text
Domains
→ 你的域名
→ DNS
→ Domain Nameservers
```

选择：

```text
USE CUSTOM NAMESERVERS
```

也就是使用自定义名称服务器。

---

## 完成 Google 身份验证

Squarespace 可能再次要求使用 Google 账号验证。

使用之前创建的：

```text
admin@yourdomain.com
```

登录。

验证通过以后进入 Nameserver 修改页面。

---

## 填写 Cloudflare Nameserver

将 Cloudflare 提供的两个地址分别复制到 Squarespace。

例如：

```text
alice.ns.cloudflare.com
bob.ns.cloudflare.com
```

然后保存。

---

## 如果提示关闭 DNSSEC 怎么办？

如果之前启用了 DNSSEC，修改 Nameserver 时可能看到：

```text
Changing Nameservers will disable DNSSEC
```

这种情况下通常需要先关闭旧 DNSSEC，再切换 Nameserver。

这是正常步骤。

不要在 Nameserver 还没完全切换到 Cloudflare 时急着重新开启 DNSSEC。

---

# 九、第六步：确认 Cloudflare 托管成功

返回 Cloudflare。

点击类似：

```text
我已更新名称服务器
```

然后等待 Cloudflare 检测。

官方可能提示需要几个小时甚至更长时间。

实际情况下，如果 DNS 更新较快，也可能几分钟就检测成功。

当 Cloudflare 显示类似：

```text
Your site is now protected by Cloudflare
```

或者：

```text
您的域名现在受到 Cloudflare 保护
```

说明域名的 Nameserver 已经成功切换。

---

# 十、第七步：重新启用 DNSSEC

DNSSEC 并不是网站运行的必选项，但开启后可以进一步提升 DNS 安全性。

如果需要开启，建议在 Cloudflare 完全接管域名以后再设置。

正确逻辑是：

```text
Cloudflare 生成 DS 参数
↓
Squarespace 添加 DS Record
↓
等待 DNSSEC 生效
```

---

## Cloudflare 获取 DNSSEC 参数

进入：

```text
Cloudflare
→ DNS
→ Settings
→ DNSSEC
```

点击：

```text
Enable DNSSEC
```

Cloudflare 会生成几项信息。

通常包括：

* Key Tag
* Algorithm
* Digest Type
* Digest

---

## Squarespace 添加 DS Record

返回：

```text
Squarespace
→ Domains
→ DNS
→ DNSSEC
```

选择：

```text
ADD RECORD
```

然后对应填写：

| Cloudflare  | Squarespace |
| ----------- | ----------- |
| Key Tag     | KEY TAG     |
| Algorithm   | ALGORITHM   |
| Digest Type | DIGEST TYPE |
| Digest      | DIGEST      |

全部保持原样复制。

保存即可。

---

# 十一、第八步：取消 Workspace，只保留域名

当确认：

* 域名已经验证
* Squarespace 可以正常管理
* Nameserver 已修改
* Cloudflare 已成功激活
* 网站 DNS 正常

以后，如果确实不需要 Workspace，可以考虑取消 Workspace 服务。

进入：

`https://admin.google.com/`

找到：

```text
结算
→ 订阅
```

---

## 查看订阅项目

一般可以看到两类内容：

```text
Google Workspace
```

以及：

```text
Domain Registration
```

这两个需要区分清楚。

你的目标是：

**取消 Workspace 服务，而不是取消域名。**

---

## 取消 Workspace

进入 Workspace 套餐详情。

找到类似：

```text
更多
→ 取消订阅
```

按照页面提示操作。

取消后重新查看订阅列表。

理想情况下应该只保留：

```text
Domain Registration
```

也就是域名注册服务。

---

# 十二、提前取消 Workspace 导致验证失败怎么办？

这是整个过程中比较容易遇到的坑。

如果你：

```text
刚买完域名
↓
立即取消 Workspace
↓
之后才去 Squarespace 修改 Nameserver
```

可能会遇到 Google 身份验证失败。

例如页面无法正常完成：

```text
Continue with Google
```

验证。

---

## 解决思路

可以重新登录：

`https://admin.google.com/`

进入：

```text
结算
→ 订阅
```

根据 Google 当前提供的选项恢复或重新开通可用的 Workspace 服务。

待账号恢复正常以后，再回到：

```text
Squarespace
→ DNS
→ Domain Nameservers
```

重新进行身份验证。

验证通过后：

1. 修改 Nameserver
2. 等待 Cloudflare 激活
3. 检查 DNS
4. 再决定是否取消 Workspace

这样会稳妥很多。

---

# 十三、整个流程正确顺序

如果第一次操作，建议严格按照下面顺序进行：

```text
注册 Google Workspace
        ↓
搜索并购买 .com 域名
        ↓
创建 Workspace 管理账号
        ↓
完成域名付款
        ↓
接收 Squarespace 验证邮件
        ↓
完成联系人邮箱验证
        ↓
Cloudflare 添加域名
        ↓
获取 Cloudflare Nameserver
        ↓
Squarespace 修改 Nameserver
        ↓
等待 Cloudflare 激活
        ↓
配置网站 DNS
        ↓
可选：重新启用 DNSSEC
        ↓
确认网站和 DNS 正常
        ↓
最后再处理 Workspace 订阅
```

其中最重要的一点就是：

> **不要刚买完域名就急着取消 Workspace。**

先把 Squarespace、Cloudflare 和 Nameserver 全部处理完成，再取消会省掉很多麻烦。

---

# 十四、这种方式适合什么人？

比较适合：

* 手里有多个域名的人
* 个人站长
* 独立开发者
* 博客作者
* Cloudflare Pages / Workers 用户
* 喜欢折腾低成本网站方案的人

如果只是注册一个域名，而且不想折腾 Workspace、Squarespace 和 Cloudflare 三个平台，那么直接使用：

```text
Cloudflare Registrar
Spaceship
Namecheap
NameSilo
```

反而会更加省时间。

但如果当前地区价格确实能做到十几元一年，那么花一点时间走完整个流程，成本优势还是非常明显的。

---

# 十五、最后提醒

这类低价方案最大的变量并不是技术，而是：

* Google 的地区定价
* Squarespace 的域名政策
* Workspace 免费试用政策
* 付款风控
* 汇率变化
* `.com` 注册和续费价格调整

所以网上看到的：

```text
75 TRY / 年
```

或者：

```text
不到 11 元人民币
```

都应该理解为**特定时间、特定地区以及特定汇率下的实测价格**，而不是永久固定价格。

真正付款之前，最重要的是确认结账页面显示的：

```text
域名价格
续费价格
币种
Workspace 订阅费用
自动续费状态
```

只要这几个地方确认清楚，再按照：

**Google Workspace 购买 → Squarespace 管理 → Cloudflare 托管**

这条路线操作，就基本不会出什么大问题。
