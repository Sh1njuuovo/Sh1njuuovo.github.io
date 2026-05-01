# Shinjuu 的个人主页

这是我的个人主页仓库，使用纯静态 HTML/CSS 构建，并通过 GitHub Pages 部署。主页主要用于介绍我自己，记录学习过程、项目尝试、未来方向和代码之外的兴趣。

访问地址：[https://sh1njuuovo.github.io/](https://sh1njuuovo.github.io/)

## 主页内容

- Hero：名字、个人简介、头像、GitHub / Projects / Notes / Contact 入口
- About Me：研 0、教育背景、最近在做的事情
- Projects：AI Paper Assistant、个人主页、学习中的实验
- Notes：学习笔记、项目日志、AI 工具使用记录的预留入口
- Skills：I use / I’m learning 两类技能栈
- Experience：2022-2026 河海大学 信息科学与工程学院 物联网工程
- Outside the Code：J-pop、galgame、推し等个人兴趣
- Contact：GitHub 入口

## 文件结构

```text
.
├── index.html
└── README.md
```

## 本地预览

这个网站没有构建步骤，直接在浏览器中打开 `index.html` 即可预览。

也可以在仓库目录启动一个本地静态服务：

```bash
python3 -m http.server 8000
```

然后访问：

```text
http://localhost:8000
```

## 部署

该仓库命名为 `Sh1njuuovo.github.io`，推送到 GitHub 后会由 GitHub Pages 自动部署到：

```text
https://sh1njuuovo.github.io/
```

## 维护建议

- 项目成熟后，为每个项目补充 GitHub 仓库、Demo、截图或文档链接。
- 如果后续开始写博客，可以把 Notes 区块改成真实文章列表。
- 如果后续方向更明确，可以增加 Research / Experience / Publications 等区块。
- 主页内容建议保持真实和简洁，不需要过早包装成成果展示页。
