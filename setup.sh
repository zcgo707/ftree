#!/bin/bash
set -e

echo "🌳 ftree — 安装脚本"
echo "━━━━━━━━━━━━━━━━━"

# 检测目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="$HOME/.local/bin"
SCRIPT_STORE="$HOME/scripts"

# 1. 安装系统依赖
echo ""
echo "📦 安装系统依赖..."
if command -v apt-get &>/dev/null; then
    sudo apt-get install -y -qq fzf tree 2>/dev/null || echo "  ⚠️  fzf/tree 安装失败，可手动安装"
fi
pip install rich 2>/dev/null || pip3 install rich 2>/dev/null || echo "  ⚠️  rich 安装失败，可手动: pip install rich"

# 2. 复制脚本
echo ""
echo "📂 复制脚本..."
mkdir -p "$SCRIPT_STORE" "$BIN_DIR"

cp "$SCRIPT_DIR/src/ftree.py" "$SCRIPT_STORE/"
cp "$SCRIPT_DIR/src/ftree-widget.py" "$SCRIPT_STORE/"
cp "$SCRIPT_DIR/src/ftree-fzf.sh" "$SCRIPT_STORE/"
cp "$SCRIPT_DIR/src/ftree-popup.sh" "$SCRIPT_STORE/"
cp "$SCRIPT_DIR/bin/ftree" "$BIN_DIR/"
cp "$SCRIPT_DIR/bin/fcd" "$BIN_DIR/"
cp "$SCRIPT_DIR/bin/fcdw" "$BIN_DIR/"

chmod +x "$SCRIPT_STORE"/*.py "$SCRIPT_STORE"/*.sh "$BIN_DIR"/*

echo "  ✅ 脚本已安装到:"
echo "     $SCRIPT_STORE/"
echo "     $BIN_DIR/"

# 3. 添加 bashrc 集成
echo ""
echo "🔧 配置 shell 集成..."
if grep -q ">>> ftree >>>" "$HOME/.bashrc" 2>/dev/null; then
    echo "  ⚠️  ftree 集成已存在，跳过"
else
    cat "$SCRIPT_DIR/config/bashrc-integration.sh" >> "$HOME/.bashrc"
    echo "  ✅ 已添加到 ~/.bashrc"
    echo "  执行以下命令立即生效:"
    echo "    source ~/.bashrc"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 安装完成!"
echo ""
echo "快速开始:"
echo "  ftree --widget ~/projects    桌面小窗"
echo "  fcd ~/projects               fzf 快速跳转"
echo "  fcdw                         从 widget 跳转"
echo "  ftree                        终端目录树"
echo ""
