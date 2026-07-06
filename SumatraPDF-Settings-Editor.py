#!/usr/bin/env python3
"""
SumatraPDF 高级设置编辑器
=========================
一个用于可视化编辑 SumatraPDF 高级设置文件 (SumatraPDF-settings.txt) 的 GUI 工具。
替代手动编辑文本文件，提供直观的分类界面和适当的输入控件。

需要: Python 3.8+ (tkinter 已包含在标准 Python 发行版中)

用法:
    python SumatraPDF-Settings-Editor.py [设置文件路径]

如果不指定路径，工具会自动检测设置文件位置:
  - 安装版: %LOCALAPPDATA%\\SumatraPDF\\SumatraPDF-settings.txt
  - 便携版: 与 SumatraPDF.exe 同目录
"""

import os
import sys
import re
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from typing import Any, Optional

# 高 DPI 支持 - 让界面在高分屏上清晰显示
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# ──────────────────────────────────────────────────────────────────────
# 设置元数据: 定义每个已知设置的类型、默认值、描述和所属分类
# ──────────────────────────────────────────────────────────────────────

# 设置类型: "bool", "int", "float", "str", "color", "choice", "compact"
# "compact" = 空格分隔的多值，如 "2 4 2 4"

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

# 每条记录: (配置键, 类型, 默认值, 中文描述, 分类, 选项列表或None)
# 嵌套设置使用点号表示: "FixedPageUI.TextColor"
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

# 构建快速查找字典
SETTINGS_LOOKUP = {s[0]: s for s in SETTINGS_META}


# ──────────────────────────────────────────────────────────────────────
# 设置文件解析器 / 写入器
# ──────────────────────────────────────────────────────────────────────

class SettingsFile:
    """解析和写入 SumatraPDF-settings.txt，保留注释和结构。"""

    def __init__(self):
        self.path: Optional[str] = None
        self.raw_lines: list[str] = []
        self.settings: dict[str, str] = {}  # 键 -> 值（字符串）
        self.structs: dict[str, dict[str, str]] = {}  # "结构名" -> {字段: 值}
        self._parse_tree: list = []  # 保留结构用于往返保存

    def find_settings_file(self) -> Optional[str]:
        """自动检测设置文件位置。"""
        candidates = []

        # 1. 安装版: %LOCALAPPDATA%\SumatraPDF
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            p = os.path.join(local_app_data, "SumatraPDF", "SumatraPDF-settings.txt")
            if os.path.isfile(p):
                candidates.append(p)

        # 2. 便携版: 与此脚本同目录或上级目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for d in [script_dir, os.path.dirname(script_dir)]:
            p = os.path.join(d, "SumatraPDF-settings.txt")
            if os.path.isfile(p):
                candidates.append(p)

        # 3. SumatraPDF.exe 旁边
        for d in [script_dir, os.path.dirname(script_dir)]:
            exe = os.path.join(d, "SumatraPDF.exe")
            if os.path.isfile(exe):
                p = os.path.join(d, "SumatraPDF-settings.txt")
                if os.path.isfile(p) and p not in candidates:
                    candidates.append(p)

        return candidates[0] if candidates else None

    def load(self, path: str):
        """加载并解析设置文件。"""
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            self.raw_lines = f.readlines()

        self.settings.clear()
        self.structs.clear()
        self._parse_tree = self._parse_lines(self.raw_lines)

    def _parse_lines(self, lines: list[str]) -> list:
        """将文本行解析为保留顺序的树结构。"""
        result = []
        i = 0
        while i < len(lines):
            line = lines[i].rstrip("\r\n")
            stripped = line.strip()

            # 注释或空行
            if not stripped or stripped.startswith(";"):
                result.append(("comment", stripped))
                i += 1
                continue

            # 结构体: Name [
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
                    elif sl == "[":
                        depth += 1
                        i += 1
                        continue
                    elif sl.startswith("["):
                        depth += 1
                        i += 1
                        continue

                    if not sl or sl.startswith(";"):
                        i += 1
                        continue

                    # 结构体内的键值对
                    kv = re.match(r'^(\w+)\s*=\s*(.*)', sl)
                    if kv:
                        key, val = kv.group(1), kv.group(2).strip()
                        self._set_nested(name, key, val)
                        items.append(("kv", key, val))
                        i += 1
                    elif re.match(r'^(\w+)\s*\[', sl):
                        # 嵌套结构体
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

            # 顶层键值对
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
        """设置嵌套结构体中的值，如 FixedPageUI.TextColor。"""
        full_key = f"{struct_name}.{key}"
        self.settings[full_key] = val
        if struct_name not in self.structs:
            self.structs[struct_name] = {}
        self.structs[struct_name][key] = val

    def get(self, key: str) -> str:
        """通过点号键获取设置值。"""
        return self.settings.get(key, "")

    def get_bool(self, key: str) -> bool:
        return self.get(key).lower() in ("true", "1")

    def get_int(self, key: str) -> int:
        try:
            return int(self.get(key))
        except (ValueError, TypeError):
            meta = SETTINGS_LOOKUP.get(key)
            return meta[2] if meta else 0

    def get_float(self, key: str) -> float:
        try:
            return float(self.get(key))
        except (ValueError, TypeError):
            meta = SETTINGS_LOOKUP.get(key)
            return meta[2] if meta else 0.0

    def set_value(self, key: str, value: str):
        """设置一个配置值。"""
        self.settings[key] = value
        if "." in key:
            parts = key.split(".", 1)
            struct_name, field = parts[0], parts[1]
            if struct_name not in self.structs:
                self.structs[struct_name] = {}
            self.structs[struct_name][field] = value

    def save(self, path: Optional[str] = None):
        """将设置文件写回，保留注释和结构。"""
        save_path = path or self.path
        if not save_path:
            raise ValueError("未指定保存路径")

        output_lines = self._rebuild_lines()
        with open(save_path, "w", encoding="utf-8") as f:
            f.writelines(output_lines)

    def _rebuild_lines(self) -> list[str]:
        """从解析树和当前值重建设置文件。"""
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
# GUI 应用程序
# ──────────────────────────────────────────────────────────────────────

class ColorButton(tk.Frame):
    """显示颜色并点击打开颜色选择器的按钮。"""

    def __init__(self, parent, color_str: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.color_str = color_str
        self._display_color = self._parse_display_color(color_str)

        self.swatch = tk.Canvas(self, width=28, height=28, bd=1, relief="raised",
                                highlightthickness=0)
        self.swatch.pack(side="left", padx=(0, 6))
        self._draw_swatch()

        self.label = tk.Label(self, text=color_str or "（默认）", font=("", 11))
        self.label.pack(side="left")

        self.btn = tk.Button(self, text="选择...", width=6, font=("", 10),
                             command=self._pick_color)
        self.btn.pack(side="left", padx=4)

        self.clear_btn = tk.Button(self, text="清除", width=4, font=("", 10),
                                   command=self._clear_color)
        self.clear_btn.pack(side="left")

        self.swatch.bind("<Button-1>", lambda e: self._pick_color())

    def _parse_display_color(self, s: str) -> str:
        """将 SumatraPDF 颜色转换为 tkinter 颜色。"""
        if not s:
            return ""
        s = s.lstrip("#")
        if len(s) == 6:
            return f"#{s}"
        elif len(s) == 8:
            # aarrggbb -> rrggbb（显示时忽略 alpha）
            return f"#{s[2:]}"
        return f"#{s}" if s else ""

    def _draw_swatch(self):
        self.swatch.delete("all")
        if self._display_color:
            try:
                self.swatch.create_rectangle(0, 0, 28, 28, fill=self._display_color, outline="#888")
            except tk.TclError:
                self.swatch.create_rectangle(0, 0, 28, 28, fill="#cccccc", outline="#888")
        else:
            self.swatch.create_rectangle(0, 0, 28, 28, fill="#cccccc", outline="#888",
                                         stipple="gray50")

    def _pick_color(self):
        initial = self._display_color or "#ffffff"
        result = colorchooser.askcolor(initialcolor=initial, title="选择颜色")
        if result and result[1]:
            hex_color = result[1]  # #rrggbb
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


class SettingsEditor(tk.Tk):
    """主应用程序窗口。"""

    def __init__(self, settings_path: Optional[str] = None):
        super().__init__()

        self.title("SumatraPDF 高级设置编辑器")
        self.geometry("1060x780")
        self.minsize(900, 650)

        # 全局 ttk 样式 - 统一字体大小
        style = ttk.Style()
        style.configure(".", font=("", 10))
        style.configure("TLabel", font=("", 10))
        style.configure("TButton", font=("", 10))
        style.configure("TCheckbutton", font=("", 10))
        style.configure("TCombobox", font=("", 10))
        style.configure("TEntry", font=("", 10))

        # 设置数据
        self.settings_file = SettingsFile()
        self.widgets: dict[str, Any] = {}  # 键 -> 控件
        self.current_category = None

        # 尝试加载设置
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
            self.title(f"SumatraPDF 高级设置编辑器 - {path}")
        except Exception as e:
            messagebox.showerror("错误", f"加载设置文件失败:\n{e}")

    def _build_ui(self):
        # 菜单栏
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="打开(O)...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="保存(S)", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="另存为(A)...", command=self._save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="恢复默认值", command=self._reset_defaults)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self._show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.config(menu=menubar)

        # 快捷键
        self.bind("<Control-o>", lambda e: self._open_file())
        self.bind("<Control-s>", lambda e: self._save_file())

        # 主布局: 侧边栏 + 内容区
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # 分类侧边栏
        sidebar = ttk.Frame(main_frame, width=220)
        sidebar.pack(side="left", fill="y", padx=(0, 6))

        ttk.Label(sidebar, text="设置分类", font=("", 13, "bold")).pack(pady=(0, 6))

        self.category_listbox = tk.Listbox(sidebar, font=("", 11), activestyle="none",
                                            exportselection=False,
                                            selectbackground="#0078d4",
                                            selectforeground="white")
        self.category_listbox.pack(fill="both", expand=True)
        for cat in CATEGORIES:
            self.category_listbox.insert("end", f"  {cat}")
        self.category_listbox.bind("<<ListboxSelect>>", self._on_category_select)

        # 内容区（带滚动条）
        content_outer = ttk.Frame(main_frame)
        content_outer.pack(side="left", fill="both", expand=True)

        # 顶部文件路径栏
        top_bar = ttk.Frame(content_outer)
        top_bar.pack(fill="x", pady=(0, 4))

        self.path_var = tk.StringVar(value=self.settings_file.path or "（未加载文件）")
        ttk.Label(top_bar, text="文件:", font=("", 10)).pack(side="left")
        ttk.Label(top_bar, textvariable=self.path_var, foreground="#333", font=("", 10)).pack(
            side="left", padx=4, fill="x", expand=True)

        btn_frame = ttk.Frame(top_bar)
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="打开", command=self._open_file, width=6).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="保存", command=self._save_file, width=6).pack(side="left", padx=2)

        # 可滚动的内容区
        canvas_frame = ttk.Frame(content_outer)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, padding=(12, 4))

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 鼠标滚轮滚动（仅在鼠标位于内容区时生效）
        def _on_mousewheel(event):
            widget = self.winfo_containing(event.x_root, event.y_root)
            if widget and (widget == self.canvas or widget.master == self.canvas
                           or str(widget).startswith(str(self.scrollable_frame))):
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.bind("<MouseWheel>", _on_mousewheel)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w",
                               font=("", 10))
        status_bar.pack(fill="x", side="bottom")

        # 选中第一个分类
        self.category_listbox.selection_set(0)
        self._show_category(CATEGORIES[0])

    def _on_category_select(self, event):
        sel = self.category_listbox.curselection()
        if sel:
            idx = sel[0]
            cat = CATEGORIES[idx]
            self._show_category(cat)

    def _show_category(self, category: str):
        """显示所选分类的设置项。"""
        # 清除当前内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.widgets.clear()

        self.current_category = category

        # 标题
        ttk.Label(self.scrollable_frame, text=category, font=("", 16, "bold")).pack(
            pady=(10, 14), anchor="w")

        # 获取此分类的设置项
        cat_settings = [s for s in SETTINGS_META if s[4] == category]

        if not cat_settings:
            ttk.Label(self.scrollable_frame, text="（此分类没有可编辑的设置项）",
                      foreground="#666", font=("", 11)).pack(pady=20)
            return

        # 构建设置项列表
        for meta in cat_settings:
            key, stype, default, desc, cat, options = meta
            self._add_setting_row(key, stype, default, desc, options)

    def _add_setting_row(self, key: str, stype: str, default: Any, desc: str, options):
        """在当前分类视图中添加单个设置行。"""
        current = self.settings_file.get(key)

        # 设置项框架
        row_frame = ttk.Frame(self.scrollable_frame, padding=(8, 6))
        row_frame.pack(fill="x", padx=4, pady=4)

        # 描述标签
        desc_label = ttk.Label(row_frame, text=desc, font=("", 11), foreground="#222",
                               wraplength=700)
        desc_label.pack(anchor="w")

        # 配置键标签
        key_label = ttk.Label(row_frame, text=key, font=("Consolas", 10), foreground="#555")
        key_label.pack(anchor="w", pady=(0, 4))

        # 控件框架
        widget_frame = ttk.Frame(row_frame)
        widget_frame.pack(fill="x", pady=(0, 8))

        if stype == "bool":
            var = tk.BooleanVar(value=self.settings_file.get_bool(key))
            cb = ttk.Checkbutton(widget_frame, text="启用", variable=var)
            cb.pack(side="left")
            self.widgets[key] = ("bool", var)

        elif stype == "int":
            var = tk.StringVar(value=current if current else str(default))
            entry = ttk.Entry(widget_frame, textvariable=var, width=15, font=("", 11))
            entry.pack(side="left")
            self.widgets[key] = ("str", var)

        elif stype == "float":
            var = tk.StringVar(value=current if current else str(default))
            entry = ttk.Entry(widget_frame, textvariable=var, width=15, font=("", 11))
            entry.pack(side="left")
            self.widgets[key] = ("str", var)

        elif stype == "str":
            var = tk.StringVar(value=current)
            entry = ttk.Entry(widget_frame, textvariable=var, width=50, font=("", 11))
            entry.pack(side="left", fill="x", expand=True)
            self.widgets[key] = ("str", var)

        elif stype == "color":
            color_btn = ColorButton(widget_frame, color_str=current)
            color_btn.pack(side="left")
            self.widgets[key] = ("color", color_btn)

        elif stype == "choice":
            var = tk.StringVar(value=current if current else str(default))
            combo = ttk.Combobox(widget_frame, textvariable=var, values=options,
                                 state="readonly", width=25, font=("", 11))
            combo.pack(side="left")
            self.widgets[key] = ("str", var)

        elif stype == "compact":
            var = tk.StringVar(value=current if current else str(default))
            entry = ttk.Entry(widget_frame, textvariable=var, width=30, font=("", 11))
            entry.pack(side="left")
            ttk.Label(widget_frame, text="（空格分隔的多个值）",
                      foreground="#666", font=("", 10)).pack(side="left", padx=8)
            self.widgets[key] = ("str", var)

        # 分隔线
        ttk.Separator(self.scrollable_frame, orient="horizontal").pack(fill="x", padx=8, pady=(0, 2))

    def _collect_values(self):
        """从控件收集所有值写回设置文件。"""
        for key, (wtype, widget) in self.widgets.items():
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
            if self.current_category:
                self._show_category(self.current_category)

    def _save_file(self):
        self._collect_values()
        try:
            self.settings_file.save()
            self.status_var.set(f"已保存到 {self.settings_file.path}")
            messagebox.showinfo("保存成功",
                                f"设置已保存。\n\n"
                                f"部分更改可能需要重启 SumatraPDF 才能生效。")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败:\n{e}")

    def _save_as_file(self):
        self._collect_values()
        path = filedialog.asksaveasfilename(
            title="另存为",
            defaultextension=".txt",
            filetypes=[("设置文件", "*.txt"), ("所有文件", "*.*")],
            initialfile="SumatraPDF-settings.txt"
        )
        if path:
            try:
                self.settings_file.save(path)
                self.settings_file.path = path
                self.path_var.set(path)
                self.status_var.set(f"已保存到 {path}")
                messagebox.showinfo("保存成功", "设置已保存。")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败:\n{e}")

    def _reset_defaults(self):
        if not messagebox.askyesno("恢复默认值",
                                    "这将把当前分类的所有设置恢复为默认值。\n是否继续？"):
            return

        for meta in SETTINGS_META:
            key, stype, default, desc, cat, options = meta
            if cat == self.current_category:
                self.settings_file.set_value(key, str(default) if default is not None else "")

        # 刷新
        self._show_category(self.current_category)
        self.status_var.set(f"已将 {self.current_category} 恢复为默认值")

    def _show_about(self):
        messagebox.showinfo(
            "关于",
            "SumatraPDF 高级设置编辑器 v1.0\n\n"
            "用于可视化编辑 SumatraPDF 高级设置的 GUI 工具。\n\n"
            "基于官方设置文档:\n"
            "https://www.sumatrapdfreader.org/settings/settings3-6\n\n"
            "提示: 保存文件后更改生效。\n"
            "部分设置需要重启 SumatraPDF。"
        )

    def _ask_for_file(self):
        """当自动检测失败时提示用户定位设置文件。"""
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
            # 创建新的空设置文件
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
                if self.current_category:
                    self._show_category(self.current_category)


# ──────────────────────────────────────────────────────────────────────
# 入口点
# ──────────────────────────────────────────────────────────────────────

def main():
    settings_path = sys.argv[1] if len(sys.argv) > 1 else None
    app = SettingsEditor(settings_path)
    app.mainloop()


if __name__ == "__main__":
    main()
