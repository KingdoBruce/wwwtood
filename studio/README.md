# TOOD Studio

TOOD Studio 是该 Hugo 博客的本地可视化内容管理器。

## 用户使用

解压 `TOOD-Studio-Windows.zip`，将完整的 `TOOD-Studio-Windows` 文件夹放在博客根目录，然后双击其中的 `TOOD-Studio.exe`。程序会自动打开本地管理页面。

请不要只复制 EXE；同目录的 `_internal` 文件夹包含程序运行所需的组件。

- 编辑网站名称、首页文字、导航和 Logo
- 新建、编辑、删除文章
- 上传并插入图片
- 启动 Hugo 实时预览
- 构建检查
- 一键提交并推送 GitHub

程序仅监听 `127.0.0.1`，不会开放给局域网访问。GitHub 登录使用电脑现有的 Git 凭据。

## 跨平台

源码支持 Windows、macOS 和 Linux。发行包必须在对应系统分别构建：Windows 为 `.exe`，macOS 为 `.app`，Linux 可打包为 AppImage。

## 开发运行

安装 `requirements.txt` 后运行 `python app.py`。普通用户不需要执行这些命令。
