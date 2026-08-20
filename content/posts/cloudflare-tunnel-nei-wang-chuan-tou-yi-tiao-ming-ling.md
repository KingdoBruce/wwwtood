+++
title = "Cloudflare Tunnel 内网穿透教程：一条命令把本地服务暴露到公网"
date = "2026-08-03T14:44:00+08:00"
draft = false
description = "本文介绍如何使用 Cloudflare Tunnel 将本地服务安全地连接到公网。临时演示可以通过一条 cloudflared tunnel --url 命令生成 HTTPS 公网地址；需要固定域名和长期运行时，则可创建命名隧道、配置 DNS 和系统服务。文章同时说明 Quick Tunnel 的并发、SSE 和稳定性限制，并提供多服务配置、常见故障排查与安全建议。"
categories = ["Tech Notes"]
tags = ["本地服务公网访问", "Webhook 调试", "无公网 IP", "开发工具"]
+++

本地项目已经运行成功，却无法发给同事或客户查看？调试微信、支付宝或 Stripe Webhook 时，需要填写公网 HTTPS 回调地址，但你手里只有 `localhost`？

[Cloudflare](/tags/cloudflare/) Tunnel 可以让本地设备主动连接 Cloudflare 网络，再把公网请求转发到本地服务。整个过程不要求家庭宽带拥有公网 IP，也不需要在路由器上开放入站端口。

对于临时演示，只需要一条命令。

```bash
cloudflared tunnel --url http://localhost:3000
```

运行后，终端会生成一个类似下面的临时公网地址：

```text
https://random-name.trycloudflare.com
```

![Cloudflare Tunnel 内网穿透教程：一条命令把本地服务暴露到公网](/uploads/2026/08/Ch202683_14_47_13-1611ee7b.jpg)

把这个地址发给其他人，对方就能访问你电脑上运行的 `localhost:3000` 服务。

> Quick Tunnel 主要用于开发、测试和临时演示，不适合部署正式网站或长期业务。

## Cloudflare Tunnel 是什么？

传统端口映射通常要求路由器拥有公网 IP，并且需要开放端口。Cloudflare Tunnel 的工作方式不同：

```text
公网访客
   ↓
Cloudflare 网络
   ↓
加密隧道
   ↓
cloudflared
   ↓
本地服务
```

`cloudflared` 会从本地设备主动建立出站连接，因此通常不需要：

* 公网 IPv4 地址
* 路由器端口转发
* 将服务器端口直接开放到公网
* 自建带公网 IP 的 FRP 服务端

这可以减少直接暴露源站 IP 和入站端口带来的风险，但并不代表本地应用可以取消登录验证、权限控制或安全更新。

## 适合哪些使用场景？

Cloudflare Tunnel 比较适合以下需求：

* 临时分享本地开发环境
* 给客户演示尚未部署的项目
* 调试 Webhook 和第三方支付回调
* 分享本地 API 或测试页面
* 远程访问 NAS 管理页面
* 为家庭服务器建立固定访问入口

如果只是临时分享项目，使用 Quick Tunnel 即可；如果需要固定域名和长期运行，应使用命名隧道。

## 一、安装 cloudflared

### macOS

使用 Homebrew 安装：

```bash
brew install cloudflared
```

### Windows

可以使用 [WinGet](/tags/winget/)：

```powershell
winget install --id Cloudflare.cloudflared
```

安装完成后关闭并重新打开 PowerShell，然后检查版本：

```powershell
cloudflared --version
```

也可以前往官方 GitHub Releases 页面下载 Windows MSI 或可执行文件。

### Ubuntu / Debian

添加 Cloudflare 官方软件源：

```bash
sudo mkdir -p --mode=0755 /usr/share/keyrings

curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg \
  | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null

echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main" \
  | sudo tee /etc/apt/sources.list.d/cloudflared.list

sudo apt-get update
sudo apt-get install cloudflared
```

安装后检查版本：

```bash
cloudflared --version
```

## 二、一条命令创建临时公网地址

假设本地项目运行在：

```text
http://localhost:3000
```

执行：

```bash
cloudflared tunnel --url http://localhost:3000
```

终端会返回一个随机的 `trycloudflare.com` 地址：

```text
https://random-name.trycloudflare.com
```

只要终端中的 `cloudflared` 进程仍在运行，这个公网地址就可以访问。

按下 `Ctrl + C` 停止进程后，隧道会断开。再次运行命令时，通常会生成新的随机地址。

### 本地服务使用 HTTPS

如果本地服务本身运行在 HTTPS：

```bash
cloudflared tunnel --url https://localhost:3000
```

不过，本地自签名证书可能触发 TLS 验证问题。开发环境遇到证书错误时，应优先检查本地证书配置，而不是直接关闭所有安全验证。

### 减少日志输出

```bash
cloudflared tunnel --url http://localhost:3000 --loglevel error
```

## 三、Quick Tunnel 的限制

Quick Tunnel 虽然方便，但不是正式部署方案。

目前需要注意：

* 每次运行生成的随机域名可能不同
* 官方不保证 SLA 或持续可用性
* 最多支持 200 个正在处理的并发请求
* 超过限制可能返回 HTTP `429`
* 不支持 Server-Sent Events，也就是 SSE
* 主要用于开发、测试和临时演示
* `.cloudflared` 目录中存在 `config.yaml` 时，Quick Tunnel 可能无法启动

如果项目需要固定域名、长期运行、访问控制或更稳定的配置，建议创建正式的 Cloudflare Tunnel。

## 四、使用固定域名创建命名隧道

命名隧道需要：

* Cloudflare 账号
* 一个已经接入 Cloudflare DNS 的域名
* 在本地或服务器上运行 `cloudflared`

下面以 `demo.example.com` 转发到 `localhost:3000` 为例。

### 第一步：登录 Cloudflare

```bash
cloudflared tunnel login
```

命令会打开浏览器，要求登录 Cloudflare 并选择对应域名。

授权成功后，本地 `.cloudflared` 目录中会生成认证文件。

### 第二步：创建隧道

```bash
cloudflared tunnel create my-tunnel
```

执行成功后会显示隧道 UUID，并生成类似下面的凭据文件：

```text
~/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json
```

查看已经创建的隧道：

```bash
cloudflared tunnel list
```

### 第三步：绑定域名

```bash
cloudflared tunnel route dns my-tunnel demo.example.com
```

这条命令会在 Cloudflare DNS 中创建一条指向隧道的 CNAME 记录。

### 第四步：创建配置文件

Linux 和 macOS 默认配置路径：

```text
~/.cloudflared/config.yml
```

Windows 默认配置路径：

```text
%USERPROFILE%\.cloudflared\config.yml
```

配置示例：

```yaml
tunnel: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
credentials-file: /home/your-user/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json

ingress:
  - hostname: demo.example.com
    service: http://localhost:3000

  - service: http_status:404
```

请将：

* `tunnel` 修改为实际隧道 UUID
* `credentials-file` 修改为实际 JSON 文件路径
* `demo.example.com` 修改为自己的域名
* `localhost:3000` 修改为本地服务地址

最后一条 `http_status:404` 是兜底规则。使用 `ingress` 配置时，最后必须有一条能够匹配剩余请求的规则。

### 第五步：启动隧道

```bash
cloudflared tunnel run my-tunnel
```

启动成功后，可以通过下面的固定地址访问本地服务：

```text
https://demo.example.com
```

注意，固定域名并不代表本地服务永远在线。电脑关机、网络断开或 `cloudflared` 停止运行后，公网地址仍然存在，但无法连接到本地服务。

## 五、一个隧道绑定多个本地服务

同一个命名隧道可以根据不同子域名转发到不同服务：

```yaml
tunnel: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
credentials-file: /home/your-user/.cloudflared/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.json

ingress:
  - hostname: app.example.com
    service: http://localhost:3000

  - hostname: api.example.com
    service: http://localhost:8080

  - hostname: nas.example.com
    service: http://192.168.1.10:5000

  - service: http_status:404
```

对应关系如下：

| 公网地址              | 本地服务                |
| ----------------- | ------------------- |
| `app.example.com` | `localhost:3000`    |
| `api.example.com` | `localhost:8080`    |
| `nas.example.com` | `192.168.1.10:5000` |

修改配置后，需要重新启动 `cloudflared` 才能应用新配置。

## 六、配置为系统服务

长期使用时，不建议每次开机后手动运行。可以把 `cloudflared` 安装为系统服务。

Linux：

```bash
sudo cloudflared --config /home/your-user/.cloudflared/config.yml service install
```

然后检查服务状态：

```bash
sudo systemctl status cloudflared
```

常用管理命令：

```bash
sudo systemctl start cloudflared
sudo systemctl stop cloudflared
sudo systemctl restart cloudflared
```

Windows 也支持将 `cloudflared` 安装为服务，但配置文件路径、运行账户和凭据权限需要正确设置。

## 七、常见问题

### 1. 公网地址打开后显示 502

通常表示 Cloudflare Tunnel 已连接，但 `cloudflared` 无法访问本地服务。

检查本地端口：

```bash
curl http://localhost:3000
```

还要确认：

* 本地项目是否已经启动
* HTTP 和 HTTPS 是否填写正确
* 端口号是否正确
* Docker 服务是否只监听容器内部
* 防火墙是否阻止本机访问

### 2. Quick Tunnel 无法启动

检查下面的目录中是否存在 `config.yaml`：

```text
~/.cloudflared/
```

Quick Tunnel 与现有配置文件可能发生冲突。可以暂时重命名配置文件后再测试。

### 3. Vite 页面提示 Host not allowed

部分开发服务器会检查请求的 Host。使用 Quick Tunnel 时，需要把 `.trycloudflare.com` 加入开发服务器允许的 Host 列表。

不要为了省事在正式环境中永久允许所有 Host。

### 4. 电脑重启后无法访问

命名隧道只会保留域名和隧道配置，不会自动启动本地进程。

需要：

* 将 `cloudflared` 安装为系统服务
* 设置本地应用开机启动
* 确认配置文件和凭据路径正确

### 5. 能不能直接暴露数据库端口？

不建议把 MySQL、PostgreSQL、Redis 等数据库直接发布到公网。

数据库、SSH、RDP 等非 HTTP 服务，更适合结合 Cloudflare Access、WARP 和身份认证使用，而不是创建一个任何人都能访问的公共入口。

## 八、安全建议

Cloudflare Tunnel 减少了开放路由器端口的需求，但它仍然会为本地服务建立公网入口。

正式使用前至少做好以下设置：

1. 为管理后台设置强密码和多因素认证。
2. 不要直接公开数据库、Docker API、路由器后台和无密码 NAS。
3. 使用 Cloudflare Access 限制允许访问的账号。
4. 定期更新 `cloudflared` 和本地应用。
5. 检查应用日志和 Cloudflare 安全事件。
6. 不要在配置文件或公开仓库中提交隧道凭据 JSON。
7. 演示完成后及时关闭不再使用的 Quick Tunnel。

## Quick Tunnel 和命名隧道怎么选？

| 对比项目     | Quick Tunnel    | 命名隧道            |
| -------- | --------------- | --------------- |
| 是否需要账号   | 不需要             | 需要              |
| 是否需要自有域名 | 不需要             | 公开固定域名通常需要      |
| 公网地址     | 随机地址            | 固定域名            |
| 适合场景     | 临时演示、Webhook 调试 | NAS、测试环境、长期服务   |
| 配置难度     | 一条命令            | 需要域名和隧道配置       |
| 是否适合生产环境 | 不适合             | 可用于正式场景，但仍需安全配置 |

## 总结

临时把本地服务分享给别人，只需要记住：

```bash
cloudflared tunnel --url http://localhost:<端口>
```

例如：

```bash
cloudflared tunnel --url http://localhost:3000
```

需要固定域名和长期运行时，则使用：

```text
命名隧道 + 自有域名 + config.yml + 系统服务
```

Cloudflare Tunnel 的主要价值不是“完全没有风险”，而是在不开放路由器入站端口、不要求公网 IP 的情况下，为本地服务建立一个更容易管理的公网入口。

## 官方项目与参考资料

* GitHub 项目：[cloudflare/cloudflared](https://github.com/cloudflare/cloudflared)
* 官方下载文档：[Cloudflare Tunnel Downloads](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/)
* Quick Tunnel 文档：[TryCloudflare Quick Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/)
* 命名隧道教程：[Create a locally-managed tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/create-local-tunnel/)
* 配置文件说明：[Cloudflare Tunnel configuration file](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/configuration-file/)
