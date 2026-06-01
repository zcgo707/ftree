# 🌳 ftree — 文件树导航器

> 终端里的「文件资源管理器」· 三大模式覆盖所有场景

`ftree` 是一套文件树导航工具集，包含**终端目录树**、**桌面置顶小窗**、**fzf 快速跳转**三种使用模式，帮你告别 `cd` + `ls` 的反复操作。

---

## 🖼️ 效果一览

| 模式 | 截图示意 | 核心场景 |
|------|---------|---------|
| **桌面小窗** `ftree --widget` | 始终置顶的深色窗口 | 边编码边浏览文件结构，点击确认后 `fcdw` 一键跳转 |
| **终端树** `ftree` | Rich 库彩色树形输出 | 快速查看目录结构，实时监听文件变更 |
| **FZF 导航** `fcd` | 模糊搜索 + 树预览 | 不记路径，搜关键词直接 cd |

---

## 📦 项目组成

### 1. `ftree-widget.py` — 桌面置顶小窗【核心】

**文件**: `src/ftree-widget.py`

**技术实现**:
| 技术 | 用途 |
|------|------|
| `tkinter` + 无边框窗口 | GUI 框架，`overrideredirect(True)` 自定义标题栏 |
| `os.scandir()` | 按需扫描目录，单次 0.1ms，不卡 UI |
| 容器式 `pack()` 布局 | 每个目录节点用独立 Frame 包裹，展开折叠不串位 |
| `bind_all` 全局事件 | 鼠标滚轮翻页、键盘 PageUp/Down |
| 文件 IPC (`~/.ftree_cd_target`) | Shell 与 GUI 进程通信，`fcdw` 读取后 cd |

**特性**:
- 无边框深色窗口，完全可拖拽，双击标题栏最大化
- 点击 `>` 展开目录，点击 `v` 折叠，**双击**进入目录
- 面包屑路径栏**点击任意母目录**即可跳转
- 底部「确认跳转」按钮 → 写入目标路径 → 终端 `fcdw` 即跳转

### 2. `ftree.py` — 终端目录树查看器

**文件**: `src/ftree.py`

**技术实现**: Python `rich` 库，`Tree` + `Live` 组件实现实时刷新

**特性**:
- 彩色树形输出，文件类型图标识别
- `--watch` 实时监听模式（2 秒自动刷新）
- `--json` JSON 结构输出（可集成其他工具）
- `--depth` 控制展开深度

### 3. `ftree-fzf.sh` — FZF 导航器

**文件**: `src/ftree-fzf.sh`

**技术实现**: `fzf` + `tree` 预览窗口，快速模糊搜索目录

**特性**:
- 模糊搜索目录名，实时过滤
- 右侧预览窗口显示目录内容
- Enter 一键 cd + ls

### 4. `ftree-popup.sh` — Tmux 浮动窗

**文件**: `src/ftree-popup.sh`

**技术实现**: `tmux display-popup` 创建一个覆盖在终端之上的浮动窗口

---

## 🔧 安装

### 一键安装

```bash
git clone https://github.com/zcgo707/ftree.git
cd ftree
chmod +x setup.sh && ./setup.sh
```

### 手动安装

```bash
# 1. 复制脚本
mkdir -p ~/.local/bin
cp src/ftree* ~/scripts/ 2>/dev/null || mkdir -p ~/scripts && cp src/* ~/scripts/
cp bin/* ~/.local/bin/

# 2. 安装依赖
sudo apt-get install -y fzf tree          # 基础工具
pip install rich                           # 终端树 (ftree.py)

# 3. 添加 bashrc 集成
cat config/bashrc-integration.sh >> ~/.bashrc
source ~/.bashrc
```

### 依赖

| 工具 | 用途 | 安装方式 |
|------|------|---------|
| `fzf` | 模糊搜索导航 | `apt-get install fzf` |
| `tree` | 目录树生成 | `apt-get install tree` |
| `Python 3` + `tkinter` | 桌面小窗 | WSLg 自带 |
| `rich` (Python) | 终端彩色树 | `pip install rich` |
| `tmux` (可选) | 浮动窗口 | `apt-get install tmux` |

---

## 🚀 使用指南

### 桌面小窗（推荐——日常使用）

```bash
# 启动
ftree --widget ~/projects

# 在终端跳转
fcdw    # → 跳转到 widget 中确认的目录
```

**操作方式**:

| 操作 | 效果 |
|------|------|
| 点击 `>` / `v` 或目录名 | 展开/折叠 |
| **双击** 目录名 | 进入该目录（刷新视图） |
| 点击路径栏 `home` / `projects` | 跳到对应位置 |
| 滚轮 / PageUp / PageDown | 滚动页面 |
| 点击 `[ 确认跳转 ]` | 写入目标，供 `fcdw` 使用 |
| 拖拽标题栏 | 移动窗口 |
| 双击标题栏 | 最大化/还原 |
| `[P]` 按钮 | 切换置顶 |
| `[-]` `[=]` `[X]` | 最小化 / 最大化 / 关闭 |

### 快速跳转

```bash
fcd ~/projects    # fzf 搜索 → Enter 即 cd
```

### 终端查看

```bash
ftree              # 当前目录
ftree ~/projects --depth 4    # 指定深度
ftree ~/projects --watch      # 实时监听
ftree ~/projects --json       # JSON 输出
```

### Tmux 浮动窗

```bash
ftree --popup ~/projects
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

`ftree-widget` 和 `fcdw` 之间通过文件通信：

```
ftree-widget                     Shell (fcdw)
     │                              │
     │  click [确认跳转]             │
     ├──→ write path ──→ ~/.ftree_cd_target
     │                              │
     │                              ├──→ cat ~/.ftree_cd_target
     │                              ├──→ cd "$target"
     │                              └──→ ls
```

---

## 📄 许可证

MIT License — 自由使用、修改、分发

---

## 👤 作者

zcgo707 (zen707@qq.com)

> 项目由 Claude Code 协助开发，持续优化中 🚀
