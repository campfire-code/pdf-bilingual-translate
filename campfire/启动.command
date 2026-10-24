#!/bin/bash
# 篝火：双击启动（macOS）。第一次运行会自动下载 Python 和依赖。
cd "$(dirname "$0")" || exit 1
# ===== 篝火填写：每个工具不同 =====
TOOL_NAME="PDF 双语翻译（保版式）"
PY_VERSION="3.12"
INSTALL_CMD="uv pip install ."
RUN_CMD="pdf2zh -i"
OPEN_URL=""
# ===================================
echo; echo "  $TOOL_NAME · 篝火出品"; echo "  第一次运行会自动下载 Python 和依赖，需要几分钟，请保持联网；第一次翻译还会下载版面识别模型。"; echo
fail() { echo; echo "启动失败：请截图这个窗口，到 GitHub 仓库的 Issues 反馈。"; read -r -p "按回车关闭"; exit 1; }
if ! command -v uv >/dev/null 2>&1; then
  echo "正在安装 uv（Python 环境管理工具）..."
  curl -LsSf https://astral.sh/uv/install.sh | sh || fail
  export PATH="$HOME/.local/bin:$PATH"
fi
if [ ! -f .venv/campfire-ready ]; then
  read -r -p "使用国内镜像加速下载依赖吗？直接回车表示使用 [Y/n]：" m
  [ "$m" = "n" ] || [ "$m" = "N" ] || export UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
  uv venv --python "$PY_VERSION" .venv || fail
  source .venv/bin/activate
  eval "$INSTALL_CMD" || fail
  touch .venv/campfire-ready
else
  source .venv/bin/activate
fi
[ -n "$OPEN_URL" ] && (sleep 6; open "$OPEN_URL") &
echo "正在启动，浏览器会自动打开中文网页界面（没打开请访问 http://localhost:7860/），关闭这个窗口即可退出。"
eval "$RUN_CMD"
