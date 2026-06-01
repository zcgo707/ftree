#!/usr/bin/env python3
"""ftree-widget v4 — 全 ASCII 安全 · 容器式布局 · 无边框窗口"""

import os, sys
import tkinter as tk

CD_TARGET = os.path.expanduser("~/.ftree_cd_target")

SKIP = {
    'node_modules','.git','__pycache__','.cache','.npm','.nvm',
    '.conda','.local','venv','.venv','env','dist','build','.next',
    'pkgs','target','.vscode-server','snap','.claude','.codex',
    '.aws','.azure','.config','.dbus','.docker','.dotnet',
    '.landscape','.modelscope','.nv','.ssh','.triton','.vim',
    'miniconda3','.anaconda',
}

def ls(path):
    dirs, files = [], []
    try:
        for e in os.scandir(path):
            if e.name.startswith('.'): continue
            if e.is_dir(follow_symlinks=False):
                if e.name not in SKIP: dirs.append(e.name)
            else:
                try:
                    s = e.stat().st_size
                    sz = f"{s//1024}K" if s>1024 else f"{s}B"
                except: sz = ""
                files.append((e.name, sz))
    except: pass
    return sorted(dirs), sorted(files, key=lambda x: x[0].lower())


# 颜色
BG    = "#0f172a"
BG2   = "#1a1f2e"
HVR   = "#263548"
TXT   = "#e2e8f0"
DIM   = "#94a3b8"
DIRC  = "#4ade80"
FILEC = "#cbd5e1"
ACC   = "#60a5fa"
BTN   = "#2563eb"
BTN2  = "#059669"
WARN  = "#fbbf24"


class App(tk.Tk):
    def __init__(self, root_path):
        super().__init__()
        self.cur = os.path.abspath(root_path)

        # 无边框
        self.overrideredirect(True)
        self.configure(bg="#2d3a4d")
        self.geometry("960x860+250+50")
        self.minsize(500, 400)
        self.resizable(True, True)
        self.attributes('-topmost', True)
        self.protocol("WM_DELETE_WINDOW", self._quit)

        FN = "song ti"
        self.f24 = (FN, 24, "bold")   # 标题
        self.f20 = (FN, 20)           # 路径普通
        self.f22 = (FN, 22, "bold")   # 路径当前
        self.f18 = (FN, 18)           # 小字
        self.f26 = (FN, 26)           # 目录名
        self.f28 = (FN, 28, "bold")   # 目录加粗
        self.f22r= (FN, 22)           # 文件名
        self.f20b= (FN, 20, "bold")   # 按钮
        self.f14 = (FN, 14, "bold")   # 窗口按钮

        # 主容器
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(fill="both", expand=True, padx=2, pady=2)

        self._build()
        self._goto(self.cur)

        # 拖拽
        self._dx = self._dy = 0
        self.tbar.bind("<Button-1>", self._ds)
        self.tbar.bind("<B1-Motion>", self._dm)
        self.tbar.bind("<Double-Button-1>", lambda e: self._toggle_max())
        self._maxed = False
        self._geo = ""

    def _build(self):
        self._title()
        self._pathbar()
        self._tree()
        self._bottombar()

    def _title(self):
        tb = tk.Frame(self.main, bg=BG2, height=44)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        self.tbar = tb

        tk.Label(tb, text="  ftree  -  文件导航", font=self.f24,
                 bg=BG2, fg="#f1f5f9").pack(side="left", padx=10)

        bf = tk.Frame(tb, bg=BG2)
        bf.pack(side="right", padx=8)

        # 置顶 [P]
        self._pv = tk.BooleanVar(value=True)
        pin = tk.Checkbutton(bf, text="[P]", variable=self._pv,
            command=lambda: self.attributes('-topmost', self._pv.get()),
            bg=BG2, fg=ACC, selectcolor=BG2, activebackground=BG2,
            font=self.f14, cursor="hand2", bd=0)
        pin.pack(side="left", padx=2)

        # 最小化 [-]
        tk.Button(bf, text="[-]", font=self.f14,
            bg=BG2, fg=TXT, bd=0, padx=6,
            activebackground=HVR, cursor="hand2",
            command=self.iconify).pack(side="left", padx=2)

        # 最大化 [=]
        tk.Button(bf, text="[=]", font=self.f14,
            bg=BG2, fg=TXT, bd=0, padx=6,
            activebackground=HVR, cursor="hand2",
            command=self._toggle_max).pack(side="left", padx=2)

        # 关闭 [X]
        tk.Button(bf, text="[X]", font=self.f14,
            bg=BG2, fg="#ef4444", bd=0, padx=6,
            activebackground="#7f1d1d", cursor="hand2",
            command=self._quit).pack(side="left", padx=2)

    def _pathbar(self):
        self.pf = tk.Frame(self.main, bg=BG, height=46)
        self.pf.pack(fill="x")

    def _draw_path(self):
        for w in self.pf.winfo_children(): w.destroy()
        pf = tk.Frame(self.pf, bg=BG)
        pf.pack(fill="x", padx=14, pady=6)
        parts = self.cur.split(os.sep)

        self._seg(pf, " / ", "/", True)
        acc = ""
        for i, seg in enumerate(parts):
            if not seg:
                if i == 0: acc = "/"
                continue
            acc = os.path.join(acc, seg) if i > 0 else seg
            last = (i == len(parts)-1)
            tk.Label(pf, text=" > ", font=self.f18,
                     bg=BG, fg="#64748b").pack(side="left")
            if last:
                tk.Label(pf, text=seg, font=self.f22,
                         bg=BG, fg="#f1f5f9").pack(side="left")
            else:
                self._seg(pf, seg, acc, False)

    def _seg(self, pf, text, target, root=False):
        lb = tk.Label(pf, text=text, font=self.f20,
                      bg=BG, fg=DIM, cursor="hand2")
        lb.pack(side="left")
        lb.bind("<Button-1>", lambda e, t=target: self._goto(t))
        lb.bind("<Enter>", lambda e: lb.configure(fg=TXT, bg=HVR))
        lb.bind("<Leave>", lambda e: lb.configure(fg=DIM, bg=BG))

    def _tree(self):
        cf = tk.Frame(self.main, bg=BG)
        cf.pack(fill="both", expand=True, padx=4)

        self.cv = tk.Canvas(cf, bg=BG, highlightthickness=0)
        self.sb = tk.Scrollbar(cf, orient="vertical", command=self.cv.yview)
        self.tf = tk.Frame(self.cv, bg=BG)

        self.cv.bind("<Configure>", lambda e: (
            self.cv.itemconfig("tw", width=e.width),
            self.cv.configure(scrollregion=self.cv.bbox("all"))))
        self.tf.bind("<Configure>",
            lambda e: self.cv.configure(scrollregion=self.cv.bbox("all")))
        self.cv.create_window((0, 0), window=self.tf, anchor="nw", tags="tw")
        self.cv.configure(yscrollcommand=self.sb.set)
        self.cv.pack(side="left", fill="both", expand=True)
        self.sb.pack(side="right", fill="y")

        self.bind_all("<MouseWheel>",
            lambda e: self.cv.yview_scroll(int(-e.delta/20), "units"))
        self.bind_all("<Button-4>", lambda e: self.cv.yview_scroll(-3, "units"))
        self.bind_all("<Button-5>", lambda e: self.cv.yview_scroll(3, "units"))
        self.bind_all("<Prior>", lambda e: self.cv.yview_scroll(-1, "pages"))
        self.bind_all("<Next>",  lambda e: self.cv.yview_scroll(1, "pages"))

    def _bottombar(self):
        bb = tk.Frame(self.main, bg=BG2)
        bb.pack(fill="x")

        self.pl = tk.Label(bb, text="", font=self.f26,
                           bg=BG2, fg=ACC, anchor="w", padx=16)
        self.pl.pack(fill="x", pady=(8, 2))

        fb = tk.Frame(bb, bg=BG2)
        fb.pack(fill="x", padx=16, pady=(2, 10))

        self.dl = tk.Label(fb, text="", font=self.f28, bg=BG2, fg=WARN)
        self.dl.pack(side="left")

        self.btn = tk.Button(fb, text="    [ 确认跳转 ]    ",
            font=self.f20b, bg=BTN, fg="white", bd=0,
            padx=28, pady=10, cursor="hand2",
            activebackground="#1d4ed8", command=self._confirm)
        self.btn.pack(side="right")

    # ─── 核心：目录树 ──────────────────────────────────────
    def _goto(self, path):
        if not path or not os.path.isdir(path): return
        self.cur = os.path.abspath(path)
        self._draw_path()
        self.pl.configure(text=self.cur)
        dn = os.path.basename(self.cur) or self.cur
        self.dl.configure(text=f"    {dn}    ")
        for w in self.tf.winfo_children(): w.destroy()
        self._render(self.cur, self.tf, 0)

    def _render(self, path, parent, depth):
        """加载并渲染当前目录"""
        dirs, files = ls(path)
        for d in dirs:
            self._add_dir(d, os.path.join(path, d), parent, depth)
        for fn, sz in files:
            self._add_file(fn, sz, parent, depth)

    def _add_dir(self, name, full, parent, depth):
        """容器式目录节点"""
        box = tk.Frame(parent, bg=BG)
        box.pack(fill="x")

        # ── 当前行 ──
        row = tk.Frame(box, bg=BG, cursor="hand2")
        row.pack(fill="x")

        tk.Frame(row, bg=BG, width=depth*36).pack(side="left")

        arr = tk.Label(row, text=" >", font=self.f18,
                       bg=BG, fg="#888", width=2, cursor="hand2")
        arr.pack(side="left")

        tk.Label(row, text=" [+] ", font=self.f18,
                 bg=BG, fg="#22c55e").pack(side="left")

        lb = tk.Label(row, text=f"  {name}", font=self.f26 if depth>0 else self.f28,
                      bg=BG, fg=DIRC, anchor="w", cursor="hand2")
        lb.pack(side="left", fill="x", expand=True)

        # ── 子容器（紧跟在 row 下面，预创建但不显示） ──
        cf = tk.Frame(box, bg=BG)
        cf.pack(fill="x")         # pack 到 row 后面
        cf.pack_forget()          # 隐藏，但位置已确立

        opened = False
        loaded = False
        dbl_guard = False

        def toggle(e=None):
            nonlocal opened, loaded, dbl_guard
            if opened:
                # 折叠
                cf.pack_forget()
                arr.configure(text=" >")
                opened = False
            else:
                # 展开
                cf.pack(fill="x")
                arr.configure(text=" v")
                opened = True
                if not loaded:
                    self._render(full, cf, depth+1)
                    loaded = True
            self.cv.configure(scrollregion=self.cv.bbox("all"))

        def double_click(e):
            self._goto(full)

        # 大面积点击
        row.bind("<Button-1>", toggle)
        arr.bind("<Button-1>", toggle)
        lb.bind("<Button-1>", toggle)
        lb.bind("<Double-Button-1>", double_click)

        # hover
        for w in (row, arr, lb):
            w.bind("<Enter>", lambda e, r=row: r.configure(bg=HVR))
            w.bind("<Leave>", lambda e, r=row: r.configure(bg=BG))

        # 第一层自动展开
        if depth == 0:
            self.after(50, toggle)

    def _add_file(self, name, size, parent, depth):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x")
        tk.Frame(row, bg=BG, width=depth*36+32).pack(side="left")

        ext = os.path.splitext(name)[1].lower()
        icons = {'.py':'py','.js':'js','.ts':'ts','.md':'md','.json':'{}',
                 '.html':'<>','.css':'#','.sh':'sh','.yaml':'ym','.yml':'ym',
                 '.toml':'tm','.jpg':'im','.png':'im','.svg':'im','.txt':'tx'}
        tag = icons.get(ext, "  ")
        sz = f" [{size}]" if size else ""

        tk.Label(row, text=f" {tag}  {name}{sz}", font=self.f22r,
                 bg=BG, fg=FILEC, anchor="w").pack(side="left", fill="x", expand=True)

    # ─── 操作 ──────────────────────────────────────────────
    def _confirm(self):
        try:
            with open(CD_TARGET, 'w') as f:
                f.write(self.cur + '\n')
            self.pl.configure(text=f"OK  {self.cur}")
            self.btn.configure(text="    [ 已确认 ]    ", bg=BTN2)
            self.after(2500, lambda: self.btn.configure(
                text="    [ 确认跳转 ]    ", bg=BTN))
        except Exception as e:
            self.pl.configure(text=f"ERR  {e}")

    def _toggle_max(self):
        if self._maxed:
            self.geometry(self._geo)
            self._maxed = False
        else:
            self._geo = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"{sw}x{sh}+0+0")
            self._maxed = True

    def _quit(self):
        try: self.destroy()
        except: pass
        os._exit(0)

    def _ds(self, e):
        self._dx = e.x; self._dy = e.y
    def _dm(self, e):
        self.geometry(f"+{self.winfo_x()+e.x-self._dx}+{self.winfo_y()+e.y-self._dy}")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--cd':
        try:
            with open(CD_TARGET) as f:
                p = f.read().strip()
                if p and os.path.isdir(p): print(p); sys.exit(0)
        except: pass
        print(os.getcwd()); sys.exit(0)

    root = '.'
    for a in sys.argv[1:]:
        if a in ('--help','-h'): print(__doc__); sys.exit(0)
        elif not a.startswith('-'): root = a

    root = os.path.abspath(root)
    if not os.path.isdir(root): print(f"目录不存在: {root}"); sys.exit(1)
    print(f"  ftree-widget v4  -  {root}")
    print(f"  窗口按钮:  [P]置顶  [-]最小化  [=]最大化  [X]关闭\n")
    App(root).mainloop()
