#!/bin/bash
# ───────────────────────────────────────────────────────────
# ftree-fzf — 快速目录跳转 (fzf + tree 预览)
# 用法: ftree-fzf [目录]     → 跳转到选中目录
#       ftree-fzf --cd       → 输出路径供 cd (source 用)
# ───────────────────────────────────────────────────────────

VERSION="1.1.0"

# 颜色定义
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; DIM='\033[2m'; NC='\033[0m'

usage() {
    echo "🌳 ftree-fzf v${VERSION} — 快速目录跳转"
    echo ""
    echo "用法:"
    echo "  ftree-fzf [目录]            跳转到选中的目录"
    echo "  ftree-fzf --cd [目录]       输出目录路径 (用于 source 加载)"
    echo "  ftree-fzf --install         安装到 .bashrc"
    echo "  ftree-fzf --help            显示帮助"
    echo ""
    echo "快捷键 (在 fzf 界面中):"
    echo "  ↑↓         导航"
    echo "  Enter       跳转到选中目录"
    echo "  Ctrl-R      重新加载目录树"
    echo "  Esc/Ctrl-C  取消"
    echo "  /           搜索过滤"
    echo "  Tab         多选"
    echo "  ?           切换预览"
}

# 获取目录列表
get_dirs() {
    local root="${1:-.}"
    root=$(realpath "$root" 2>/dev/null) || root="$PWD"
    
    # 使用 tree 或 find 获取目录列表
    if command -v tree &>/dev/null; then
        # tree -d --sort=name -f 输出完整路径
        tree -d --sort=name -f "$root" 2>/dev/null | grep -v '^$' | grep '/' | sed 's/.*│//g' | sed 's/.*── //g' | sed 's/^[[:space:]]*//'
    else
        # fallback: 使用 find
        find "$root" -type d -not -path '*/\.*' -not -path '*/node_modules/*' \
            -not -path '*/.git/*' -not -path '*/__pycache__/*' \
            -not -path '*/miniconda3/*' -not -path '*/envs/*/pkgs/*' \
            2>/dev/null | sort
    fi
}

# 主函数
ftree_fzf() {
    local root="${1:-.}"
    local mode="${2:-goto}"  # goto 或 cd
    
    root=$(realpath "$root" 2>/dev/null) || root="$PWD"
    
    if [ ! -d "$root" ]; then
        echo -e "${RED}❌ 目录不存在: $root${NC}" >&2
        return 1
    fi
    
    echo -e "${CYAN}🌳 扫描目录树: ${root}${NC}" >&2
    
    # 获取目录列表 (生成相对路径)
    local dir_list
    if command -v tree &>/dev/null; then
        # 使用 tree 生成好看的目录结构
        dir_list=$(tree -d --sort=name -f "$root" 2>/dev/null | \
                   grep -v '^$' | grep -v 'directories$' | \
                   sed 's/.*── //' | sed 's/^[[:space:]]*//' | \
                   tail -n +2 | head -n -1)
    else
        dir_list=$(find "$root" -type d -not -path '*/\.*' \
                   2>/dev/null | sed "s|^$root/||" | sed 's|^\.$|/|' | sort)
    fi
    
    if [ -z "$dir_list" ]; then
        # Fallback: 只显示自己
        echo "."
    fi
    
    # 构建预览命令
    local preview_cmd=""
    if command -v tree &>/dev/null; then
        preview_cmd="tree -C -L 2 --dirsfirst {} 2>/dev/null | head -50"
    else
        preview_cmd="ls -la {} 2>/dev/null | head -30"
    fi
    
    # 从根目录计算相对路径的预览
    local full_preview_cmd="tree -C -L 2 --dirsfirst '$root/{}' 2>/dev/null | head -50"
    
    # 启动 fzf
    local selected
    selected=$(echo "$dir_list" | fzf \
        --height=85% \
        --layout=reverse \
        --border \
        --border-label=' 🌳 ftree-fzf ' \
        --border-label-pos=2 \
        --color='border:#60a5fa,label:#60a5fa' \
        --preview="$full_preview_cmd" \
        --preview-window='right:55%:border-rounded' \
        --header=$'↑↓ 导航  |  Enter 跳转  |  / 搜索  |  Tab 多选  |  Ctrl-R 刷新  |  Esc 退出' \
        --header-first \
        --prompt='📁 > ' \
        --pointer='▶ ' \
        --marker='✓ ' \
        --ansi \
        --bind='ctrl-r:reload(eval "get_dirs $root")' \
        --bind='?:toggle-preview' \
        --bind='alt-v:preview-page-up' \
        --bind='alt-V:preview-page-down' \
        2>/dev/null)
    
    if [ -n "$selected" ]; then
        # 构建完整路径
        local full_path
        if [[ "$selected" == /* ]]; then
            full_path="$selected"
        elif [[ "$selected" == "." ]]; then
            full_path="$root"
        else
            full_path="$root/$selected"
        fi
        
        # 确保是目录
        if [ ! -d "$full_path" ]; then
            # 尝试从树输出解析
            full_path=$(echo "$selected" | sed 's/.*\/\(.*\)/\1/')
            local try_path="$root/$full_path"
            [ -d "$try_path" ] && full_path="$try_path"
        fi
        
        # 输出
        if [ "$mode" = "cd" ]; then
            # 输出路径供 shell 使用
            echo "$full_path"
        else
            echo -e "${GREEN}✓ 选中: ${full_path}${NC}" >&2
            echo "$full_path"
        fi
        return 0
    else
        echo -e "${YELLOW}⚠ 取消选择${NC}" >&2
        return 1
    fi
}

# 安装到 .bashrc
install_ftree() {
    local bashrc="$HOME/.bashrc"
    local marker="# >>> ftree >>>"
    
    if grep -q "$marker" "$bashrc" 2>/dev/null; then
        echo -e "${YELLOW}⚠ ftree 已经安装到 .bashrc${NC}"
        return
    fi
    
    cat >> "$bashrc" << 'EOF'

# >>> ftree >>> — 文件树导航 (由 ftree-fzf 安装)
export FZF_DEFAULT_OPTS='--color=fg:#e2e8f0,bg:#0f172a,hl:#60a5fa --color=fg+:#f1f5f9,bg+:#1e293b,hl+:#93c5fd --color=info:#94a3b8,prompt:#60a5fa,pointer:#60a5fa --color=marker:#a78bfa,spinner:#a78bfa,header:#94a3b8'

# ftree — 文件树导航 (主命令)
ftree() {
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        /home/linhua/scripts/ftree.py --help
    elif [ "$1" = "--fzf" ] || [ "$1" = "-f" ]; then
        shift
        local target
        target=$(/home/linhua/scripts/ftree-fzf.sh --cd "${@:-.}") && cd "$target"
    elif [ "$1" = "--watch" ] || [ "$1" = "-w" ]; then
        shift
        /home/linhua/scripts/ftree.py --watch "${@:-.}"
    elif [ "$1" = "--popup" ] || [ "$1" = "-p" ]; then
        shift
        /home/linhua/scripts/ftree-popup.sh "${@:-.}"
    elif [ "$1" = "--json" ] || [ "$1" = "-j" ]; then
        shift
        /home/linhua/scripts/ftree.py --json "${@:-.}"
    elif [ "$1" = "--install" ]; then
        /home/linhua/scripts/ftree-fzf.sh --install
    else
        /home/linhua/scripts/ftree.py "${@:-.}"
    fi
}

# fcd — 快速目录跳转 (fzf + cd)
fcd() {
    local target
    target=$(/home/linhua/scripts/ftree-fzf.sh --cd "${1:-.}")
    if [ $? -eq 0 ] && [ -n "$target" ] && [ -d "$target" ]; then
        cd "$target"
        echo -e "\033[1;32m📂 → $target\033[0m"
        ls --color=auto
    fi
}

# ftree-popup — tmux 浮动窗口 (如果使用 tmux)
ftree-popup() {
    if [ -z "$TMUX" ]; then
        echo "⚠ 请在 tmux 会话中使用此功能"
        echo "   启动 tmux: tmux new-session -s main"
        return 1
    fi
    local dir="${1:-.}"
    tmux display-popup -h 80% -w 80% -E "ftree.py --watch '$dir'"
}

# Ctrl+F 快捷键绑定 (如果使用 fzf)
if [ -f /usr/share/doc/fzf/examples/key-bindings.bash ]; then
    source /usr/share/doc/fzf/examples/key-bindings.bash 2>/dev/null
fi

# ftree 命令补全
_ftree_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -d -- "$cur") )
}
complete -o default -o dirnames -F _ftree_complete ftree fcd

# <<< ftree <<<
EOF
    
    echo -e "${GREEN}✅ ftree 已安装到 .bashrc${NC}"
    echo -e "${CYAN}请执行: source ~/.bashrc${NC}"
    echo ""
    echo -e "可用命令:"
    echo -e "  ${GREEN}ftree${NC}         查看当前目录树"
    echo -e "  ${GREEN}ftree --fzf${NC}   快速目录跳转 (fzf)"
    echo -e "  ${GREEN}fcd${NC}           快速 cd 到目录"
    echo -e "  ${GREEN}ftree --watch${NC} 实时监听模式"
    echo -e "  ${GREEN}ftree --popup${NC} tmux 浮动窗口"
    echo -e "  ${GREEN}ftree --json${NC}  输出 JSON 结构"
}

# ── Main ──────────────────────────────────────────────────────────
case "${1:-}" in
    --help|-h)
        usage
        ;;
    --install)
        install_ftree
        ;;
    --cd)
        ftree_fzf "${2:-.}" "cd"
        ;;
    --version|-v)
        echo "ftree-fzf v${VERSION}"
        ;;
    *)
        ftree_fzf "${1:-.}" "goto"
        ;;
esac
