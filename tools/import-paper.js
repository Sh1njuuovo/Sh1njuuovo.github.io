#!/usr/bin/env node
/*
 * 把本地写的论文阅读笔记导入成站点文章。
 *
 * 用法：
 *   node tools/import-paper.js <源文件> <短名> <日期> [方向] [标签]
 *
 * 例子：
 *   node tools/import-paper.js ~/intern/search-recommend-study/papers/scaling-up/rankmixer/README.md \
 *     rankmixer 2026-09-12 推荐系统 "特征交互,扩展律"
 *
 * 它会做这几件事：
 *   1. 把一级标题提出来放进 front matter
 *   2. 补上分类（论文 + 方向）和标签
 *   3. 打开公式开关，这样 $$ 公式会由 MathJax 渲染
 *   4. 把指向本地文件、站点之外的相对链接降级成纯文字，避免链接检查失败
 *
 * 生成的文件在 _posts/ 下，导入后请自己看一眼开头几行，特别是标签和摘要。
 */
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const POSTS = path.join(root, "_posts");

const [src, slug, date, direction = "推荐系统", tagArg = ""] = process.argv.slice(2);

if (!src || !slug || !date) {
  console.error("用法：node tools/import-paper.js <源文件> <短名> <日期> [方向] [标签]");
  process.exit(1);
}
if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
  console.error("日期要写成 2026-09-11 这种格式");
  process.exit(1);
}

let text = fs.readFileSync(src, "utf8");

const h1 = text.match(/^#\s+(.+?)\s*$/m);
if (!h1) {
  console.error("源文件里没找到一级标题");
  process.exit(1);
}
const title = h1[1].trim();
text = text.replace(/^#\s+.+?\s*\n/, "");

// 各种「返回上级 / 全部索引」的导航行，站内没有对应页面，换成分类入口
text = text.replace(
  /^\[返回[^\]]*\]\([^)]*\)(\s*·\s*\[[^\]]*\]\([^)]*\))*\s*$/m,
  "[全部论文](/categories/%E8%AE%BA%E6%96%87/)"
);

// 本地 PDF 与本地附件的链接去掉，论文原文用 arXiv 或 DOI 即可
text = text.replace(/\[[^\]]*\.pdf\]\([^)]*\)\s*·\s*/gi, "");
text = text.replace(/^\|\s*(来源|本地)\s*\|.*\n/m, "");

// 其余站点外的相对链接降级成纯文字
text = text.replace(/\[([^\]]+)\]\((?!https?:|mailto:|#|\/)[^)]+\)/g, "$1");

const leftover = text.match(/\]\((?!https?:|mailto:|#|\/)[^)]+\)/g);
if (leftover) {
  console.error("还有没处理的相对链接，请手动检查：", leftover);
  process.exit(1);
}

const tags = tagArg
  ? tagArg
      .split(/[,，]/)
      .map((t) => t.trim())
      .filter(Boolean)
      .map((t) => JSON.stringify(t))
      .join(", ")
  : "";

const summary = "（这里写一句话概括：这篇论文做了什么、结论是什么）";

const front = [
  "---",
  `title: ${JSON.stringify(title)}`,
  `date: ${date} 23:30:00 +0800`,
  `categories: [论文, ${direction}]`,
  `tags: [${tags}]`,
  "description: >-",
  `  ${summary}`,
  "math: true",
  "---",
  ""
].join("\n");

const out = path.join(POSTS, `${date}-${slug}.md`);
fs.writeFileSync(out, front + text.replace(/^\s*\n/, ""));

console.log("已生成 _posts/" + path.basename(out));
console.log("标题：", title);
console.log("分类：论文 /", direction);
console.log("标签：", tags || "（空，自己补一下）");
console.log("\n还要手工做两件事：");
console.log("  1. 把 description 那句占位说明换成真正的摘要");
console.log("  2. 如果原笔记里有别的本地文件链接，检查一下有没有漏掉的");
