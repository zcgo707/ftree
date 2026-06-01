# >>> ftree >>> — 文件树导航集成 (by setup.sh)

# FZF 主题 (深色)
export FZF_DEFAULT_OPTS='--color=fg:#e2e8f0,bg:#0f172a,hl:#60a5fa --color=fg+:#f1f5f9,bg+:#1e293b,hl+:#93c5fd --color=info:#94a3b8,prompt:#60a5fa,pointer:#60a5fa --color=marker:#a78bfa,spinner:#a78bfa,header:#94a3b8'

# fzf 快捷键 (Ctrl+R 历史, Ctrl+T 文件)
if [ -f /usr/share/doc/fzf/examples/key-bindings.bash ]; then
    source /usr/share/doc/fzf/examples/key-bindings.bash 2>/dev/null
fi

# 命令补全
_ftree_complete() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=( $(compgen -d -- "$cur") )
}
complete -o default -o dirnames -F _ftree_complete ftree fcd fcdw
# <<< ftree <<<
