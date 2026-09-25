#!/usr/bin/env bash
#
# 准备本地构建环境
#
# 思路是把环境固定在项目里，不动系统的 ruby：
#   1. 用 Homebrew 的 ruby@3.4（keg-only，不会进入 PATH，不影响系统 ruby）
#   2. gem 依赖装到项目内的 vendor/bundle（.gitignore 已忽略）
#   所以不管机器上原本是什么 ruby，构建结果都是一致的。
#
# 用法：bash tools/setup.sh

set -euo pipefail

cd "$(dirname "$0")/.."

RUBY_HOME="${RUBY_HOME:-/opt/homebrew/opt/ruby@3.4}"

if [ ! -x "$RUBY_HOME/bin/ruby" ]; then
  echo "没有找到 $RUBY_HOME，尝试用 Homebrew 安装（不会替换系统的 ruby）"
  brew install ruby@3.4
fi

export PATH="$RUBY_HOME/bin:$PATH"

echo "使用的 Ruby：$(ruby -v)"
echo "依赖目录：$(pwd)/vendor/bundle"

bundle config set --local path vendor/bundle
bundle install

echo
echo "环境准备好了。接下来可以："
echo "  bash tools/run.sh     本地预览，浏览器打开 http://127.0.0.1:4000"
echo "  bash tools/test.sh    构建并检查站内链接"
