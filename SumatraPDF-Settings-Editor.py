#!/usr/bin/env python3
"""
SumatraPDF 高级设置编辑器
=========================
一个用于可视化编辑 SumatraPDF 高级设置文件 (SumatraPDF-settings.txt) 的 GUI 工具。

需要: Python 3.8+ (tkinter 已包含在标准 Python 发行版中)

用法:
    python SumatraPDF-Settings-Editor.py [设置文件路径]
"""

import os
import sys
import re
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from typing import Any, Optional

# 高 DPI 支持
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ──────────────────────────────────────────────────────────────────────
# 颜色常量 - 现代化配色
# ──────────────────────────────────────────────────────────────────────
class Colors:
    BG = "#f8f9fa"              # 主背景
    SIDEBAR_BG = "#ffffff"      # 侧边栏背景
    CARD_BG = "#ffffff"         # 卡片背景
    BORDER = "#e2e8f0"          # 边框
    TEXT = "#1a202c"            # 主文字
    TEXT_SECONDARY = "#4a5568"  # 次要文字
    TEXT_MUTED = "#a0aec0"      # 弱化文字
    ACCENT = "#4f6bed"          # 强调色
    ACCENT_LIGHT = "#eef2ff"    # 强调色浅
    HOVER = "#f1f5f9"           # 悬停
    SELECTED_BG = "#4f6bed"     # 选中背景
    SELECTED_FG = "#ffffff"     # 选中文字
    SEPARATOR = "#edf2f7"       # 分隔线
    INPUT_BG = "#ffffff"        # 输入框背景
    INPUT_BORDER = "#cbd5e0"    # 输入框边框
    INPUT_FOCUS = "#4f6bed"     # 输入框聚焦边框

# ──────────────────────────────────────────────────────────────────────
# 字体常量
# ──────────────────────────────────────────────────────────────────────
class Fonts:
    # 优先使用微软雅黑，回退到 Segoe UI
    FAMILY = "Microsoft YaHei UI"
    FAMILY_MONO = "Consolas"

    TITLE = (FAMILY, 18, "bold")
    SUBTITLE = (FAMILY, 14, "bold")
    BODY = (FAMILY, 11)
    BODY_BOLD = (FAMILY, 11, "bold")
    SMALL = (FAMILY, 10)
    SMALL_MUTED = (FAMILY, 10)
    SIDEBAR = (FAMILY, 11)
    SIDEBAR_TITLE = (FAMILY, 13, "bold")
    KEY = (FAMILY_MONO, 10)
    INPUT = (FAMILY, 11)
    BUTTON = (FAMILY, 10)
    STATUS = (FAMILY, 10)

# ──────────────────────────────────────────────────────────────────────
# 设置元数据
# ──────────────────────────────────────────────────────────────────────

# 基于 SumatraPDF 3.6 官方设置文档
# https://www.sumatrapdfreader.org/settings/settings3-6

CATEGORIES = [
    "常规",
    "页面显示",
    "工具栏与侧边栏",
    "主题与外观",
    "PDF / XPS / DjVu 页面",
    "电子书",
    "漫画与图片",
    "CHM 帮助文件",
    "PDF 批注",
    "LaTeX 正向搜索",
    "打印",
    "快捷键",
    "外部查看器",
    "选中文字处理",
    "高级选项",
]

# 每条: (配置键, 类型, 默认值, 中文说明, 分类, 选项)
# 类型: "bool", "int", "float", "str", "color", "choice", "compact"

SETTINGS_META = [
    # ══════════════════════════════════════════════
    # 常规
    # ══════════════════════════════════════════════
    ("CheckForUpdates", "bool", True,
     "每天自动检查更新", "常规", None),
    ("UseTabs", "bool", True,
     "用标签页打开文档，而不是每个文件开一个新窗口", "常规", None),
    ("RememberOpenedFiles", "bool", True,
     "记住打开过的文件和它们的显示状态", "常规", None),
    ("RememberStatePerDocument", "bool", True,
     "为每个文件单独记住缩放、页面布局等设置", "常规", None),
    ("RestoreSession", "bool", True,
     "下次启动时自动恢复上次打开的文件和标签页", "常规", None),
    ("ReuseInstance", "bool", True,
     "打开新文件时复用已有的 SumatraPDF 窗口", "常规", None),
    ("NoHomeTab", "bool", False,
     "不显示主页标签页", "常规", None),
    ("HomePageSortByFrequentlyRead", "bool", False,
     "主页按打开频率排序（3.6 之前的老方式），否则按最近打开排序", "常规", None),
    ("LazyLoading", "bool", False,
     "恢复会话时，延迟加载标签页直到用户切换过去", "常规", None),
    ("UiLanguage", "str", "",
     "界面语言代码，如 cn（简体中文）、en（英文）、de（德文）", "常规", None),

    # ══════════════════════════════════════════════
    # 页面显示
    # ══════════════════════════════════════════════
    ("DefaultDisplayMode", "choice", "automatic",
     "默认页面布局方式", "页面显示",
     ["automatic", "single page", "facing", "book view",
      "continuous", "continuous facing", "continuous book view"]),
    ("DefaultZoom", "str", "fit page",
     "默认缩放比例，可用值：fit page、fit width、fit content 或百分比如 100%",
     "页面显示", None),
    ("ZoomIncrement", "float", 0,
     "每次缩放的步长百分比，设为 0 则使用 ZoomLevels 中的值", "页面显示", None),
    ("ZoomLevels", "str", "",
     "自定义缩放级别序列（空格分隔），每个值在 8.33 到 6400 之间", "页面显示", None),
    ("SmoothScroll", "bool", False,
     "平滑滚动", "页面显示", None),
    ("FastScrollOverScrollbar", "bool", False,
     "鼠标悬停在滚动条上时，滚轮滚动更快", "页面显示", None),
    ("ScrollbarInSinglePage", "bool", False,
     "单页模式下也显示滚动条", "页面显示", None),
    ("DisableAntiAlias", "bool", False,
     "关闭 PDF 渲染的抗锯齿（文字边缘会变锐利但可能有锯齿）", "页面显示", None),

    # ══════════════════════════════════════════════
    # 工具栏与侧边栏
    # ══════════════════════════════════════════════
    ("ShowToolbar", "bool", True,
     "显示顶部工具栏", "工具栏与侧边栏", None),
    ("ToolbarSize", "int", 18,
     "工具栏图标大小（像素）", "工具栏与侧边栏", None),
    ("ShowMenubar", "bool", True,
     "显示菜单栏（仅在 UseTabs=false 时生效，按 F9 临时显示）", "工具栏与侧边栏", None),
    ("ShowFavorites", "bool", False,
     "显示收藏夹侧边栏", "工具栏与侧边栏", None),
    ("ShowToc", "bool", True,
     "文档有目录时自动显示目录侧边栏", "工具栏与侧边栏", None),
    ("ShowStartPage", "bool", True,
     "没有打开文件时显示常用文档列表", "工具栏与侧边栏", None),
    ("ShowLinks", "bool", False,
     "在文档中的链接周围画蓝色边框", "工具栏与侧边栏", None),
    ("SidebarDx", "int", 0,
     "收藏夹/目录侧边栏的宽度（像素），0 表示默认", "工具栏与侧边栏", None),
    ("TocDy", "int", 0,
     "当收藏夹和目录同时显示时，目录部分的高度", "工具栏与侧边栏", None),
    ("TabWidth", "int", 300,
     "单个标签页的最大宽度（像素）", "工具栏与侧边栏", None),
    ("TreeFontName", "str", "automatic",
     "目录树和收藏夹树的字体，automatic 表示用系统默认", "工具栏与侧边栏", None),
    ("TreeFontSize", "int", 0,
     "目录树和收藏夹树的字体大小，0 表示用系统默认", "工具栏与侧边栏", None),
    ("UIFontSize", "int", 0,
     "覆盖整个程序的字体大小，0 表示用系统默认", "工具栏与侧边栏", None),

    # ══════════════════════════════════════════════
    # 主题与外观
    # ══════════════════════════════════════════════
    ("Theme", "choice", "",
     "颜色主题", "主题与外观", ["", "light", "dark", "darker"]),
    ("MainWindowBackground", "color", "#80fff200",
     "非文档区域的背景色（默认是半透明黄色）", "主题与外观", None),
    ("UseSysColors", "bool", False,
     "使用 Windows 系统配色，会覆盖上面的颜色设置", "主题与外观", None),

    # ══════════════════════════════════════════════
    # PDF / XPS / DjVu 页面
    # ══════════════════════════════════════════════
    ("FixedPageUI.TextColor", "color", "#000000",
     "文字颜色（替换文档中的黑色）", "PDF / XPS / DjVu 页面", None),
    ("FixedPageUI.BackgroundColor", "color", "#ffffff",
     "背景颜色（替换文档中的白色）", "PDF / XPS / DjVu 页面", None),
    ("FixedPageUI.SelectionColor", "color", "#f5fc0c",
     "选中文字和搜索高亮的颜色，用 #aarrggbb 格式可控制透明度", "PDF / XPS / DjVu 页面", None),
    ("FixedPageUI.WindowMargin", "compact", "2 4 2 4",
     "文档与窗口之间的边距（上 右 下 左）", "PDF / XPS / DjVu 页面", None),
    ("FixedPageUI.PageSpacing", "compact", "4 4",
     "双页模式下两页之间的间距（水平 垂直）", "PDF / XPS / DjVu 页面", None),
    ("FixedPageUI.GradientColors", "str", "",
     "从上到下的渐变背景色（最多 3 个颜色，空格分隔），用于感知阅读进度",
     "PDF / XPS / DjVu 页面", None),
    ("FixedPageUI.InvertColors", "bool", False,
     "反转文字和背景颜色", "PDF / XPS / DjVu 页面", None),
    ("FixedPageUI.HideScrollbars", "bool", False,
     "隐藏滚动条（仍可用鼠标滚轮或键盘滚动）", "PDF / XPS / DjVu 页面", None),

    # ══════════════════════════════════════════════
    # 电子书
    # ══════════════════════════════════════════════
    ("EBookUI.FontSize", "float", 0,
     "电子书字体大小，0 表示默认值 8.0", "电子书", None),
    ("EBookUI.LayoutDx", "float", 0,
     "电子书页面宽度，0 表示默认值 420", "电子书", None),
    ("EBookUI.LayoutDy", "float", 0,
     "电子书页面高度，0 表示默认值 595", "电子书", None),
    ("EBookUI.IgnoreDocumentCSS", "bool", False,
     "忽略电子书自带的 CSS 样式", "电子书", None),
    ("EBookUI.CustomCSS", "str", "",
     "自定义 CSS（可能需要同时开启 IgnoreDocumentCSS）", "电子书", None),

    # ══════════════════════════════════════════════
    # 漫画与图片
    # ══════════════════════════════════════════════
    ("ComicBookUI.WindowMargin", "compact", "0 0 0 0",
     "文档与窗口之间的边距（上 右 下 左）", "漫画与图片", None),
    ("ComicBookUI.PageSpacing", "compact", "4 4",
     "双页模式下两页之间的间距（水平 垂直）", "漫画与图片", None),
    ("ComicBookUI.CbxMangaMode", "bool", False,
     "默认从右到左翻页（漫画模式）", "漫画与图片", None),

    # ══════════════════════════════════════════════
    # CHM 帮助文件
    # ══════════════════════════════════════════════
    ("ChmUI.UseFixedPageUI", "bool", False,
     "对 CHM 文件使用 PDF 的渲染方式", "CHM 帮助文件", None),

    # ══════════════════════════════════════════════
    # PDF 批注
    # ══════════════════════════════════════════════
    ("Annotations.HighlightColor", "color", "#ffff00",
     "高亮批注的颜色", "PDF 批注", None),
    ("Annotations.UnderlineColor", "color", "#00ff00",
     "下划线批注的颜色", "PDF 批注", None),
    ("Annotations.SquigglyColor", "color", "#ff00ff",
     "波浪线批注的颜色", "PDF 批注", None),
    ("Annotations.StrikeOutColor", "color", "#ff0000",
     "删除线批注的颜色", "PDF 批注", None),
    ("Annotations.FreeTextColor", "color", "",
     "文本批注的文字颜色", "PDF 批注", None),
    ("Annotations.FreeTextBackgroundColor", "color", "",
     "文本批注的背景颜色", "PDF 批注", None),
    ("Annotations.FreeTextOpacity", "int", 100,
     "文本批注的不透明度（0 = 完全透明，100 = 完全不透明）", "PDF 批注", None),
    ("Annotations.FreeTextSize", "int", 12,
     "文本批注的字号", "PDF 批注", None),
    ("Annotations.FreeTextBorderWidth", "int", 1,
     "文本批注的边框宽度", "PDF 批注", None),
    ("Annotations.TextIconColor", "color", "",
     "便签图标的颜色", "PDF 批注", None),
    ("Annotations.TextIconType", "choice", "",
     "便签图标样式", "PDF 批注",
     ["", "comment", "help", "insert", "key", "new paragraph", "note", "paragraph"]),
    ("Annotations.DefaultAuthor", "str", "",
     "批注的默认作者名，留空用 Windows 用户名，填 (none) 则不添加作者",
     "PDF 批注", None),

    # ══════════════════════════════════════════════
    # LaTeX 正向搜索
    # ══════════════════════════════════════════════
    ("ForwardSearch.HighlightOffset", "int", 0,
     "设为正数时，高亮样式变为页面左侧的矩形条（值为距页边的偏移）",
     "LaTeX 正向搜索", None),
    ("ForwardSearch.HighlightWidth", "int", 15,
     "左侧矩形高亮条的宽度（需 HighlightOffset > 0）", "LaTeX 正向搜索", None),
    ("ForwardSearch.HighlightColor", "color", "#6581ff",
     "正向搜索高亮的颜色", "LaTeX 正向搜索", None),
    ("ForwardSearch.HighlightPermanent", "bool", False,
     "高亮一直显示直到点击鼠标（否则会自动消失）", "LaTeX 正向搜索", None),

    # ══════════════════════════════════════════════
    # 打印
    # ══════════════════════════════════════════════
    ("PrinterDefaults.PrintScale", "choice", "shrink",
     "打印时的默认缩放方式", "打印", ["shrink", "fit", "none"]),

    # ══════════════════════════════════════════════
    # 快捷键
    # ══════════════════════════════════════════════
    # Shortcuts 是数组类型，这里只展示结构说明
    # 格式: Shortcuts [ [ Cmd = CmdXxx  Key = Ctrl-X  Name = 显示名  ToolbarText = 工具栏文字 ] ]

    # ══════════════════════════════════════════════
    # 外部查看器
    # ══════════════════════════════════════════════
    # ExternalViewers 是数组类型
    # 格式: ExternalViewers [ [ CommandLine = ...  Name = ...  Filter = ...  Key = ... ] ]

    # ══════════════════════════════════════════════
    # 选中文字处理
    # ══════════════════════════════════════════════
    # SelectionHandlers 是数组类型
    # 格式: SelectionHandlers [ [ URL = ...  Name = ...  Key = ... ] ]

    # ══════════════════════════════════════════════
    # 高级选项
    # ══════════════════════════════════════════════
    ("CustomScreenDPI", "int", 0,
     "手动指定屏幕 DPI，0 表示自动检测", "高级选项", None),
    ("EnableTeXEnhancements", "bool", False,
     "在设置菜单中显示 LaTeX 反向搜索的配置选项", "高级选项", None),
    ("InverseSearchCmdLine", "str", "",
     "LaTeX 反向搜索的命令行（点击 PDF 跳转到编辑器）", "高级选项", None),
    ("ReloadModifiedDocuments", "bool", True,
     "文件被修改后自动重新加载（电子书格式暂不支持）", "高级选项", None),
    ("EscToExit", "bool", False,
     "按 Esc 键关闭程序", "高级选项", None),
    ("FullPathInTitle", "bool", False,
     "标题栏显示文件的完整路径", "高级选项", None),
    ("DefaultPasswords", "str", "",
     "打开加密文档时自动尝试的密码（空格分隔，含空格的密码用引号括起）",
     "高级选项", None),
    ("VersionToSkip", "str", "",
     "跳过该版本的更新提示", "高级选项", None),
    ("WindowState", "int", 1,
     "窗口默认状态：1=普通，2=最大化，3=全屏，4=最小化", "高级选项", None),
]

SETTINGS_LOOKUP = {s[0]: s for s in SETTINGS_META}


# ──────────────────────────────────────────────────────────────────────
# 设置文件解析器
# ──────────────────────────────────────────────────────────────────────

class SettingsFile:
    def __init__(self):
        self.path: Optional[str] = None
        self.settings: dict[str, str] = {}
        self.structs: dict[str, dict[str, str]] = {}
        self._parse_tree: list = []

    def find_settings_file(self) -> Optional[str]:
        candidates = []
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            p = os.path.join(local_app_data, "SumatraPDF", "SumatraPDF-settings.txt")
            if os.path.isfile(p):
                candidates.append(p)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for d in [script_dir, os.path.dirname(script_dir)]:
            p = os.path.join(d, "SumatraPDF-settings.txt")
            if os.path.isfile(p):
                candidates.append(p)
        return candidates[0] if candidates else None

    def load(self, path: str):
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.settings.clear()
        self.structs.clear()
        self._parse_tree = self._parse_lines(lines)

    def _parse_lines(self, lines: list[str]) -> list:
        result = []
        i = 0
        while i < len(lines):
            line = lines[i].rstrip("\r\n")
            stripped = line.strip()
            if not stripped or stripped.startswith(";"):
                result.append(("comment", stripped))
                i += 1
                continue
            struct_match = re.match(r'^(\w+)\s*\[', stripped)
            if struct_match and not stripped.startswith("["):
                name = struct_match.group(1)
                i += 1
                items = []
                depth = 1
                while i < len(lines) and depth > 0:
                    sl = lines[i].rstrip("\r\n").strip()
                    if sl == "]":
                        depth -= 1
                        if depth == 0:
                            i += 1
                            break
                    elif sl == "[" or sl.startswith("["):
                        depth += 1
                        i += 1
                        continue
                    if not sl or sl.startswith(";"):
                        i += 1
                        continue
                    kv = re.match(r'^(\w+)\s*=\s*(.*)', sl)
                    if kv:
                        key, val = kv.group(1), kv.group(2).strip()
                        self._set_nested(name, key, val)
                        items.append(("kv", key, val))
                        i += 1
                    elif re.match(r'^(\w+)\s*\[', sl):
                        sub_match = re.match(r'^(\w+)\s*\[', sl)
                        sub_name = sub_match.group(1)
                        i += 1
                        sub_items = []
                        sub_depth = 1
                        while i < len(lines) and sub_depth > 0:
                            sub_sl = lines[i].rstrip("\r\n").strip()
                            if sub_sl == "]":
                                sub_depth -= 1
                                if sub_depth == 0:
                                    i += 1
                                    break
                            elif sub_sl == "[":
                                sub_depth += 1
                                i += 1
                                continue
                            if not sub_sl or sub_sl.startswith(";"):
                                i += 1
                                continue
                            sub_kv = re.match(r'^(\w+)\s*=\s*(.*)', sub_sl)
                            if sub_kv:
                                sk, sv = sub_kv.group(1), sub_kv.group(2).strip()
                                self._set_nested(f"{name}.{sub_name}", sk, sv)
                                sub_items.append(("kv", sk, sv))
                            i += 1
                        items.append(("struct", sub_name, sub_items))
                    else:
                        i += 1
                result.append(("struct", name, items))
                continue
            kv = re.match(r'^(\w+)\s*=\s*(.*)', stripped)
            if kv:
                key, val = kv.group(1), kv.group(2).strip()
                self.settings[key] = val
                result.append(("kv", key, val))
                i += 1
                continue
            i += 1
        return result

    def _set_nested(self, struct_name: str, key: str, val: str):
        full_key = f"{struct_name}.{key}"
        self.settings[full_key] = val
        if struct_name not in self.structs:
            self.structs[struct_name] = {}
        self.structs[struct_name][key] = val

    def get(self, key: str) -> str:
        return self.settings.get(key, "")

    def get_bool(self, key: str) -> bool:
        return self.get(key).lower() in ("true", "1")

    def set_value(self, key: str, value: str):
        self.settings[key] = value
        if "." in key:
            parts = key.split(".", 1)
            struct_name, field = parts[0], parts[1]
            if struct_name not in self.structs:
                self.structs[struct_name] = {}
            self.structs[struct_name][field] = value

    def save(self, path: Optional[str] = None):
        save_path = path or self.path
        if not save_path:
            raise ValueError("未指定保存路径")
        output_lines = self._rebuild_lines()
        with open(save_path, "w", encoding="utf-8") as f:
            f.writelines(output_lines)

    def _rebuild_lines(self) -> list[str]:
        lines = []
        for entry in self._parse_tree:
            if entry[0] == "comment":
                lines.append(entry[1] + "\n")
            elif entry[0] == "kv":
                _, key, _ = entry
                val = self.settings.get(key, "")
                lines.append(f"{key} = {val}\n")
            elif entry[0] == "struct":
                _, name, items = entry
                lines.append(f"{name} [\n")
                for item in items:
                    if item[0] == "kv":
                        _, key, _ = item
                        full_key = f"{name}.{key}"
                        val = self.settings.get(full_key, "")
                        lines.append(f"    {key} = {val}\n")
                    elif item[0] == "struct":
                        _, sub_name, sub_items = item
                        lines.append(f"    {sub_name} [\n")
                        for si in sub_items:
                            if si[0] == "kv":
                                _, sk, _ = si
                                full_key = f"{name}.{sub_name}.{sk}"
                                val = self.settings.get(full_key, "")
                                lines.append(f"        {sk} = {val}\n")
                        lines.append(f"    ]\n")
                lines.append(f"]\n")
        return lines


# ──────────────────────────────────────────────────────────────────────
# 颜色选择按钮
# ──────────────────────────────────────────────────────────────────────

class ColorButton(tk.Frame):
    def __init__(self, parent, color_str: str = "", **kwargs):
        super().__init__(parent, bg=Colors.CARD_BG, **kwargs)
        self.color_str = color_str
        self._display_color = self._parse_display_color(color_str)

        self.swatch = tk.Canvas(self, width=32, height=32, bd=0, highlightthickness=0,
                                bg=Colors.CARD_BG)
        self.swatch.pack(side="left", padx=(0, 8))
        self._draw_swatch()

        self.label = tk.Label(self, text=color_str or "（默认）", font=Fonts.BODY,
                              bg=Colors.CARD_BG, fg=Colors.TEXT)
        self.label.pack(side="left")

        self.btn = tk.Button(self, text="选择颜色", font=Fonts.BUTTON,
                             bg=Colors.ACCENT, fg="white", bd=0, padx=12, pady=4,
                             activebackground="#3d5bd9", activeforeground="white",
                             cursor="hand2", command=self._pick_color)
        self.btn.pack(side="left", padx=(12, 4))

        self.clear_btn = tk.Button(self, text="清除", font=Fonts.BUTTON,
                                   bg=Colors.HOVER, fg=Colors.TEXT_SECONDARY, bd=0, padx=8, pady=4,
                                   activebackground=Colors.BORDER, activeforeground=Colors.TEXT,
                                   cursor="hand2", command=self._clear_color)
        self.clear_btn.pack(side="left")

        self.swatch.bind("<Button-1>", lambda e: self._pick_color())

    def _parse_display_color(self, s: str) -> str:
        if not s:
            return ""
        s = s.lstrip("#")
        if len(s) == 6:
            return f"#{s}"
        elif len(s) == 8:
            return f"#{s[2:]}"
        return f"#{s}" if s else ""

    def _draw_swatch(self):
        self.swatch.delete("all")
        if self._display_color:
            try:
                self.swatch.create_rectangle(2, 2, 30, 30, fill=self._display_color,
                                             outline=Colors.BORDER, width=1)
            except tk.TclError:
                self.swatch.create_rectangle(2, 2, 30, 30, fill="#cccccc",
                                             outline=Colors.BORDER, width=1)
        else:
            self.swatch.create_rectangle(2, 2, 30, 30, fill="#f0f0f0",
                                         outline=Colors.BORDER, width=1, stipple="gray50")

    def _pick_color(self):
        initial = self._display_color or "#ffffff"
        result = colorchooser.askcolor(initialcolor=initial, title="选择颜色")
        if result and result[1]:
            hex_color = result[1]
            self.color_str = hex_color
            self._display_color = hex_color
            self.label.config(text=hex_color)
            self._draw_swatch()

    def _clear_color(self):
        self.color_str = ""
        self._display_color = ""
        self.label.config(text="（默认）")
        self._draw_swatch()

    def get_value(self) -> str:
        return self.color_str

    def set_value(self, val: str):
        self.color_str = val
        self._display_color = self._parse_display_color(val)
        self.label.config(text=val or "（默认）")
        self._draw_swatch()


# ──────────────────────────────────────────────────────────────────────
# 主应用程序
# ──────────────────────────────────────────────────────────────────────

class SettingsEditor(tk.Tk):
    def __init__(self, settings_path: Optional[str] = None):
        super().__init__()

        self.title("SumatraPDF 高级设置编辑器")
        self.geometry("1100x800")
        self.minsize(950, 650)
        self.configure(bg=Colors.BG)

        self.settings_file = SettingsFile()
        self.current_category = None
        self._sidebar_buttons: list[tk.Button] = []
        # 预建页面: category_name -> (frame, widgets_dict)
        self._pages: dict[str, tuple[tk.Frame, dict[str, Any]]] = {}

        if settings_path:
            self._load_file(settings_path)
        else:
            auto_path = self.settings_file.find_settings_file()
            if auto_path:
                self._load_file(auto_path)
            else:
                self.after(100, self._ask_for_file)

        self._build_ui()

    def _load_file(self, path: str):
        try:
            self.settings_file.load(path)
            self.title(f"SumatraPDF 高级设置编辑器 — {path}")
        except Exception as e:
            messagebox.showerror("错误", f"加载设置文件失败:\n{e}")

    def _build_ui(self):
        # 顶部工具栏
        toolbar = tk.Frame(self, bg=Colors.CARD_BG, height=52)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        # Logo / 标题
        tk.Label(toolbar, text="⚙  SumatraPDF 设置编辑器", font=Fonts.SUBTITLE,
                 bg=Colors.CARD_BG, fg=Colors.TEXT).pack(side="left", padx=20)

        # 文件路径
        self.path_var = tk.StringVar(value=self.settings_file.path or "未加载文件")
        tk.Label(toolbar, textvariable=self.path_var, font=Fonts.SMALL,
                 bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED).pack(side="left", padx=20)

        # 按钮
        btn_frame = tk.Frame(toolbar, bg=Colors.CARD_BG)
        btn_frame.pack(side="right", padx=16)

        self._make_toolbar_button(btn_frame, "打开文件", self._open_file)
        self._make_toolbar_button(btn_frame, "保存", self._save_file, primary=True)

        # 分隔线
        tk.Frame(self, height=1, bg=Colors.BORDER).pack(fill="x")

        # 主体
        body = tk.Frame(self, bg=Colors.BG)
        body.pack(fill="both", expand=True)

        # 左侧边栏
        sidebar_outer = tk.Frame(body, bg=Colors.SIDEBAR_BG, width=220)
        sidebar_outer.pack(side="left", fill="y")
        sidebar_outer.pack_propagate(False)

        sidebar_header = tk.Frame(sidebar_outer, bg=Colors.SIDEBAR_BG)
        sidebar_header.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(sidebar_header, text="设置分类", font=Fonts.SIDEBAR_TITLE,
                 bg=Colors.SIDEBAR_BG, fg=Colors.TEXT).pack(anchor="w")

        # 分隔线
        tk.Frame(sidebar_outer, height=1, bg=Colors.BORDER).pack(fill="x", padx=16)

        # 分类按钮列表（可滚动）
        sidebar_canvas = tk.Canvas(sidebar_outer, bg=Colors.SIDEBAR_BG,
                                   highlightthickness=0, bd=0)
        sidebar_scrollbar = ttk.Scrollbar(sidebar_outer, orient="vertical",
                                          command=sidebar_canvas.yview)
        sidebar_inner = tk.Frame(sidebar_canvas, bg=Colors.SIDEBAR_BG)

        sidebar_inner.bind("<Configure>",
                           lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        sidebar_canvas.create_window((0, 0), window=sidebar_inner, anchor="nw", tags="inner")
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)

        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")

        # 让 canvas 内窗口宽度跟随 canvas
        def _resize_sidebar_inner(event):
            sidebar_canvas.itemconfig("inner", width=event.width)
        sidebar_canvas.bind("<Configure>", _resize_sidebar_inner)

        # 创建分类按钮
        for i, cat in enumerate(CATEGORIES):
            btn = tk.Button(sidebar_inner, text=f"  {cat}", font=Fonts.SIDEBAR,
                            bg=Colors.SIDEBAR_BG, fg=Colors.TEXT_SECONDARY,
                            bd=0, anchor="w", padx=16, pady=10,
                            activebackground=Colors.HOVER, activeforeground=Colors.TEXT,
                            cursor="hand2",
                            command=lambda c=cat, idx=i: self._select_category(c, idx))
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=Colors.HOVER)
                     if b.cget("bg") != Colors.ACCENT_LIGHT else None)
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=Colors.SIDEBAR_BG)
                     if b.cget("bg") != Colors.ACCENT_LIGHT else None)
            self._sidebar_buttons.append(btn)

        # 右侧内容区
        content_outer = tk.Frame(body, bg=Colors.BG)
        content_outer.pack(side="left", fill="both", expand=True)

        # 内容滚动区
        self.canvas = tk.Canvas(content_outer, bg=Colors.BG, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(content_outer, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame,
                                                        anchor="nw", tags="content")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=(1, 0))
        scrollbar.pack(side="right", fill="y")

        # 内容区宽度跟随
        def _resize_content(event):
            self.canvas.itemconfig("content", width=event.width)
        self.canvas.bind("<Configure>", _resize_content)

        # 鼠标滚轮
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # 预建所有分类页面
        self._build_all_pages()

        # 底部状态栏
        status_bar = tk.Frame(self, bg=Colors.CARD_BG, height=32)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        self.status_var = tk.StringVar(value="就绪")
        tk.Label(status_bar, textvariable=self.status_var, font=Fonts.STATUS,
                 bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED).pack(side="left", padx=16)

        # 快捷键
        self.bind("<Control-o>", lambda e: self._open_file())
        self.bind("<Control-s>", lambda e: self._save_file())

        # 选中第一个分类
        self._select_category(CATEGORIES[0], 0)

    def _make_toolbar_button(self, parent, text, command, primary=False):
        if primary:
            btn = tk.Button(parent, text=text, font=Fonts.BUTTON,
                            bg=Colors.ACCENT, fg="white", bd=0, padx=16, pady=6,
                            activebackground="#3d5bd9", activeforeground="white",
                            cursor="hand2", command=command)
        else:
            btn = tk.Button(parent, text=text, font=Fonts.BUTTON,
                            bg=Colors.HOVER, fg=Colors.TEXT, bd=0, padx=16, pady=6,
                            activebackground=Colors.BORDER, activeforeground=Colors.TEXT,
                            cursor="hand2", command=command)
        btn.pack(side="left", padx=4)
        return btn

    def _build_all_pages(self):
        """预建所有分类页面，切换时只显示/隐藏，避免闪烁。"""
        for cat in CATEGORIES:
            page = tk.Frame(self.scrollable_frame, bg=Colors.BG)
            widgets = {}

            # 分类标题
            header = tk.Frame(page, bg=Colors.BG)
            header.pack(fill="x", padx=28, pady=(24, 16))
            tk.Label(header, text=cat, font=Fonts.TITLE,
                     bg=Colors.BG, fg=Colors.TEXT).pack(anchor="w")

            cat_settings = [s for s in SETTINGS_META if s[4] == cat]
            # 对于数组类型的分类，显示提示和参考信息
            array_categories = {
                "快捷键": "shortcuts",
                "外部查看器": "external",
                "选中文字处理": "selection",
            }
            if not cat_settings:
                if cat in array_categories:
                    self._build_array_category_page(page, array_categories[cat])
                else:
                    tk.Label(page, text="此分类没有可编辑的设置项",
                             font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_MUTED).pack(pady=40)
            else:
                for meta in cat_settings:
                    key, stype, default, desc, _, options = meta
                    self._add_setting_card(page, key, stype, default, desc, options, widgets)

            self._pages[cat] = (page, widgets)

    def _build_array_category_page(self, page, page_type):
        """为数组类型的分类（快捷键、外部查看器等）构建参考信息页面。"""

        if page_type == "shortcuts":
            # 快捷键格式说明
            fmt_frame = tk.Frame(page, bg=Colors.CARD_BG,
                                 highlightbackground=Colors.BORDER, highlightthickness=1)
            fmt_frame.pack(fill="x", padx=28, pady=(0, 12))
            fmt_inner = tk.Frame(fmt_frame, bg=Colors.CARD_BG)
            fmt_inner.pack(fill="x", padx=20, pady=16)
            tk.Label(fmt_inner, text="自定义快捷键格式", font=Fonts.BODY_BOLD,
                     bg=Colors.CARD_BG, fg=Colors.TEXT).pack(anchor="w")
            tk.Label(fmt_inner, text=(
                "在设置文件中添加 Shortcuts 数组来自定义快捷键：\n\n"
                "Shortcuts [\n"
                "  [\n"
                "    Cmd = CmdFindNext\n"
                "    Key = F3\n"
                "  ]\n"
                "  [\n"
                "    Cmd = CmdCreateAnnotHighlight #00ff00 openedit\n"
                "    Key = a\n"
                "  ]\n"
                "]"
            ), font=("Consolas", 10), bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY,
                justify="left").pack(anchor="w", pady=(8, 0))

            # 命令列表
            commands = [
                # (分类, [(命令ID, 默认快捷键, 说明)])
                ("文件操作", [
                    ("CmdOpenFile", "Ctrl+O", "打开文件"),
                    ("CmdSaveAs", "Ctrl+S", "另存为"),
                    ("CmdClose", "Ctrl+W", "关闭文档"),
                    ("CmdCloseCurrentDocument", "Q", "关闭当前文档"),
                    ("CmdReloadDocument", "R", "重新加载"),
                    ("CmdPrint", "Ctrl+P", "打印"),
                    ("CmdProperties", "Ctrl+D", "文档属性"),
                    ("CmdRenameFile", "F2", "重命名文件"),
                    ("CmdNewWindow", "Ctrl+N", "新窗口"),
                    ("CmdDuplicateInNewWindow", "Shift+Ctrl+N", "在新窗口打开"),
                    ("CmdReopenLastClosedFile", "Shift+Ctrl+T", "恢复上次关闭的"),
                    ("CmdExit", "Ctrl+Q", "退出"),
                    ("CmdSelectAll", "Ctrl+A", "全选"),
                    ("CmdCopySelection", "Ctrl+C", "复制选中"),
                    ("CmdCommandPalette", "Ctrl+K", "命令面板"),
                ]),
                ("搜索", [
                    ("CmdFindFirst", "Ctrl+F", "查找"),
                    ("CmdFindNext", "F3", "查找下一个"),
                    ("CmdFindPrev", "Shift+F3", "查找上一个"),
                    ("CmdFindNextSel", "Ctrl+F3", "查找选中文字下一个"),
                    ("CmdFindPrevSel", "Shift+Ctrl+F3", "查找选中文字上一个"),
                ]),
                ("页面视图", [
                    ("CmdSinglePageView", "Ctrl+6", "单页视图"),
                    ("CmdFacingView", "Ctrl+7", "双页视图"),
                    ("CmdBookView", "Ctrl+8", "书籍视图"),
                    ("CmdToggleContinuousView", "C", "切换连续滚动"),
                    ("CmdToggleFullscreen", "F11", "全屏"),
                    ("CmdTogglePresentationMode", "F5", "演示模式"),
                    ("CmdToggleToolbar", "F8", "显示/隐藏工具栏"),
                    ("CmdToggleMenuBar", "F9", "显示/隐藏菜单栏"),
                    ("CmdInvertColors", "I", "反转颜色"),
                    ("CmdRotateLeft", "[", "向左旋转"),
                    ("CmdRotateRight", "]", "向右旋转"),
                    ("CmdToggleMangaMode", "", "漫画模式"),
                    ("CmdToggleLinks", "", "显示/隐藏链接框"),
                ]),
                ("页面导航", [
                    ("CmdGoToNextPage", "N", "下一页"),
                    ("CmdGoToPrevPage", "P", "上一页"),
                    ("CmdGoToFirstPage", "Home", "第一页"),
                    ("CmdGoToLastPage", "End", "最后一页"),
                    ("CmdGoToPage", "G", "跳转到页"),
                    ("CmdScrollUp", "K / ↑", "向上滚动"),
                    ("CmdScrollDown", "J / ↓", "向下滚动"),
                    ("CmdScrollLeft", "H / ←", "向左滚动"),
                    ("CmdScrollRight", "L / →", "向右滚动"),
                    ("CmdScrollUpPage", "PageUp", "向上翻页"),
                    ("CmdScrollDownPage", "PageDown", "向下翻页"),
                    ("CmdNavigateBack", "Alt+←", "后退"),
                    ("CmdNavigateForward", "Alt+→", "前进"),
                    ("CmdOpenNextFileInFolder", "Shift+Ctrl+→", "打开下一个文件"),
                    ("CmdOpenPrevFileInFolder", "Shift+Ctrl+←", "打开上一个文件"),
                ]),
                ("标签页", [
                    ("CmdNextTab", "Ctrl+PageUp", "下一个标签"),
                    ("CmdPrevTab", "Ctrl+PageDown", "上一个标签"),
                    ("CmdNextTabSmart", "Ctrl+Tab", "智能切换标签"),
                    ("CmdPrevTabSmart", "Ctrl+Shift+Tab", "智能切换标签(反向)"),
                    ("CmdMoveTabRight", "Ctrl+Shift+PageUp", "标签右移"),
                    ("CmdMoveTabLeft", "Ctrl+Shift+PageDown", "标签左移"),
                    ("CmdCloseAllTabs", "", "关闭所有标签"),
                    ("CmdCloseOtherTabs", "", "关闭其他标签"),
                    ("CmdCloseTabsToTheLeft", "", "关闭左侧标签"),
                    ("CmdCloseTabsToTheRight", "", "关闭右侧标签"),
                ]),
                ("缩放", [
                    ("CmdZoomIn", "Ctrl++", "放大"),
                    ("CmdZoomOut", "Ctrl+-", "缩小"),
                    ("CmdZoomFitPage", "Ctrl+0", "适合页面"),
                    ("CmdZoomFitWidth", "Ctrl+2", "适合宽度"),
                    ("CmdZoomFitContent", "Ctrl+3", "适合内容"),
                    ("CmdZoomActualSize", "Ctrl+1", "实际大小"),
                    ("CmdZoomCustom", "Ctrl+Y", "自定义缩放"),
                    ("CmdToggleZoom", "Z", "切换缩放"),
                ]),
                ("收藏夹", [
                    ("CmdFavoriteAdd", "Ctrl+B", "添加收藏"),
                    ("CmdFavoriteDel", "", "删除收藏"),
                    ("CmdFavoriteToggle", "", "显示/隐藏收藏夹"),
                ]),
                ("批注", [
                    ("CmdCreateAnnotHighlight", "A", "高亮批注"),
                    ("CmdCreateAnnotUnderline", "U", "下划线批注"),
                    ("CmdCreateAnnotStrikeOut", "", "删除线批注"),
                    ("CmdCreateAnnotSquiggly", "", "波浪线批注"),
                    ("CmdCreateAnnotFreeText", "", "文本批注"),
                    ("CmdCreateAnnotText", "", "便签批注"),
                    ("CmdCreateAnnotStamp", "", "图章批注"),
                    ("CmdCreateAnnotInk", "", "墨迹批注"),
                    ("CmdCreateAnnotCircle", "", "圆形批注"),
                    ("CmdCreateAnnotSquare", "", "矩形批注"),
                    ("CmdCreateAnnotLine", "", "线条批注"),
                    ("CmdCreateAnnotPolygon", "", "多边形批注"),
                    ("CmdDeleteAnnotation", "Delete", "删除批注"),
                    ("CmdSaveAnnotations", "Shift+Ctrl+S", "保存批注到PDF"),
                ]),
                ("外部应用", [
                    ("CmdTranslateSelectionWithGoogle", "", "Google 翻译选中文字"),
                    ("CmdTranslateSelectionWithDeepL", "", "DeepL 翻译选中文字"),
                    ("CmdSearchSelectionWithGoogle", "", "Google 搜索选中文字"),
                    ("CmdSearchSelectionWithBing", "", "Bing 搜索选中文字"),
                    ("CmdSearchSelectionWithWikipedia", "", "Wikipedia 搜索"),
                    ("CmdSearchSelectionWithGoogleScholar", "", "Google 学术搜索"),
                    ("CmdOpenWithAcrobat", "", "用 Acrobat 打开"),
                    ("CmdOpenWithFoxIt", "", "用 Foxit 打开"),
                    ("CmdSendByEmail", "", "通过邮件发送"),
                ]),
                ("帮助与系统", [
                    ("CmdHelpOpenManual", "F1", "打开手册"),
                    ("CmdOptions", "", "选项"),
                    ("CmdAdvancedOptions", "", "高级设置"),
                    ("CmdCheckUpdate", "", "检查更新"),
                    ("CmdChangeLanguage", "", "更改语言"),
                ]),
            ]

            for group_name, cmds in commands:
                group_frame = tk.Frame(page, bg=Colors.CARD_BG,
                                       highlightbackground=Colors.BORDER, highlightthickness=1)
                group_frame.pack(fill="x", padx=28, pady=(0, 8))
                group_inner = tk.Frame(group_frame, bg=Colors.CARD_BG)
                group_inner.pack(fill="x", padx=20, pady=12)

                tk.Label(group_inner, text=group_name, font=Fonts.BODY_BOLD,
                         bg=Colors.CARD_BG, fg=Colors.ACCENT).pack(anchor="w", pady=(0, 6))

                for cmd_id, shortcut, desc in cmds:
                    row = tk.Frame(group_inner, bg=Colors.CARD_BG)
                    row.pack(fill="x", pady=1)
                    tk.Label(row, text=cmd_id, font=("Consolas", 9),
                             bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED, width=32, anchor="w").pack(side="left")
                    tk.Label(row, text=shortcut, font=Fonts.SMALL,
                             bg=Colors.CARD_BG, fg=Colors.ACCENT, width=16, anchor="w").pack(side="left")
                    tk.Label(row, text=desc, font=Fonts.SMALL,
                             bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY, anchor="w").pack(side="left")

        elif page_type == "external":
            tk.Label(page, text=(
                "外部查看器是数组格式，需要手动编辑设置文件。\n\n"
                "格式示例：\n\n"
                "ExternalViewers [\n"
                "  [\n"
                '    CommandLine = "C:\\Path\\to\\viewer.exe" "%1"\n'
                "    Name = 我的查看器\n"
                "    Filter = *.pdf\n"
                "    Key = Alt + 1\n"
                "  ]\n"
                "]"
            ), font=("Consolas", 10), bg=Colors.BG, fg=Colors.TEXT_SECONDARY,
                justify="left", wraplength=650).pack(pady=40, padx=28, anchor="w")

        elif page_type == "selection":
            tk.Label(page, text=(
                "选中文字处理是数组格式，需要手动编辑设置文件。\n\n"
                "格式示例：\n\n"
                "SelectionHandlers [\n"
                "  [\n"
                "    URL = https://translate.google.com/?sl=auto&tl=zh-CN&text=${selection}\n"
                "    Name = Google 翻译\n"
                "    Key = Ctrl + T\n"
                "  ]\n"
                "]"
            ), font=("Consolas", 10), bg=Colors.BG, fg=Colors.TEXT_SECONDARY,
                justify="left", wraplength=650).pack(pady=40, padx=28, anchor="w")

    def _select_category(self, category: str, idx: int):
        # 更新侧边栏选中状态
        for i, btn in enumerate(self._sidebar_buttons):
            if i == idx:
                btn.configure(bg=Colors.ACCENT_LIGHT, fg=Colors.ACCENT)
            else:
                btn.configure(bg=Colors.SIDEBAR_BG, fg=Colors.TEXT_SECONDARY)

        # 隐藏当前页面
        if self.current_category and self.current_category in self._pages:
            self._pages[self.current_category][0].pack_forget()

        # 显示新页面
        self.current_category = category
        page, _ = self._pages[category]
        page.pack(fill="both", expand=True)

        # 滚动到顶部
        self.canvas.yview_moveto(0)

    def _add_setting_card(self, parent, key, stype, default, desc, options, widgets):
        current = self.settings_file.get(key)

        # 卡片
        card = tk.Frame(parent, bg=Colors.CARD_BG,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        card.pack(fill="x", padx=28, pady=(0, 8))

        inner = tk.Frame(card, bg=Colors.CARD_BG)
        inner.pack(fill="x", padx=20, pady=16)

        # 上方：描述 + 配置键
        top = tk.Frame(inner, bg=Colors.CARD_BG)
        top.pack(fill="x", pady=(0, 12))

        tk.Label(top, text=desc, font=Fonts.BODY, bg=Colors.CARD_BG,
                 fg=Colors.TEXT, wraplength=650, anchor="w", justify="left").pack(anchor="w")
        tk.Label(top, text=key, font=Fonts.KEY, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_MUTED).pack(anchor="w", pady=(4, 0))

        # 下方：控件
        widget_frame = tk.Frame(inner, bg=Colors.CARD_BG)
        widget_frame.pack(fill="x")

        if stype == "bool":
            var = tk.BooleanVar(value=self.settings_file.get_bool(key))
            cb = tk.Checkbutton(widget_frame, text="启用", variable=var, font=Fonts.BODY,
                                bg=Colors.CARD_BG, fg=Colors.TEXT, selectcolor=Colors.CARD_BG,
                                activebackground=Colors.CARD_BG, activeforeground=Colors.TEXT,
                                bd=0, highlightthickness=0, cursor="hand2")
            cb.pack(side="left")
            widgets[key] = ("bool", var)

        elif stype == "int":
            var = tk.StringVar(value=current if current else str(default))
            self._make_entry(widget_frame, var)
            widgets[key] = ("str", var)

        elif stype == "float":
            var = tk.StringVar(value=current if current else str(default))
            self._make_entry(widget_frame, var)
            widgets[key] = ("str", var)

        elif stype == "str":
            var = tk.StringVar(value=current)
            entry = self._make_entry(widget_frame, var, width=50)
            entry.pack(side="left", fill="x", expand=True)
            widgets[key] = ("str", var)

        elif stype == "color":
            color_btn = ColorButton(widget_frame, color_str=current)
            color_btn.pack(side="left")
            widgets[key] = ("color", color_btn)

        elif stype == "choice":
            var = tk.StringVar(value=current if current else str(default))
            combo = ttk.Combobox(widget_frame, textvariable=var, values=options,
                                 state="readonly", width=28, font=Fonts.INPUT)
            combo.pack(side="left")
            widgets[key] = ("str", var)

        elif stype == "compact":
            var = tk.StringVar(value=current if current else str(default))
            self._make_entry(widget_frame, var, width=30)
            tk.Label(widget_frame, text="空格分隔多个值", font=Fonts.SMALL_MUTED,
                     bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED).pack(side="left", padx=12)
            widgets[key] = ("str", var)

    def _make_entry(self, parent, var, width=20):
        entry_frame = tk.Frame(parent, bg=Colors.INPUT_BORDER, padx=1, pady=1)
        entry_frame.pack(side="left")
        entry = tk.Entry(entry_frame, textvariable=var, font=Fonts.INPUT, width=width,
                         bg=Colors.INPUT_BG, fg=Colors.TEXT,
                         insertbackground=Colors.TEXT, bd=0,
                         highlightthickness=1, highlightcolor=Colors.INPUT_FOCUS,
                         highlightbackground=Colors.INPUT_BORDER)
        entry.pack(fill="x", padx=2, pady=2)
        return entry

    def _collect_values(self):
        """从所有预建页面收集控件值。"""
        for cat, (page, widgets) in self._pages.items():
            for key, (wtype, widget) in widgets.items():
                if wtype == "bool":
                    val = "true" if widget.get() else "false"
                elif wtype == "str":
                    val = widget.get()
                elif wtype == "color":
                    val = widget.get_value()
                else:
                    val = str(widget)
                self.settings_file.set_value(key, val)

    def _open_file(self):
        path = filedialog.askopenfilename(
            title="打开 SumatraPDF 设置文件",
            filetypes=[("设置文件", "*.txt"), ("所有文件", "*.*")],
            initialdir=os.path.expanduser("~\\AppData\\Local\\SumatraPDF")
        )
        if path:
            self._load_file(path)
            self.path_var.set(path)
            # 重建所有页面以加载新数据
            self._rebuild_pages()

    def _rebuild_pages(self):
        """销毁并重建所有分类页面（用于加载新文件后）。"""
        # 隐藏当前页面
        if self.current_category and self.current_category in self._pages:
            self._pages[self.current_category][0].pack_forget()
        # 销毁旧页面
        for cat, (page, widgets) in self._pages.items():
            page.destroy()
        self._pages.clear()
        # 重建
        self._build_all_pages()
        # 恢复选中状态
        if self.current_category and self.current_category in CATEGORIES:
            idx = CATEGORIES.index(self.current_category)
            self._select_category(self.current_category, idx)
        else:
            self._select_category(CATEGORIES[0], 0)

    def _save_file(self):
        self._collect_values()
        try:
            self.settings_file.save()
            self.status_var.set(f"✓ 已保存到 {self.settings_file.path}")
            messagebox.showinfo("保存成功", "设置已保存。\n部分更改可能需要重启 SumatraPDF 才能生效。")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败:\n{e}")

    def _ask_for_file(self):
        result = messagebox.askyesnocancel(
            "未找到设置文件",
            "无法自动检测到 SumatraPDF-settings.txt。\n\n"
            "是否要手动定位？\n\n"
            "常见位置:\n"
            "  安装版: %LOCALAPPDATA%\\SumatraPDF\\\n"
            "  便携版: 与 SumatraPDF.exe 同目录"
        )
        if result is True:
            self._open_file()
        elif result is False:
            path = filedialog.asksaveasfilename(
                title="创建新设置文件",
                defaultextension=".txt",
                filetypes=[("设置文件", "*.txt")],
                initialfile="SumatraPDF-settings.txt"
            )
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("; SumatraPDF 设置文件\n")
                self._load_file(path)
                self.path_var.set(path)
                self._rebuild_pages()


def main():
    settings_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = SettingsEditor(settings_path)
    app.mainloop()


if __name__ == "__main__":
    main()
