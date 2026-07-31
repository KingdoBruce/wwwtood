+++
title = "网站域名应该带 www 还是不带 www？Vercel、Sitemap 与 GSC 设置指南"
date = "2026-07-31T14:34:00+08:00"
draft = false
featured = true
categories = ["随笔"]
tags = ["网站域名", "www域名", "非www域名", "Vercel域名设置", "Google Search Console", "Sitemap", "Canonical URL", "Google SEO", "301重定向", "域名规范化"]
+++

网站上线时，经常需要在下面两种域名格式中选择一种：

```text
https://tood.win
https://www.tood.win
```

从 [Google](/tags/google/) [SEO](/tags/seo/) 的角度看，带不带 `www` 本身没有明显的排名差异。真正重要的是：**选择一个主域名，并让重定向、Canonical、Sitemap、站内链接和 [Google Search Console](/tags/google-search-console/) 保持一致。**

---

![网站域名应该带 www 还是不带 www？Vercel、Sitemap 与 GSC 设置指南](/uploads/2026/07/ChatGPT_Image_2026731_14_47_02-7612a27b.jpg)

## 一、为什么 Vercel 推荐使用 www 域名？

在 Vercel 中添加根域名，例如：

```text
tood.win
```

平台通常会建议同时添加：

```text
www.tood.win
```

并将不带 `www` 的根域名重定向到带 `www` 的版本。

Vercel 推荐将 `www` 设置为主域名，主要是因为 DNS 结构上的差异：

* `www.tood.win` 属于子域名，可以直接使用 CNAME 记录。
* `tood.win` 属于根域名，也叫 Apex Domain，传统 DNS 规范不允许直接使用普通 CNAME。
* 使用 `www` 后，Vercel 可以更灵活地控制流量调度、CDN 路由、可靠性和安全策略。

因此，Vercel 官方推荐的结构通常是：

```text
tood.win
↓ 308 或 301 重定向
www.tood.win
```

这是一种基础设施方面的推荐，不代表不带 `www` 的网站速度一定更慢，也不代表不带 `www` 会影响 [Google SEO](/tags/google-seo/)。

---

## 二、如何将 Vercel 改成不带 www？

更喜欢简洁域名时，也可以将不带 `www` 的版本设置为主域名，例如：

```text
https://tood.win
```

操作路径：

```text
Vercel Dashboard
→ 选择项目
→ Settings
→ Domains
```

然后进行以下设置：

1. 找到 `tood.win`。
2. 将它设置为项目的主域名。
3. 编辑 `www.tood.win`。
4. 将 `www.tood.win` 重定向到 `tood.win`。

最终结构应为：

```text
www.tood.win
↓
tood.win
```

设置完成后，建议分别访问下面两个地址进行检查：

```text
https://tood.win
https://www.tood.win
```

无论访问哪一个，都应该最终停留在同一个主域名上。

> 不带 `www` 只是网址看起来更短，并没有权威证据表明它对移动端体验或 [Google](/tags/google/) 排名更有优势。

---

## 三、Sitemap 中的 URL 是否必须带 www？

取决于网站最终使用的主域名。

假设网站的主域名是：

```text
https://www.tood.win
```

那么 Sitemap 中也应该使用带 `www` 的最终 URL：

```xml
<url>
  <loc>https://www.tood.win/article/example/</loc>
</url>
```

不要写成：

```xml
<url>
  <loc>https://tood.win/article/example/</loc>
</url>
```

因为后者访问后还需要重定向到带 `www` 的地址。

Google 建议 Sitemap 提交网站希望被索引的规范 URL，也就是 Canonical URL。Sitemap 中出现重定向地址通常不会导致严重的 [SEO](/tags/seo/) 惩罚，但会向 Google 发送不一致的信号，也会增加一次不必要的重定向处理。

因此，下面几处应保持完全一致：

```text
网站主域名
Canonical URL
Sitemap URL
站内链接
Open Graph URL
结构化数据中的 URL
```

### 带 www 的正确示例

```text
主域名：https://www.tood.win
Sitemap：https://www.tood.win/sitemap.xml
Canonical：https://www.tood.win/article/example/
```

### 不带 www 的正确示例

```text
主域名：https://tood.win
Sitemap：https://tood.win/sitemap.xml
Canonical：https://tood.win/article/example/
```

---

## 四、[Google Search Console](/tags/google-search-console/) 应该添加哪个域名？

Google Search Console 提供两种资源类型：

* 网域资源（Domain Property）
* 网址前缀资源（URL-prefix Property）

它们的统计范围不同。

### 方案一：网域资源

添加时只填写域名：

```text
tood.win
```

不要填写：

```text
https://tood.win
www.tood.win
```

网域资源可以统一查看该域名下的不同协议和子域名数据，包括：

```text
http://tood.win
https://tood.win
http://www.tood.win
https://www.tood.win
```

这种方式需要通过 DNS TXT 记录验证，适合查看整个网站的数据，也是大多数网站比较省心的选择。

验证完成后，在该资源中提交实际主域名对应的 Sitemap：

```text
https://www.tood.win/sitemap.xml
```

或者：

```text
https://tood.win/sitemap.xml
```

具体使用哪个，取决于网站最终设置的主域名。

### 方案二：网址前缀资源

网址前缀资源必须填写完整协议和域名，例如：

```text
https://www.tood.win/
```

它只统计该前缀下面的数据，不会自动包含其他版本。

例如：

```text
https://tood.win/
```

和：

```text
https://www.tood.win/
```

在网址前缀资源中属于两个不同的统计范围。

如果网站已经统一使用：

```text
https://www.tood.win/
```

但 GSC 中添加的是：

```text
https://tood.win/
```

那么这个资源中可能主要看到重定向页面，而无法完整查看带 `www` 页面对应的索引和搜索表现数据。

这通常不会直接影响 Google 对网站的正常索引，但会导致 GSC 数据查看、URL 检查和 Sitemap 管理不方便。

正确处理方式是新增：

```text
https://www.tood.win/
```

或者直接新增网域资源：

```text
tood.win
```

不需要删除原来的资源，旧数据可以继续保留。

---

## 五、推荐的最终配置

假设选择带 `www` 作为主域名，建议配置如下：

```text
主域名：
https://www.tood.win

重定向：
https://tood.win
→ https://www.tood.win

Sitemap：
https://www.tood.win/sitemap.xml

Canonical：
https://www.tood.win/当前页面路径/

GSC 网域资源：
tood.win

可选的网址前缀资源：
https://www.tood.win/
```

如果选择不带 `www`，只需要将以上地址统一替换为：

```text
https://tood.win
```

---

## 六、网站上线后的检查清单

完成配置后，检查以下项目：

* 带 `www` 和不带 `www` 是否只有一个版本返回正常页面。
* 另一个版本是否通过永久重定向跳转到主域名。
* 浏览器最终地址是否为设定的主域名。
* Sitemap 中是否全部使用主域名。
* 页面 `rel="canonical"` 是否指向主域名。
* 站内链接是否直接使用最终 URL，而不是经过重定向。
* GSC 是否添加了网域资源。
* GSC 中提交的 Sitemap 是否可以正常读取。
* HTTP 是否统一跳转到 HTTPS。
* 页面是否不存在重定向循环或多次跳转。

可以使用下面的命令检查响应头：

```bash
curl -I https://tood.win
curl -I https://www.tood.win
```

其中一个地址应该返回正常页面，另一个地址应该重定向到主域名。

---

## 总结

带 `www` 和不带 `www` 都可以正常进行 [Google SEO](/tags/google-seo/)。

Vercel 推荐 `www`，主要是因为子域名可以使用 CNAME，让平台更灵活地管理 CDN、流量路由和安全策略，而不是因为 `www` 本身具有排名优势。

网站真正需要避免的，是多个地方使用不同的域名版本：

```text
页面使用 www
Sitemap 不带 www
Canonical 使用 www
站内链接又不带 www
```

最稳妥的原则只有一句：

> 确定一个主域名，然后让重定向、Canonical、Sitemap、站内链接和 GSC 配置全部保持一致。

## 官方参考资料

* Vercel：Deploying and Redirecting Domains
* Vercel：Adding and Configuring a Custom Domain
* Google Search Central：Canonical URL 规范
* Google Search Central：Sitemap 指南
* Google Search Console：Domain Property
* Google Search Console：URL-prefix Property
