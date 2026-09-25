#!/usr/bin/env bash
#
# 构建并检查站内链接，等价于 GitHub Actions 里跑的那套
#
# 用法：bash tools/check.sh

set -euo pipefail

cd "$(dirname "$0")/.."
RUBY_HOME="${RUBY_HOME:-/opt/homebrew/opt/ruby@3.4}"
export PATH="$RUBY_HOME/bin:$PATH"

bash tools/test.sh "$@"
