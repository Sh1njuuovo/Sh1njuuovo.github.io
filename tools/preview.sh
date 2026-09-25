#!/usr/bin/env bash
#
# 本地预览，自动使用项目固定的 Ruby 版本
#
# 用法：bash tools/preview.sh

set -euo pipefail

cd "$(dirname "$0")/.."
RUBY_HOME="${RUBY_HOME:-/opt/homebrew/opt/ruby@3.4}"
export PATH="$RUBY_HOME/bin:$PATH"

bash tools/run.sh "$@"
