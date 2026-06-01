#!/bin/bash
# ───────────────────────────────────────────────────────────
# ftree-popup — tmux 浮动窗口文件树导航
# 在 tmux 会话中打开一个置顶浮动窗口显示文件树
# 用法: ftree-popup [目录]
# ───────────────────────────────────────────────────────────

VERSION="1.1.0"
DIR="${1:-.}"
DIR=$(realpath "$DIR" 2>/dev/null || echo "$PWD")

# 颜色
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

usage() {
    echo -e "${CYAN}ftree-popup v${VERSION}${NC} — tmux 浮动文件树"
    echo ""
    echo "用法:"
    echo "  ftree-popup [目录]          在浮动窗口显示目录树"
    echo "  ftree-popup --fzf [目录]    浮动窗口 + fzf 导航"
    echo "  ftree-popup --help          显示帮助"
    echo ""
    echo "说明:"
    echo "  在 tmux 会话中使用 display-popup 创建一个"
    echo "  浮动置顶窗口，显示实时文件树。"
    echo "  适用于边编码边查看文件结构。"
}

# 检查是否在 tmux 中
check_tmux() {
    if [ -z "$TMUX" ]; then
        echo -e "${YELLOW}⚠ 不在 tmux 会话中${NC}"
        echo "请先启动 tmux:"
        echo "  tmux new-session -s main"
        echo ""
        echo "或者直接使用: ftree.py --watch $DIR"
        return 1
    fi
    return 0
}

# tmux 浮动窗口显示目录树
popup_tree() {
    check_tmux || return 1
    
    echo -e "${GREEN}🌳 在 tmux 浮动窗口中打开: $DIR${NC}"
    echo -e "${CYAN}提示: 按 q 或 Esc 关闭浮动窗口${NC}"
    
    tmux display-popup \
        -h 80% \
        -w 80% \
        -E "ftree.py --watch '$DIR'; echo ''; echo -e '${CYAN}按 Enter 关闭...${NC}'; read"
}

# tmux 浮动窗口 + fzf 导航
popup_fzf() {
    check_tmux || return 1
    
    echo -e "${GREEN}🌳 在 tmux 浮动窗口中打开 fzf 导航: $DIR${NC}"
    echo -e "${CYAN}选择目录后将自动 cd${NC}"
    
    tmux display-popup \
        -h 85% \
        -w 85% \
        -E "ftree-fzf.sh --cd '$DIR' && echo -e '${GREEN}已选中目录${NC}'; echo ''; echo -e '${CYAN}按 Enter 关闭...${NC}'; read"
}

# ── Main ──────────────────────────────────────────────────────────
case "${1:-}" in
    --help|-h)
        usage
        ;;
    --fzf|-f)
        shift
        popup_fzf "${1:-.}"
        ;;
    --version|-v)
        echo "ftree-popup v${VERSION}"
        ;;
    *)
        popup_tree "$@"
        ;;
esac
