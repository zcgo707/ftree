<div align="center">

# 🌳 ftree

> **终端里的「文件资源管理器」** · 三种模式覆盖所有文件浏览场景

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](src/ftree-widget.py)
[![Platform: Linux/WSL](https://img.shields.io/badge/Platform-Linux%20%7C%20WSL-orange)](https://github.com/zcgo707/ftree)
[![fzf](https://img.shields.io/badge/powered%20by-fzf-ff69b4)](https://github.com/junegunn/fzf)
[![rich](https://img.shields.io/badge/powered%20by-rich-1abc9c)](https://github.com/Textualize/rich)

[✨ 特性](#-特性) •
[📦 项目组成](#-项目组成) •
[🔧 安装](#-安装) •
[🚀 使用指南](#-使用指南) •
[🏗️ 架构](#️-架构设计)

</div>

---

## ✨ 特性

| 模式 | 命令 | 一句话描述 |
|------|------|-----------|
| 🖥️ **桌面置顶小窗** | `ftree --widget` | 始终置顶的 GUI 文件树，双击确认后一键 `fcdw` cd |
| 🌲 **终端彩色树** | `ftree` | Rich 库渲染的彩色目录树，支持 `--watch` 实时监听 |
| ⚡ **FZF 快速跳转** | `fcd` | 模糊搜索目录名，预览内容，Enter 即 cd |
| 📟 **Tmux 浮动窗** | `ftree --popup` | tmux display-popup 浮动窗口，不离开终端 |

---

## 🖼️ 截图

> *（此处分隔符区域将放置实际截图）*

```
┌─────────────────────────────────────────┐
│  ftree  -  文件导航        [P][-][=][X] │  ← 无边框自定义窗口
├─────────────────────────────────────────┤
│  / > home > linhua > projects           │  ← 面包屑路径（可点击跳转）
├─────────────────────────────────────────┤
│ v [+]  projects                         │
│   v [+]  app                            │  ← 点击 >/v 展开折叠
│     > [+]  Cloudy                       │
│     > [+]  ai_disk_cleaner              │    双击进入目录
│     > [+]  mem_sys                      │
│   > [+]  ml                             │
│   > [+]  web                            │
│   [+]  INDEX.html                       │
│   [+]  PROJECT_MAP.md                   │
├─────────────────────────────────────────┤
│  /home/linhua/projects                  │
│  [ projects ]    [ 确认跳转 ]           │  ← 蓝底按钮确认
└─────────────────────────────────────────┘
```

---

## 📦 项目组成

### 1️⃣ `ftree-widget.py` — 桌面置顶小窗 ⭐

| 技术 | 用途 |
|------|------|
| `tkinter` + `overrideredirect(True)` | 无边框自定义 GUI 窗口 |
| `os.scandir()` | 按需扫描目录，单次 **0.1ms**，不卡 UI |
| 容器式 `pack()` 布局 | 每个目录用独立 Frame 包裹，展开折叠**不串位** |
| `bind_all` 全局事件 | 鼠标滚轮翻页、键盘 PageUp/Down/Home/End |
| 文件 IPC | 通过 `~/.ftree_cd_target` 与 Shell 通信 |

**操作方式**:

| 操作 | 效果 |
|------|------|
| 点击 **`>` / `v`** 或目录名 | 展开/折叠子目录 |
| **双击** 目录名 | 进入该目录（视图刷新到该目录） |
| 点击路径栏 **`home` / `projects`** | 跳转到对应母目录 |
| 滚轮 / `PgUp` / `PgDn` / `↑↓` | 滚动页面 |
| 点击 **[确认跳转]** | ✅ 写入目标路径 → 终端 `fcdw` 跳转 |
| **拖拽标题栏** | 移动窗口 |
| **双击标题栏** | 最大化/还原 |
| `[P]` `[-]` `[=]` `[X]` | 置顶 / 最小化 / 最大化 / 关闭 |

---

### 2️⃣ `ftree.py` — 终端目录树

| 技术 | 用途 |
|------|------|
| `rich.Tree` | 彩色树形输出，文件类型图标 |
| `rich.Live` | `--watch` 模式实时刷新 |
| `argparse` | CLI 参数解析 |

```bash
ftree                          # 当前目录
ftree ~/projects --depth 4     # 指定深度
ftree ~/projects --watch       # 实时监听
ftree ~/projects --json        # JSON 输出（可集成其他工具）
```

---

### 3️⃣ `ftree-fzf.sh` — FZF 导航器

| 技术 | 用途 |
|------|------|
| `fzf` | 模糊搜索，实时过滤 |
| `tree` | 右侧预览窗口 |
| Shell 函数 | 直接 `cd` + `ls` |

```bash
fcd ~/projects     # 模糊搜索 → Enter 即 cd + ls
```

---

### 4️⃣ `ftree-popup.sh` — Tmux 浮动窗

| 技术 | 用途 |
|------|------|
| `tmux display-popup` | 覆盖在终端之上的浮动窗口 |

```bash
ftree --popup ~/projects
```

---

## 🔧 安装

### 一键安装

```bash
git clone https://github.com/zcgo707/ftree.git
cd ftree
chmod +x setup.sh && ./setup.sh
source ~/.bashrc
```

### 手动安装

```bash
# 1. 复制脚本
mkdir -p ~/scripts ~/.local/bin
cp src/ftree* ~/scripts/
cp bin/* ~/.local/bin/
chmod +x ~/scripts/* ~/.local/bin/*

# 2. 安装系统依赖
sudo apt-get install -y fzf tree
pip install rich

# 3. 添加 bashrc 集成
cat config/bashrc-integration.sh >> ~/.bashrc
source ~/.bashrc
```

### 依赖清单

| 工具 | 用途 | 安装命令 |
|------|------|---------|
| `fzf` | 模糊搜索 | `apt-get install fzf` |
| `tree` | 目录树预览 | `apt-get install tree` |
| `Python 3` + `tkinter` | 桌面小窗 | WSLg 自带 |
| `rich` | 终端彩色树 | `pip install rich` |
| `tmux` 3.2+ | 浮动窗（可选） | `apt-get install tmux` |

---

## 🚀 使用指南

### 日常推荐工作流

```bash
# 终端 1: 启动桌面小窗
ftree --widget ~/projects

# 在 widget 中浏览 → 找到目标目录 → 点击「确认跳转」

# 终端 2: 一键跳转
fcdw    # → cd /home/linhua/projects/app/Cloudy
        # → ls 列出文件
```

### 快速目录跳转（不需要小窗）

```bash
fcd                  # 当前目录模糊搜索
fcd ~/projects       # 在 projects 中搜索
# 输入 "cloud" → 选中 Cloudy → Enter → cd + ls
```

### 终端目录树

```bash
ftree                     # 查看当前目录树
ftree --watch ~/projects  # 实时监听变化
ftree --depth 2 --no-files ~/projects  # 只看目录
```

---

## 🏗️ 架构设计

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────┐
│  ftree-widget │     │   ftree.py       │     │ ftree-fzf.sh│
│  (tkinter)    │     │   (rich)         │     │ (fzf+tree)  │
│               │     │                  │     │             │
│  桌面置顶小窗  │     │  终端彩色树      │     │ 模糊搜索跳转 │
└──────┬───────┘     └──────┬───────────┘     └──────┬──────┘
       │                    │                        │
       └────────────────────┼────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │  ftree (入口)  │
                    │  bin/ftree     │
                    │  统一分发命令   │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ fcdw (文件IPC) │
                    │ ~/.ftree_cd.. │
                    │  → cd 跳转    │
                    └───────────────┘
```

### 进程间通信

```
ftree-widget                     Shell (fcdw)
     │                              │
     │  点击「确认跳转」             │
     ├──→ 写入 path ──→ ~/.ftree_cd_target
     │                              │
     │                    fcdw 执行 │
     │                              ├──→ cat ~/.ftree_cd_target
     │                              ├──→ cd "$target"
     │                              └──→ ls
```

---

## 📂 项目结构

```
ftree/
├── README.md                       ← 本文档
├── LICENSE                         ← MIT 许可证
├── setup.sh                        ← 一键安装脚本
├── .gitignore
├── bin/                            ← 入口命令（须在 PATH 中）
│   ├── ftree                       ← 统一入口
│   ├── fcd                         ← fzf 快速跳转
│   └── fcdw                        ← 从 widget 跳转
├── src/                            ← 核心源代码
│   ├── ftree.py                    ← 终端彩色目录树
│   ├── ftree-widget.py             ← 桌面置顶小窗
│   ├── ftree-fzf.sh               ← fzf 搜索导航
│   └── ftree-popup.sh             ← tmux 浮动窗
└── config/
    └── bashrc-integration.sh       ← Shell 集成片段
```

---

## 📄 许可证

[MIT License](LICENSE) — 自由使用、修改、分发

---

## 👤 作者

**zcgo707** — [zen707@qq.com](mailto:zen707@qq.com)

> 💡 项目由 [Claude Code](https://claude.ai) 协助开发 · 持续优化中 🚀
>
> 如果你觉得有用，欢迎 ⭐ Star 或提出 Issue！
