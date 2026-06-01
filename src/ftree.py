#!/usr/bin/env python3
"""
ftree.py — 终端文件树查看器
用法: ftree.py [目录] [选项]

选项:
  --watch/-w   实时监听模式
  --json/-j    输出 JSON
  --depth N    展开深度 (默认 5)
  --no-files   只显示目录
  --no-dot     隐藏 . 开头的目录
"""

import os, sys, time, json
from pathlib import Path
from datetime import datetime

try:
    from rich.tree import Tree as RichTree
    from rich.console import Console
    from rich.live import Live
    from rich.panel import Panel
    from rich import box
except ImportError:
    print("❌ 需要 rich 库: pip install rich")
    sys.exit(1)

VERSION = "2.0.0"

IGNORE = {
    'node_modules', '.git', '__pycache__', '.cache', '.npm', '.nvm',
    '.conda', '.local', 'venv', 'env', '.venv', 'dist', 'build',
    'pkgs', '.vscode-server', 'snap', '.claude', '.codex',
    '.anaconda', '.aws', '.azure', '.config', '.dbus',
    '.docker', '.dotnet', '.landscape', '.modelscope',
    '.nv', '.ssh', '.triton', '.vim', '.npm/_cacache',
}

MAX_DEPTH = 5
HIDE_DOT = True
SHOW_FILES = True


def get_tree(root, depth=MAX_DEPTH, show_files=SHOW_FILES, hide_dot=HIDE_DOT):
    t = RichTree(f"📂 [bold cyan]{os.path.basename(root) or root}[/] [dim]{root}[/]",
                 guide_style="bright_black")

    def _add(d, pt, cd):
        if cd > depth:
            return
        try:
            ents = sorted(os.listdir(d))
        except:
            pt.add("🚫 [dim]无权限[/]")
            return
        dirs, files = [], []
        for e in ents:
            fp = os.path.join(d, e)
            if hide_dot and e.startswith('.'):
                continue
            if os.path.isdir(fp):
                rel = os.path.relpath(fp, root)
                if any(ig in rel for ig in IGNORE):
                    continue
                dirs.append(e)
            elif show_files:
                files.append(e)
        for dd in dirs:
            fd = os.path.join(d, dd)
            subs = []
            try:
                subs = [x for x in os.listdir(fd)
                        if os.path.isdir(os.path.join(fd, x)) and not x.startswith('.')]
            except:
                pass
            if subs and cd < depth:
                b = pt.add(f"📁 [green]{dd}[/]")
                _add(fd, b, cd + 1)
            else:
                pt.add(f"📁 [green]{dd}[/]")
        for f in files:
            ff = os.path.join(d, f)
            ext = os.path.splitext(f)[1].lower()
            icons = {'.py':'🐍','.js':'📜','.ts':'📘','.tsx':'⚛️','.md':'📝',
                     '.json':'📋','.html':'🌐','.css':'🎨','.sh':'📜',
                     '.yaml':'⚙️','.yml':'⚙️','.toml':'⚙️'}
            icon = icons.get(ext, '📄')
            sz = ""
            try:
                s = os.path.getsize(ff)
                sz = f"[dim]({s//1024}KB)[/]" if s>1024 else f"[dim]({s}B)[/]"
            except:
                pass
            pt.add(f"{icon} [white]{f}[/] {sz}" if sz else f"{icon} [white]{f}[/]")

    _add(root, t, 0)
    return t


def get_stats(root):
    d, f, s = 0, 0, 0
    try:
        for r, ds, fs in os.walk(root):
            ds[:] = [x for x in ds if x not in IGNORE and not (x.startswith('.') and HIDE_DOT)]
            d += len(ds)
            f += len(fs)
            for fn in fs:
                try:
                    s += os.path.getsize(os.path.join(r, fn))
                except: pass
    except: pass
    sz = f"{s/1024**3:.1f}GB" if s>1024**3 else f"{s/1024**2:.1f}MB" if s>1024**2 else f"{s/1024:.1f}KB" if s>1024 else f"{s}B"
    return d, f, sz


def run_tui(root, watch=False):
    c = Console()
    root = os.path.abspath(root)
    try:
        with Live(auto_refresh=False, screen=True) as live:
            while True:
                d, f, sz = get_stats(root)
                h = Panel(f"[bold cyan]🌳 ftree[/] [dim]v{VERSION}[/] — [white]{root}[/]\n"
                          f"[dim]📂 {d} 目录 · 📄 {f} 文件 · 💾 {sz}[/]",
                          box=box.ROUNDED, border_style="cyan", padding=(1, 2))
                t = get_tree(root)
                disp = RichTree("")
                disp.add(h)
                disp.add(t)
                live.update(disp, refresh=True)
                if not watch:
                    break
                time.sleep(2)
    except KeyboardInterrupt:
        pass


def json_dump(root, depth=4):
    result = {"name": os.path.basename(root) or root, "path": os.path.abspath(root),
              "type": "dir", "children": []}
    def _sc(d, node, cd=0):
        if cd > depth:
            return
        try:
            ents = sorted(os.listdir(d))
        except:
            return
        for e in ents:
            if HIDE_DOT and e.startswith('.'):
                continue
            fp = os.path.join(d, e)
            c = {"name": e, "path": fp, "type": "file"}
            if os.path.isdir(fp):
                rel = os.path.relpath(fp, root)
                if any(ig in rel for ig in IGNORE):
                    continue
                c["type"] = "dir"
                c["children"] = []
                _sc(fp, c, cd + 1)
                node["children"].append(c)
            else:
                try:
                    c["size"] = os.path.getsize(fp)
                except:
                    pass
                node["children"].append(c)
    _sc(root, result)
    return result


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='🌳 ftree — 终端文件树')
    p.add_argument('dir', nargs='?', default='.', help='目录')
    p.add_argument('--watch', '-w', action='store_true', help='实时监听')
    p.add_argument('--json', '-j', action='store_true', help='JSON 输出')
    p.add_argument('--depth', type=int, default=5, help='展开深度')
    p.add_argument('--no-files', action='store_true', help='只显示目录')
    p.add_argument('--no-dot', action='store_true', help='隐藏 . 目录')
    p.add_argument('--version', '-v', action='version', version=f'ftree v{VERSION}')
    a = p.parse_args()

    MAX_DEPTH = a.depth
    if a.no_dot:
        HIDE_DOT = True
    if a.no_files:
        SHOW_FILES = False

    root = os.path.abspath(a.dir)
    if not os.path.isdir(root):
        print(f"❌ 目录不存在: {root}")
        sys.exit(1)

    if a.json:
        print(json.dumps(json_dump(root, a.depth), indent=2, ensure_ascii=False))
    else:
        run_tui(root, a.watch)
