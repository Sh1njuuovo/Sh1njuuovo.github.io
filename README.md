# Sh1njuuovo 的笔记

个人笔记站，基于 Jekyll 和 [Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) 主题，托管在 GitHub Pages。

访问地址：https://sh1njuuovo.github.io

## 内容结构

侧边栏一共六项，顺序由 `_tabs/` 目录里每个文件的 `order` 决定。

| 侧边栏 | 文件 | 说明 |
| --- | --- | --- |
| 首页 | `index.html` | 文章列表，按时间倒序，每页 10 篇 |
| 力扣索引 | `_tabs/leetcode.md` | 按专题串起来的题单索引 |
| 分类 | `_tabs/categories.md` | 按分类聚合，目前只有「力扣」 |
| 标签 | `_tabs/tags.md` | 按标签聚合，每篇笔记带两个标签 |
| 归档 | `_tabs/archives.md` | 按时间排的文章列表 |
| 常用链接 | `_tabs/links.md` | 刷题、文档、工具的常用入口 |
| 关于 | `_tabs/about.md` | 个人介绍和联系方式 |

## 怎么加一篇新笔记

在 `_posts/` 目录新建一个文件，文件名必须是 `年-月-日-英文短名.md` 的格式，例如 `2026-10-01-binary-indexed-tree.md`。

文件开头是配置，之后是正文。

```markdown
---
title: "树状数组"
date: 2026-10-01 15:00:00 +0800
categories: [力扣]
tags: [树状数组, Hot100]
description: >-
  一句话说明这篇写了什么，会显示在列表页。
---

## 一句话概括

正文从这里开始，一级标题不用写，页面会自动用 title 作为标题。
```

保存之后提交，GitHub 会自动重新构建。分类页、标签页、归档页、相关文章、上一篇下一篇都会自动更新。

标签建议保持两个，一个写专题，一个写题单来源。这样标签页不会太散。

## 手动维护索引

`_tabs/leetcode.md` 里的链接列表需要自己加一行，格式是：

```markdown
- [树状数组](/posts/binary-indexed-tree/) —— Hot 100：315. 计算右侧小于当前元素的个数
```

链接里的 `/posts/` 后面跟的是文件名去掉日期的那一段，要和 `_posts/` 里的文件名对上，否则构建时的链接检查会报错。

## 本地预览

环境固定在项目里，不会改动系统里的 ruby。

```bash
bash tools/setup.sh     # 第一次运行，安装依赖（会用到 Homebrew 的 ruby@3.4，约 70MB，装在 vendor/bundle）
bash tools/preview.sh   # 启动本地预览，浏览器打开 http://127.0.0.1:4000
bash tools/check.sh     # 构建并检查站内链接，和线上跑的是同一套
```

如果不想装本地环境，也可以直接改文件然后提交，让 GitHub 去构建，几分钟后刷新线上页面就行。

## 改文字和外观

| 想改什么 | 改哪里 |
| --- | --- |
| 站点标题、副标题、描述、时区 | `_config.yml` |
| 头像 | `assets/img/avatar.svg` |
| 社交链接 | `_config.yml` 里的 `social`，图标开关在 `_data/contact.yml` |
| 侧边栏文案 | `_data/locales/zh-CN.yml`，键名用文件名（不含扩展名） |
| 关于页、链接页 | `_tabs/about.md`、`_tabs/links.md` |
| 主题配色 | 在 `assets/css/` 下新建覆盖文件，或者直接改 `_sass` 里的变量 |

## 部署

仓库里已经带好 GitHub Actions 的配置，`.github/workflows/pages-deploy.yml` 会在每次推送到 main 分支时构建并发布。

第一次部署需要在仓库的 Settings 里找到 Pages，把 Source 改成 `GitHub Actions`。之后每次 `git push` 都会自动更新站点。

构建参数和线上一致，用的 Ruby 版本是 3.4，并且会拉取 `assets/lib` 子模块来托管主题静态资源，避免依赖国外 CDN。

## 升级主题

主题以 gem 的形式引入，版本写在 `Gemfile` 里。升级时改版本号，本地跑一次 `bash tools/setup.sh` 和 `bash tools/check.sh`，确认没问题再推送。

## 备注

- 笔记正文里写的原始 HTML 会被当成普通文字处理，不会执行。
- `vendor/`、`_site/`、`.bundle/` 都在 `.gitignore` 里，不会提交。
- 站点没有统计脚本，也不接第三方评论。
- PWA 离线缓存是关掉的，原因见下面一节。

## 关于离线缓存（PWA）

`_config.yml` 里 `pwa.enabled` 是 `false`，这是有意为之。

Chirpy 的离线缓存会把首页、标签页和样式存进浏览器。问题是 Service Worker 的脚本文件
本身不会随内容变化，浏览器就不会去刷新缓存，回头访问的人会一直看到旧页面，新写的笔记也刷不出来。
对一个经常更新的笔记站来说，随时拿到最新内容更重要，所以关掉了。

根目录的 `sw.min.js` 是一段一次性清理代码，专门用来处理早期版本注册过缓存的浏览器。
它会把旧的缓存清空、注销自己，然后让页面重新加载。手动改内容之后没有浏览器再注册它，
所以这段代码只会执行一次。不要删掉它，否则装过旧缓存的浏览器没法自己恢复。

每次构建时 Jekyll 会提示 `/sw.min.js` 这个路径被两个文件共用，属于预期情况，不影响构建结果。

如果以后想要离线阅读，把 `_config.yml` 里的 `pwa.enabled` 和 `pwa.cache.enabled` 都改成 `true`，
代价是每次更新内容后，浏览器需要手动清一次缓存才能看到新版。
