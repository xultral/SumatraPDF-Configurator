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

CATEGORIES = [
    "常规",
    "显示与缩放",
    "界面与交互",
    "颜色与主题",
    "固定页面 UI",
    "电子书 UI",
    "漫画书 UI",
    "图片 UI",
    "CHM UI",
    "批注",
    "正向搜索",
    "打印",
    "全屏模式",
    "AI 聊天 (Claude Code)",
    "AI 聊天 (Grok Build)",
    "AI 聊天 (Codex Build)",
    "专家 / 内部",
]

SETTINGS_META = [
    # ── 常规 ──
    ("CheckForUpdates", "bool", True,
     "每天检查一次更新", "常规", None),
    ("NoHomeTab", "bool", False,
     "不打开主页标签", "常规", None),
    ("HomePageSortByFrequentlyRead", "bool", False,
     "主页按使用频率排序（3.6 之前的行为）", "常规", None),
    ("HomePageShowList", "bool", False,
     "主页历史以列表而非缩略图显示", "常规", None),
    ("UseTabs", "bool", True,
     "在标签页中打开文档（而非新窗口）", "常规", None),
    ("TabsMru", "bool", False,
     "Ctrl+Tab 按最近使用顺序切换标签", "常规", None),
    ("ReuseInstance", "bool", True,
     "始终使用已有 SumatraPDF 进程打开文件", "常规", None),
    ("RememberOpenedFiles", "bool", True,
     "记住已打开的文件及其显示设置", "常规", None),
    ("RememberStatePerDocument", "bool", True,
     "为每个文档单独存储显示设置", "常规", None),
    ("RestoreSession", "bool", True,
     "启动时恢复上次会话", "常规", None),
    ("LazyLoading", "bool", False,
     "延迟加载文档，直到选中其标签页", "常规", None),
    ("UiLanguage", "str", "",
     "界面语言 ISO 代码（如 cn, de, fr, ja）", "常规", None),

    # ── 显示与缩放 ──
    ("DefaultDisplayMode", "choice", "automatic",
     "默认页面布局", "显示与缩放",
     ["automatic", "single page", "facing", "book view",
      "continuous", "continuous facing", "continuous book view"]),
    ("DefaultZoom", "str", "fit page",
     "默认缩放（fit page, fit width, fit content 或百分比如 100%）",
     "显示与缩放", None),
    ("ZoomIncrement", "float", 0,
     "缩放步长百分比（0 = 使用 ZoomLevels）", "显示与缩放", None),
    ("ZoomLevels", "str", "",
     "自定义缩放级别（空格分隔，范围 8.33-6400）", "显示与缩放", None),
    ("SmoothScroll", "bool", False,
     "启用平滑滚动", "显示与缩放", None),
    ("FastScrollOverScrollbar", "bool", False,
     "鼠标在滚动条上时加速滚轮滚动", "显示与缩放", None),
    ("Scrollbars", "choice", "windows",
     "滚动条模式", "显示与缩放",
     ["windows", "smart", "overlay", "hidden"]),
    ("ScrollbarInSinglePage", "bool", False,
     "在单页模式下显示滚动条", "显示与缩放", None),
    ("DisableAntiAlias", "bool", False,
     "禁用 PDF 渲染的抗锯齿", "显示与缩放", None),
    ("PreventSleepInFullscreen", "bool", True,
     "全屏/演示模式下防止屏幕关闭", "显示与缩放", None),
    ("CitationHoverDelay", "int", -1,
     "引用悬停弹出延迟（毫秒，-1 = 禁用）", "显示与缩放", None),

    # ── 界面与交互 ──
    ("ShowToolbar", "bool", True,
     "显示工具栏", "界面与交互", None),
    ("Toolbar", "choice", "",
     "工具栏模式（空 = 由 ShowToolbar 决定）", "界面与交互",
     ["", "show", "hide", "overlay"]),
    ("ToolbarPosition", "choice", "top",
     "工具栏位置", "界面与交互", ["top", "bottom"]),
    ("ToolbarSize", "int", 18,
     "工具栏高度", "界面与交互", None),
    ("TabWidth", "int", 300,
     "单个标签页最大宽度", "界面与交互", None),
    ("ShowMenubar", "bool", True,
     "显示菜单栏（F9 切换）", "界面与交互", None),
    ("ShowMenubarWithTabs", "bool", False,
     "使用标签页时显示菜单栏", "界面与交互", None),
    ("ShowFavorites", "bool", False,
     "显示收藏夹侧边栏", "界面与交互", None),
    ("ShowToc", "bool", True,
     "如果文档包含目录则显示目录侧边栏", "界面与交互", None),
    ("ShowStartPage", "bool", True,
     "未打开文档时显示常用文档列表", "界面与交互", None),
    ("ShowLinks", "bool", False,
     "在文档中的链接周围绘制蓝色边框", "界面与交互", None),
    ("ShowTips", "bool", True,
     "在主页显示提示", "界面与交互", None),
    ("SidebarDx", "int", 0,
     "收藏夹/书签侧边栏宽度", "界面与交互", None),
    ("TocDy", "int", 0,
     "当侧边栏两部分都可见时，目录部分的高度", "界面与交互", None),
    ("SearchUIFloating", "bool", False,
     "使用带结果列表的浮动查找窗口", "界面与交互", None),
    ("FullPathInTitle", "bool", False,
     "在标题栏显示文件完整路径", "界面与交互", None),
    ("EscToExit", "bool", False,
     "按 Esc 键关闭 SumatraPDF", "界面与交互", None),
    ("TreeFontName", "str", "automatic",
     "书签/收藏夹树形视图字体（automatic = Windows 默认）",
     "界面与交互", None),
    ("TreeFontSize", "int", 0,
     "树形视图字体大小（0 = Windows 默认）", "界面与交互", None),
    ("UIFontSize", "int", 0,
     "覆盖应用程序字体大小（0 = Windows 默认）", "界面与交互", None),
    ("ReadAloudVoiceId", "str", "",
     "朗读功能的语音 ID（空 = 系统默认）", "界面与交互", None),
    ("ReadAloudSpeed", "float", 1,
     "朗读速度倍率（0.5-3.0）", "界面与交互", None),

    # ── 颜色与主题 ──
    ("Theme", "choice", "",
     "颜色主题", "颜色与主题", ["", "light", "dark", "darker"]),
    ("MainWindowBackground", "color", "#80fff200",
     "非文档窗口的背景色", "颜色与主题", None),
    ("CustomColors", "str", "",
     "背景色选择器的自定义颜色（空格分隔，最多 13 个）",
     "颜色与主题", None),
    ("UseSysColors", "bool", False,
     "使用 Windows 系统颜色（覆盖其他颜色设置）", "颜色与主题", None),

    # ── 固定页面 UI ──
    ("FixedPageUI.TextColor", "color", "#000000",
     "文字颜色（替换黑色）", "固定页面 UI", None),
    ("FixedPageUI.BackgroundColor", "color", "#ffffff",
     "背景色（替换白色）", "固定页面 UI", None),
    ("FixedPageUI.SelectionColor", "color", "#ffff00",
     "文字选择/查找高亮颜色（#aarrggbb 控制透明度）", "固定页面 UI", None),
    ("FixedPageUI.WindowMargin", "compact", "2 4 2 4",
     "窗口边距：上 右 下 左", "固定页面 UI", None),
    ("FixedPageUI.PageSpacing", "compact", "4 4",
     "页面间距：水平 垂直", "固定页面 UI", None),
    ("FixedPageUI.GradientColors", "str", "",
     "渐变背景色（最多 3 个，空格分隔）", "固定页面 UI", None),
    ("FixedPageUI.InvertColors", "bool", False,
     "交换文字和背景颜色", "固定页面 UI", None),
    ("FixedPageUI.WindowBgCol", "color", "",
     "PDF 文件的画布背景色", "固定页面 UI", None),

    # ── 电子书 UI ──
    ("EBookUI.FontSize", "float", 0,
     "字体大小（0 = 默认 8.0）", "电子书 UI", None),
    ("EBookUI.LayoutDx", "float", 0,
     "布局宽度（0 = 默认 420）", "电子书 UI", None),
    ("EBookUI.LayoutDy", "float", 0,
     "布局高度（0 = 默认 595）", "电子书 UI", None),
    ("EBookUI.IgnoreDocumentCSS", "bool", False,
     "忽略电子书的 CSS", "电子书 UI", None),
    ("EBookUI.CustomCSS", "str", "",
     "自定义 CSS（可能需要设置 IgnoreDocumentCSS = true）", "电子书 UI", None),
    ("EBookUI.WindowBgCol", "color", "",
     "电子书的画布背景色", "电子书 UI", None),

    # ── 漫画书 UI ──
    ("ComicBookUI.WindowMargin", "compact", "0 0 0 0",
     "窗口边距：上 右 下 左", "漫画书 UI", None),
    ("ComicBookUI.PageSpacing", "compact", "4 4",
     "页面间距：水平 垂直", "漫画书 UI", None),
    ("ComicBookUI.CbxMangaMode", "bool", False,
     "默认使用漫画模式（从右到左阅读）", "漫画书 UI", None),
    ("ComicBookUI.WindowBgCol", "color", "",
     "漫画书的画布背景色", "漫画书 UI", None),

    # ── 图片 UI ──
    ("ImageUI.WindowBgCol", "color", "",
     "图片文件的画布背景色", "图片 UI", None),
    ("ImageUI.DefaultZoom", "choice", "shrink to fit",
     "图片文件的默认缩放", "图片 UI",
     ["fit page", "fit width", "fit content", "shrink to fit"]),

    # ── CHM UI ──
    ("ChmUI.UseFixedPageUI", "bool", False,
     "对 CHM 文档使用 PDF 的 UI", "CHM UI", None),

    # ── 批注 ──
    ("Annotations.HighlightColor", "color", "#ffff00",
     "高亮批注颜色", "批注", None),
    ("Annotations.UnderlineColor", "color", "#00ff00",
     "下划线批注颜色", "批注", None),
    ("Annotations.SquigglyColor", "color", "#ff00ff",
     "波浪线批注颜色", "批注", None),
    ("Annotations.StrikeOutColor", "color", "#ff0000",
     "删除线批注颜色", "批注", None),
    ("Annotations.FreeTextColor", "color", "",
     "自由文本批注的文字颜色", "批注", None),
    ("Annotations.FreeTextBackgroundColor", "color", "",
     "自由文本批注的背景色", "批注", None),
    ("Annotations.FreeTextOpacity", "int", 100,
     "自由文本不透明度（0-100）", "批注", None),
    ("Annotations.FreeTextSize", "int", 12,
     "自由文本批注字体大小", "批注", None),
    ("Annotations.FreeTextBorderWidth", "int", 1,
     "自由文本批注边框宽度", "批注", None),
    ("Annotations.TextIconColor", "color", "",
     "文字图标批注颜色", "批注", None),
    ("Annotations.TextIconType", "choice", "",
     "文字批注图标类型", "批注",
     ["", "comment", "help", "insert", "key", "new paragraph", "note", "paragraph"]),
    ("Annotations.DefaultAuthor", "str", "",
     "默认批注作者（空 = Windows 用户名，(none) = 不添加）",
     "批注", None),

    # ── 正向搜索 ──
    ("ForwardSearch.HighlightOffset", "int", 0,
     "高亮偏移（>0 = 左边距矩形样式）", "正向搜索", None),
    ("ForwardSearch.HighlightWidth", "int", 15,
     "高亮矩形宽度", "正向搜索", None),
    ("ForwardSearch.HighlightColor", "color", "#6581ff",
     "正向搜索高亮颜色", "正向搜索", None),
    ("ForwardSearch.HighlightPermanent", "bool", False,
     "高亮保持到下次点击（而非自动消失）", "正向搜索", None),

    # ── 打印 ──
    ("PrinterDefaults.PrintScale", "choice", "shrink",
     "默认打印缩放", "打印", ["shrink", "fit", "none"]),
    ("PrinterDefaults.Collate", "choice", "default",
     "默认逐份打印设置", "打印", ["default", "collate", "nocollate"]),

    # ── 全屏模式 ──
    ("Fullscreen.ShowToolbar", "bool", False,
     "全屏模式下显示工具栏", "全屏模式", None),
    ("Fullscreen.ShowMenubar", "bool", False,
     "全屏模式下显示菜单栏", "全屏模式", None),

    # ── AI 聊天 (Claude Code) ──
    ("ClaudeCode.Model", "str", "sonnet",
     "Claude 模型别名（sonnet, opus, haiku）", "AI 聊天 (Claude Code)", None),
    ("ClaudeCode.Models", "str", "",
     "下拉菜单中的额外模型别名（逗号分隔）", "AI 聊天 (Claude Code)", None),
    ("ClaudeCode.Effort", "choice", "1",
     "推理努力级别", "AI 聊天 (Claude Code)", ["0", "1", "2", "3"]),
    ("ClaudeCode.SkipPermissions", "bool", False,
     "传递 --dangerously-skip-permissions 参数", "AI 聊天 (Claude Code)", None),
    ("ClaudeCode.BgColor", "color", "#ffffff",
     "聊天面板背景色", "AI 聊天 (Claude Code)", None),

    # ── AI 聊天 (Grok Build) ──
    ("GrokBuild.Model", "str", "grok-composer-2.5-fast",
     "Grok 模型 ID", "AI 聊天 (Grok Build)", None),
    ("GrokBuild.Models", "str", "",
     "下拉菜单中的额外模型 ID（逗号分隔）", "AI 聊天 (Grok Build)", None),
    ("GrokBuild.Effort", "choice", "1",
     "推理努力级别", "AI 聊天 (Grok Build)", ["0", "1", "2", "3", "4"]),
    ("GrokBuild.AlwaysApprove", "bool", False,
     "传递 --always-approve（自动批准工具执行）", "AI 聊天 (Grok Build)", None),
    ("GrokBuild.BgColor", "color", "#ffffff",
     "聊天面板背景色", "AI 聊天 (Grok Build)", None),

    # ── AI 聊天 (Codex Build) ──
    ("CodexBuild.Model", "str", "gpt-5.5",
     "Codex 模型 ID", "AI 聊天 (Codex Build)", None),
    ("CodexBuild.Models", "str", "",
     "下拉菜单中的额外模型 ID（逗号分隔）", "AI 聊天 (Codex Build)", None),
    ("CodexBuild.Sandbox", "choice", "1",
     "沙箱模式", "AI 聊天 (Codex Build)", ["0", "1", "2"]),
    ("CodexBuild.SkipSandbox", "bool", False,
     "传递 --dangerously-bypass-approvals-and-sandbox", "AI 聊天 (Codex Build)", None),
    ("CodexBuild.BgColor", "color", "#ffffff",
     "聊天面板背景色", "AI 聊天 (Codex Build)", None),

    # ── 专家 / 内部 ──
    ("CustomScreenDPI", "int", 0,
     "屏幕 DPI 覆盖（0 = 使用系统值）", "专家 / 内部", None),
    ("DisableJavaScript", "bool", False,
     "禁用 PDF 文档中的 JavaScript", "专家 / 内部", None),
    ("AllowExternalImages", "bool", False,
     "允许 PDF 加载外部图片", "专家 / 内部", None),
    ("EnableTeXEnhancements", "bool", False,
     "在设置 -> 选项中显示 SyncTeX 反向搜索命令", "专家 / 内部", None),
    ("InverseSearchCmdLine", "str", "",
     "LaTeX 编辑器反向搜索命令", "专家 / 内部", None),
    ("ReloadModifiedDocuments", "bool", True,
     "自动重新加载已更改的文档", "专家 / 内部", None),
    ("DisableAutoLinks", "bool", False,
     "禁用 PDF 文本中 URL 的自动链接", "专家 / 内部", None),
    ("AIChatSidebarDx", "int", 0,
     "AI 聊天侧边栏宽度（0 = 默认）", "专家 / 内部", None),
    ("TranslateToLang", "str", "",
     "选中文字翻译的目标语言", "专家 / 内部", None),
    ("DefaultPasswords", "str", "",
     "受保护文档的密码（空格分隔）", "专家 / 内部", None),
    ("VersionToSkip", "str", "",
     "跳过更新通知的版本号", "专家 / 内部", None),
    ("WindowState", "int", 1,
     "默认窗口状态（1=正常, 2=最大化, 3=全屏, 4=最小化）",
     "专家 / 内部", None),
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
            if not cat_settings:
                tk.Label(page, text="此分类没有可编辑的设置项",
                         font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_MUTED).pack(pady=40)
            else:
                for meta in cat_settings:
                    key, stype, default, desc, _, options = meta
                    self._add_setting_card(page, key, stype, default, desc, options, widgets)

            self._pages[cat] = (page, widgets)

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
