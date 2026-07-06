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
    "自定义主题",
    "高级选项",
]

# 每条: (配置键, 类型, 默认值, 中文说明, 分类, 选项)
# 类型: "bool", "int", "float", "str", "color", "choice", "compact"

# ──────────────────────────────────────────────────────────────────────
# 命令数据库: (命令ID, 默认快捷键, 中文说明)
# ──────────────────────────────────────────────────────────────────────
COMMANDS_DB = [
    # 文件
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
    ("CmdDuplicateInNewTab", "", "在新标签打开"),
    ("CmdReopenLastClosedFile", "Shift+Ctrl+T", "恢复上次关闭的"),
    ("CmdExit", "Ctrl+Q", "退出"),
    ("CmdSelectAll", "Ctrl+A", "全选"),
    ("CmdCopySelection", "Ctrl+C", "复制选中"),
    ("CmdCommandPalette", "Ctrl+K", "命令面板"),
    ("CmdShowInFolder", "", "在资源管理器中显示"),
    ("CmdDeleteFile", "", "删除文件"),
    # 搜索
    ("CmdFindFirst", "Ctrl+F", "查找"),
    ("CmdFindNext", "F3", "查找下一个"),
    ("CmdFindPrev", "Shift+F3", "查找上一个"),
    ("CmdFindNextSel", "Ctrl+F3", "查找选中文字下一个"),
    ("CmdFindPrevSel", "Shift+Ctrl+F3", "查找选中文字上一个"),
    # 视图
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
    ("CmdToggleBookmarks", "F12", "显示/隐藏书签"),
    ("CmdToggleTableOfContents", "", "显示/隐藏目录"),
    ("CmdToggleScrollbars", "", "显示/隐藏滚动条"),
    ("CmdTogglePageInfo", "Shift+I", "显示/隐藏页码"),
    ("CmdSelectNextTheme", "", "切换下一个主题"),
    # 导航
    ("CmdGoToNextPage", "N", "下一页"),
    ("CmdGoToPrevPage", "P", "上一页"),
    ("CmdGoToFirstPage", "Home", "第一页"),
    ("CmdGoToLastPage", "End", "最后一页"),
    ("CmdGoToPage", "G", "跳转到页"),
    ("CmdScrollUp", "K", "向上滚动"),
    ("CmdScrollDown", "J", "向下滚动"),
    ("CmdScrollLeft", "H", "向左滚动"),
    ("CmdScrollRight", "L", "向右滚动"),
    ("CmdScrollUpPage", "PageUp", "向上翻页"),
    ("CmdScrollDownPage", "PageDown", "向下翻页"),
    ("CmdNavigateBack", "Alt+Left", "后退"),
    ("CmdNavigateForward", "Alt+Right", "前进"),
    ("CmdOpenNextFileInFolder", "Shift+Ctrl+Right", "打开下一个文件"),
    ("CmdOpenPrevFileInFolder", "Shift+Ctrl+Left", "打开上一个文件"),
    # 标签页
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
    # 缩放
    ("CmdZoomIn", "Ctrl+Add", "放大"),
    ("CmdZoomOut", "Ctrl+Subtract", "缩小"),
    ("CmdZoomFitPage", "Ctrl+0", "适合页面"),
    ("CmdZoomFitWidth", "Ctrl+2", "适合宽度"),
    ("CmdZoomFitContent", "Ctrl+3", "适合内容"),
    ("CmdZoomActualSize", "Ctrl+1", "实际大小"),
    ("CmdZoomCustom", "Ctrl+Y", "自定义缩放"),
    ("CmdToggleZoom", "Z", "切换缩放"),
    # 收藏夹
    ("CmdFavoriteAdd", "Ctrl+B", "添加收藏"),
    ("CmdFavoriteDel", "", "删除收藏"),
    ("CmdFavoriteToggle", "", "显示/隐藏收藏夹"),
    # 批注
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
    ("CmdCreateAnnotPolyLine", "", "折线批注"),
    ("CmdCreateAnnotCaret", "", "插入符批注"),
    ("CmdCreateAnnotRedact", "", "遮盖批注"),
    ("CmdDeleteAnnotation", "Delete", "删除批注"),
    ("CmdSaveAnnotations", "Shift+Ctrl+S", "保存批注到PDF"),
    # 外部应用
    ("CmdTranslateSelectionWithGoogle", "", "Google 翻译选中文字"),
    ("CmdTranslateSelectionWithDeepL", "", "DeepL 翻译选中文字"),
    ("CmdSearchSelectionWithGoogle", "", "Google 搜索选中文字"),
    ("CmdSearchSelectionWithBing", "", "Bing 搜索选中文字"),
    ("CmdSearchSelectionWithWikipedia", "", "Wikipedia 搜索"),
    ("CmdSearchSelectionWithGoogleScholar", "", "Google 学术搜索"),
    ("CmdOpenWithAcrobat", "", "用 Acrobat 打开"),
    ("CmdOpenWithFoxIt", "", "用 Foxit 打开"),
    ("CmdSendByEmail", "", "通过邮件发送"),
    # 帮助
    ("CmdHelpOpenManual", "F1", "打开手册"),
    ("CmdOptions", "", "选项"),
    ("CmdAdvancedOptions", "", "高级设置"),
    ("CmdCheckUpdate", "", "检查更新"),
    ("CmdChangeLanguage", "", "更改语言"),
]

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
                    elif sl == "[":
                        # 数组元素开始
                        depth += 1
                        i += 1
                        elem_items = []
                        elem_depth = 1
                        while i < len(lines) and elem_depth > 0:
                            elem_sl = lines[i].rstrip("\r\n").strip()
                            if elem_sl == "]":
                                elem_depth -= 1
                                if elem_depth == 0:
                                    i += 1
                                    break
                            elif elem_sl == "[":
                                elem_depth += 1
                                i += 1
                                continue
                            if not elem_sl or elem_sl.startswith(";"):
                                i += 1
                                continue
                            elem_kv = re.match(r'^(\w+)\s*=\s*(.*)', elem_sl)
                            if elem_kv:
                                ek, ev = elem_kv.group(1), elem_kv.group(2).strip()
                                elem_items.append(("kv", ek, ev))
                            i += 1
                        items.append(("struct", "", elem_items))
                        depth -= 1
                        continue
                    elif sl.startswith("["):
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

    def get_shortcuts(self) -> dict[str, dict[str, str]]:
        """从解析树中提取 Shortcuts 数组，返回 {cmd_id: {Key:, Name:, ToolbarText:}}"""
        result = {}
        for entry in self._parse_tree:
            if entry[0] == "struct" and entry[1] == "Shortcuts":
                for item in entry[2]:
                    if item[0] == "struct" and item[1] == "":
                        # 这是一个快捷键条目
                        cmd_id = ""
                        key_val = ""
                        name_val = ""
                        toolbar_val = ""
                        for sub in item[2]:
                            if sub[0] == "kv":
                                if sub[1] == "Cmd":
                                    cmd_id = sub[2]
                                elif sub[1] == "Key":
                                    key_val = sub[2]
                                elif sub[1] == "Name":
                                    name_val = sub[2]
                                elif sub[1] == "ToolbarText":
                                    toolbar_val = sub[2]
                        if cmd_id:
                            # 只取纯命令名（去掉参数部分如 #00ff00 openedit）
                            pure_cmd = cmd_id.split()[0] if cmd_id else ""
                            result[pure_cmd] = {
                                "Cmd": cmd_id,
                                "Key": key_val,
                                "Name": name_val,
                                "ToolbarText": toolbar_val,
                            }
        return result

    def set_shortcuts(self, shortcuts: list[dict[str, str]]):
        """设置 Shortcuts 数组。shortcuts 是 [{Cmd:, Key:, Name:, ToolbarText:}] 列表。"""
        # 找到并替换 Shortcuts 在解析树中的位置
        new_items = []
        for sc in shortcuts:
            if not sc.get("Key", "").strip():
                continue  # 没有快捷键的跳过
            entry_items = [("kv", "Cmd", sc["Cmd"])]
            entry_items.append(("kv", "Key", sc["Key"]))
            if sc.get("Name"):
                entry_items.append(("kv", "Name", sc["Name"]))
            if sc.get("ToolbarText"):
                entry_items.append(("kv", "ToolbarText", sc["ToolbarText"]))
            new_items.append(("struct", "", entry_items))

        # 在解析树中找到 Shortcuts 并替换
        for i, entry in enumerate(self._parse_tree):
            if entry[0] == "struct" and entry[1] == "Shortcuts":
                self._parse_tree[i] = ("struct", "Shortcuts", new_items)
                return

        # 如果没有 Shortcuts，添加到末尾（在注释行之前）
        insert_idx = len(self._parse_tree)
        for i in range(len(self._parse_tree) - 1, -1, -1):
            if self._parse_tree[i][0] == "comment":
                insert_idx = i
            else:
                break
        self._parse_tree.insert(insert_idx, ("struct", "Shortcuts", new_items))

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
                # 数组类型特殊处理：直接从 parse tree 写出值
                if name in ("Shortcuts", "ExternalViewers", "SelectionHandlers",
                            "Themes", "TabGroups"):
                    lines.append(f"{name} [\n")
                    for item in items:
                        if item[0] == "struct" and item[1] == "":
                            # 数组元素
                            lines.append("  [\n")
                            for si in item[2]:
                                if si[0] == "kv":
                                    _, sk, sv = si
                                    lines.append(f"    {sk} = {sv}\n")
                            lines.append("  ]\n")
                    lines.append("]\n")
                else:
                    lines.append(f"{name} [\n")
                    for item in items:
                        if item[0] == "kv":
                            _, key, _ = item
                            full_key = f"{name}.{key}"
                            val = self.settings.get(full_key, "")
                            lines.append(f"    {key} = {val}\n")
                        elif item[0] == "struct":
                            _, sub_name, sub_items = item
                            if sub_name:
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

        # 设置窗口图标（齿轮）
        self._set_icon()

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

    def _set_icon(self):
        """用代码绘制一个齿轮图标作为窗口图标。"""
        import math

        size = 32
        pixels = []
        cx, cy = size // 2, size // 2
        r_outer = 13
        r_inner = 8
        r_center = 5
        teeth = 8

        for y in range(size):
            row = []
            for x in range(size):
                dx, dy = x - cx, y - cy
                dist = (dx * dx + dy * dy) ** 0.5
                angle = math.atan2(dy, dx)

                # 齿轮齿的角度
                tooth_angle = (angle + math.pi) / (2 * math.pi) * teeth
                tooth_frac = tooth_angle - int(tooth_angle)
                is_tooth = 0.25 < tooth_frac < 0.75
                r_limit = r_outer if is_tooth else r_inner

                if r_center < dist < r_limit:
                    row.extend([59, 130, 246])  # 蓝色齿轮
                elif dist <= r_center and dist > 2:
                    row.extend([30, 58, 138])   # 深蓝中心
                elif dist <= 2:
                    row.extend([255, 255, 255]) # 白色中心点
                else:
                    row.extend([248, 249, 250]) # 背景色
            pixels.append(row)

        # 构建 PPM 格式然后转为 PhotoImage
        ppm_header = f"P6 {size} {size} 255\n".encode()
        ppm_data = ppm_header
        for row in pixels:
            for r, g, b in row:
                ppm_data += bytes([r, g, b])

        try:
            self._icon_photo = tk.PhotoImage(data=ppm_data)
            # PhotoImage 不直接支持 PPM data，用 base64 方式
            raise Exception("use base64")
        except Exception:
            # 用 base64 编码的 GIF
            import base64
            # 生成一个简单的 GIF 图标
            gif_data = self._create_gear_gif(size, pixels)
            if gif_data:
                self._icon_photo = tk.PhotoImage(data=gif_data)
                self.iconphoto(False, self._icon_photo)

    def _create_gear_gif(self, size, pixels):
        """生成齿轮图标的 GIF base64 数据。"""
        import base64, io, struct

        # 收集所有使用的颜色（pixels 是 [[r,g,b,r,g,b,...], ...] 格式）
        colors = set()
        for row in pixels:
            for i in range(0, len(row), 3):
                colors.add((row[i], row[i + 1], row[i + 2]))

        color_list = list(colors)
        color_map = {c: i for i, c in enumerate(color_list)}

        # 找到最小的 2 的幂作为颜色表大小
        n_colors = 2
        while n_colors < len(color_list):
            n_colors *= 2
        if n_colors > 256:
            return None

        # 补齐颜色表
        while len(color_list) < n_colors:
            color_list.append((0, 0, 0))

        # 构建 GIF
        buf = io.BytesIO()

        # GIF89a header
        buf.write(b'GIF89a')
        buf.write(struct.pack('<HH', size, size))  # 宽高
        buf.write(b'\x87')  # GCTF=1, 颜色分辨率=7
        buf.write(b'\x00')  # 背景色索引
        buf.write(b'\x00')  # 像素宽高比

        # 全局颜色表
        for r, g, b in color_list[:n_colors]:
            buf.write(bytes([r, g, b]))

        # 图像描述符
        buf.write(b'\x2c')  # 图像分隔符
        buf.write(struct.pack('<HH', 0, 0))  # 左上角
        buf.write(struct.pack('<HH', size, size))  # 宽高
        buf.write(b'\x00')  # 无局部颜色表

        # LZW 压缩
        min_code_size = 8
        buf.write(bytes([min_code_size]))

        # 简单的未压缩数据（用 GIF 的 LZW 最小编码大小=8 来简化）
        # 实际上用未压缩方式写
        pixels_flat = []
        for row in pixels:
            for i in range(0, len(row), 3):
                idx = color_map.get((row[i], row[i + 1], row[i + 2]), 0)
                pixels_flat.append(idx)

        # 使用 zlib 的 deflate 来模拟 LZW（GIF 的 LZW 类似）
        # 但 GIF LZW 不等于 zlib，所以我们用一个简单的实现
        clear_code = 1 << min_code_size
        eoi_code = clear_code + 1

        # 简单的 GIF LZW 编码
        code_size = min_code_size + 1
        next_code = eoi_code + 1
        table = {}
        for i in range(clear_code):
            table[(i,)] = i

        bit_buf = 0
        bit_count = 0
        out_bytes = bytearray()

        def write_code(code):
            nonlocal bit_buf, bit_count
            bit_buf |= code << bit_count
            bit_count += code_size
            while bit_count >= 8:
                out_bytes.append(bit_buf & 0xff)
                bit_buf >>= 8
                bit_count -= 8

        write_code(clear_code)

        w = ()
        for pixel in pixels_flat:
            w_plus = w + (pixel,)
            if w_plus in table:
                w = w_plus
            else:
                write_code(table[w])
                if next_code < 4096:
                    table[w_plus] = next_code
                    next_code += 1
                    if next_code > (1 << code_size) and code_size < 12:
                        code_size += 1
                else:
                    write_code(clear_code)
                    table = {}
                    for i in range(clear_code):
                        table[(i,)] = i
                    next_code = eoi_code + 1
                    code_size = min_code_size + 1
                w = (pixel,)

        if w:
            write_code(table[w])

        write_code(eoi_code)

        if bit_count > 0:
            out_bytes.append(bit_buf & 0xff)

        # 写入子数据块
        idx = 0
        while idx < len(out_bytes):
            chunk_size = min(255, len(out_bytes) - idx)
            buf.write(bytes([chunk_size]))
            buf.write(out_bytes[idx:idx + chunk_size])
            idx += chunk_size

        buf.write(b'\x00')  # 块终止符
        buf.write(b'\x3b')  # GIF 结束符

        return base64.b64encode(buf.getvalue()).decode('ascii')

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
                "自定义主题": "themes",
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
        """为数组类型的分类构建可视化编辑页面。"""

        if page_type == "shortcuts":
            self._build_shortcuts_editor(page)
        elif page_type == "external":
            self._build_external_viewers_editor(page)
        elif page_type == "selection":
            self._build_selection_handlers_editor(page)
        elif page_type == "themes":
            self._build_themes_editor(page)

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

    def _build_external_viewers_editor(self, page):
        """构建外部查看器可视化编辑器。"""
        # 提示
        hint_frame = tk.Frame(page, bg=Colors.ACCENT_LIGHT)
        hint_frame.pack(fill="x", padx=28, pady=(0, 12))
        tk.Label(hint_frame, text=(
            "💡 配置外部查看器后，可以在文件菜单中直接用其他程序打开当前文档。\n"
            "CommandLine 中 %1 代表文件路径，%p 代表页码，%d 代表文件所在目录。"
        ), font=Fonts.SMALL, bg=Colors.ACCENT_LIGHT, fg=Colors.ACCENT,
            justify="left", padx=16, pady=10).pack(anchor="w")

        # 读取现有的
        existing_viewers = self._get_array_entries("ExternalViewers",
                                                    ["CommandLine", "Name", "Filter", "Key"])

        self._viewer_widgets = []

        # 预设模板
        presets = [
            ("Adobe Acrobat", '"C:\\Program Files\\Adobe\\Acrobat DC\\Acrobat\\Acrobat.exe" "%1"', "*.pdf"),
            ("Foxit Reader", '"C:\\Program Files\\Foxit Software\\Foxit Reader\\FoxitReader.exe" "%1"', "*.pdf"),
            ("PDF-XChange", '"C:\\Program Files\\Tracker Software\\PDF Editor\\PDFXEdit.exe" "%1"', "*.pdf"),
        ]

        # 预设按钮
        preset_frame = tk.Frame(page, bg=Colors.BG)
        preset_frame.pack(fill="x", padx=28, pady=(0, 8))
        tk.Label(preset_frame, text="快速添加：", font=Fonts.SMALL,
                 bg=Colors.BG, fg=Colors.TEXT_SECONDARY).pack(side="left")
        for name, cmd, filt in presets:
            btn = tk.Button(preset_frame, text=name, font=Fonts.SMALL,
                            bg=Colors.HOVER, fg=Colors.TEXT, bd=0, padx=8, pady=2,
                            cursor="hand2",
                            command=lambda n=name, c=cmd, f=filt: self._add_viewer(n, c, f))
            btn.pack(side="left", padx=4)

        # 添加自定义按钮
        add_btn = tk.Button(preset_frame, text="+ 自定义", font=Fonts.SMALL,
                            bg=Colors.ACCENT, fg="white", bd=0, padx=8, pady=2,
                            cursor="hand2",
                            command=lambda: self._add_viewer("", "", "*.pdf"))
        add_btn.pack(side="left", padx=4)

        # 列表容器
        self._viewer_list_frame = tk.Frame(page, bg=Colors.BG)
        self._viewer_list_frame.pack(fill="x", padx=28)

        # 显示已有的
        for viewer in existing_viewers:
            self._add_viewer_card(viewer.get("CommandLine", ""),
                                  viewer.get("Name", ""),
                                  viewer.get("Filter", ""),
                                  viewer.get("Key", ""))

        # 如果没有，显示一个空的
        if not existing_viewers:
            self._add_viewer_card("", "", "*.pdf", "")

    def _add_viewer(self, name, cmd, filt):
        self._add_viewer_card(cmd, name, filt, "")

    def _add_viewer_card(self, cmd, name, filt, key):
        """添加一个外部查看器卡片。"""
        card = tk.Frame(self._viewer_list_frame, bg=Colors.CARD_BG,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 8))
        inner = tk.Frame(card, bg=Colors.CARD_BG)
        inner.pack(fill="x", padx=16, pady=12)

        # 删除按钮
        del_btn = tk.Button(inner, text="✕", font=Fonts.SMALL, bg=Colors.CARD_BG,
                            fg=Colors.TEXT_MUTED, bd=0, cursor="hand2",
                            command=lambda: card.destroy())
        del_btn.pack(anchor="e")

        fields = {}

        row1 = tk.Frame(inner, bg=Colors.CARD_BG)
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="命令行", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=10, anchor="w").pack(side="left")
        var_cmd = tk.StringVar(value=cmd)
        e_cmd = self._make_entry(row1, var_cmd, width=60)
        e_cmd.pack(side="left", fill="x", expand=True)
        fields["CommandLine"] = var_cmd

        row2 = tk.Frame(inner, bg=Colors.CARD_BG)
        row2.pack(fill="x", pady=2)
        tk.Label(row2, text="显示名称", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=10, anchor="w").pack(side="left")
        var_name = tk.StringVar(value=name)
        self._make_entry(row2, var_name, width=30)
        fields["Name"] = var_name

        row3 = tk.Frame(inner, bg=Colors.CARD_BG)
        row3.pack(fill="x", pady=2)
        tk.Label(row3, text="文件过滤", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=10, anchor="w").pack(side="left")
        var_filter = tk.StringVar(value=filt)
        self._make_entry(row3, var_filter, width=30)
        fields["Filter"] = var_filter
        tk.Label(row3, text="如 *.pdf 或 *.pdf;*.xps", font=Fonts.SMALL_MUTED,
                 bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED).pack(side="left", padx=8)

        row4 = tk.Frame(inner, bg=Colors.CARD_BG)
        row4.pack(fill="x", pady=2)
        tk.Label(row4, text="快捷键", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=10, anchor="w").pack(side="left")
        var_key = tk.StringVar(value=key)
        self._make_entry(row4, var_key, width=20)
        fields["Key"] = var_key
        tk.Label(row4, text="如 Alt+7", font=Fonts.SMALL_MUTED,
                 bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED).pack(side="left", padx=8)

        self._viewer_widgets.append((card, fields))

    def _build_selection_handlers_editor(self, page):
        """构建选中文字处理可视化编辑器。"""
        hint_frame = tk.Frame(page, bg=Colors.ACCENT_LIGHT)
        hint_frame.pack(fill="x", padx=28, pady=(0, 12))
        tk.Label(hint_frame, text=(
            "💡 配置后，选中文字右键即可看到菜单项。URL 中 ${selection} 会被替换为选中的文字。"
        ), font=Fonts.SMALL, bg=Colors.ACCENT_LIGHT, fg=Colors.ACCENT,
            justify="left", padx=16, pady=10).pack(anchor="w")

        existing = self._get_array_entries("SelectionHandlers", ["URL", "Name", "Key"])

        self._selection_widgets = []

        # 预设
        presets = [
            ("Google 翻译", "https://translate.google.com/?sl=auto&tl=zh-CN&text=${selection}"),
            ("DeepL 翻译", "https://www.deepl.com/translator#auto/zh/${selection}"),
            ("Google 搜索", "https://www.google.com/search?q=${selection}"),
            ("百度搜索", "https://www.baidu.com/s?wd=${selection}"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/Special:Search?search=${selection}"),
        ]

        preset_frame = tk.Frame(page, bg=Colors.BG)
        preset_frame.pack(fill="x", padx=28, pady=(0, 8))
        tk.Label(preset_frame, text="快速添加：", font=Fonts.SMALL,
                 bg=Colors.BG, fg=Colors.TEXT_SECONDARY).pack(side="left")
        for name, url in presets:
            btn = tk.Button(preset_frame, text=name, font=Fonts.SMALL,
                            bg=Colors.HOVER, fg=Colors.TEXT, bd=0, padx=8, pady=2,
                            cursor="hand2",
                            command=lambda n=name, u=url: self._add_selection_handler(n, u))
            btn.pack(side="left", padx=4)

        add_btn = tk.Button(preset_frame, text="+ 自定义", font=Fonts.SMALL,
                            bg=Colors.ACCENT, fg="white", bd=0, padx=8, pady=2,
                            cursor="hand2",
                            command=lambda: self._add_selection_handler("", ""))
        add_btn.pack(side="left", padx=4)

        self._selection_list_frame = tk.Frame(page, bg=Colors.BG)
        self._selection_list_frame.pack(fill="x", padx=28)

        for handler in existing:
            self._add_selection_card(handler.get("URL", ""),
                                     handler.get("Name", ""),
                                     handler.get("Key", ""))

        if not existing:
            self._add_selection_card("", "", "")

    def _add_selection_handler(self, name, url):
        self._add_selection_card(url, name, "")

    def _add_selection_card(self, url, name, key):
        """添加一个选中文字处理卡片。"""
        card = tk.Frame(self._selection_list_frame, bg=Colors.CARD_BG,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 8))
        inner = tk.Frame(card, bg=Colors.CARD_BG)
        inner.pack(fill="x", padx=16, pady=12)

        del_btn = tk.Button(inner, text="✕", font=Fonts.SMALL, bg=Colors.CARD_BG,
                            fg=Colors.TEXT_MUTED, bd=0, cursor="hand2",
                            command=lambda: card.destroy())
        del_btn.pack(anchor="e")

        fields = {}

        row1 = tk.Frame(inner, bg=Colors.CARD_BG)
        row1.pack(fill="x", pady=2)
        tk.Label(row1, text="显示名称", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=10, anchor="w").pack(side="left")
        var_name = tk.StringVar(value=name)
        self._make_entry(row1, var_name, width=30)
        fields["Name"] = var_name

        row2 = tk.Frame(inner, bg=Colors.CARD_BG)
        row2.pack(fill="x", pady=2)
        tk.Label(row2, text="URL", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=10, anchor="w").pack(side="left")
        var_url = tk.StringVar(value=url)
        e_url = self._make_entry(row2, var_url, width=60)
        e_url.pack(side="left", fill="x", expand=True)
        fields["URL"] = var_url

        row3 = tk.Frame(inner, bg=Colors.CARD_BG)
        row3.pack(fill="x", pady=2)
        tk.Label(row3, text="快捷键", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=10, anchor="w").pack(side="left")
        var_key = tk.StringVar(value=key)
        self._make_entry(row3, var_key, width=20)
        fields["Key"] = var_key

        self._selection_widgets.append((card, fields))

    def _build_themes_editor(self, page):
        """构建自定义主题可视化编辑器。"""
        hint_frame = tk.Frame(page, bg=Colors.ACCENT_LIGHT)
        hint_frame.pack(fill="x", padx=28, pady=(0, 12))
        tk.Label(hint_frame, text=(
            "💡 自定义主题可以在 SumatraPDF 的 设置 → 主题 菜单中选择。\n"
            "ColorizeControls 设为 true 时，Windows 控件（菜单、工具栏等）也会使用主题颜色。"
        ), font=Fonts.SMALL, bg=Colors.ACCENT_LIGHT, fg=Colors.ACCENT,
            justify="left", padx=16, pady=10).pack(anchor="w")

        existing = self._get_array_entries("Themes",
                                            ["Name", "TextColor", "BackgroundColor",
                                             "ControlBackgroundColor", "LinkColor", "ColorizeControls"])

        self._theme_widgets = []

        # 预设主题
        presets = [
            ("Solarized Dark", "#839496", "#002b36", "#073642", "#268bd2"),
            ("Dracula", "#f8f8f2", "#282a36", "#44475a", "#8be9fd"),
            ("Nord", "#d8dee9", "#2e3440", "#3b4252", "#88c0d0"),
            ("One Dark", "#abb2bf", "#282c34", "#21252b", "#61afef"),
            ("Greeny", "#FDD085", "#4F6232", "#1E3304", "#A2E53B"),
        ]

        preset_frame = tk.Frame(page, bg=Colors.BG)
        preset_frame.pack(fill="x", padx=28, pady=(0, 8))
        tk.Label(preset_frame, text="快速添加预设主题：", font=Fonts.SMALL,
                 bg=Colors.BG, fg=Colors.TEXT_SECONDARY).pack(side="left")
        for name, text_c, bg_c, ctrl_c, link_c in presets:
            btn = tk.Button(preset_frame, text=name, font=Fonts.SMALL,
                            bg=Colors.HOVER, fg=Colors.TEXT, bd=0, padx=8, pady=2,
                            cursor="hand2",
                            command=lambda n=name, t=text_c, b=bg_c, c=ctrl_c, l=link_c:
                            self._add_theme_card(n, t, b, c, l, "true"))
            btn.pack(side="left", padx=4)

        add_btn = tk.Button(preset_frame, text="+ 自定义", font=Fonts.SMALL,
                            bg=Colors.ACCENT, fg="white", bd=0, padx=8, pady=2,
                            cursor="hand2",
                            command=lambda: self._add_theme_card("", "", "", "", "", "true"))
        add_btn.pack(side="left", padx=4)

        self._theme_list_frame = tk.Frame(page, bg=Colors.BG)
        self._theme_list_frame.pack(fill="x", padx=28)

        for theme in existing:
            self._add_theme_card(
                theme.get("Name", ""),
                theme.get("TextColor", ""),
                theme.get("BackgroundColor", ""),
                theme.get("ControlBackgroundColor", ""),
                theme.get("LinkColor", ""),
                theme.get("ColorizeControls", "true"),
            )

    def _add_theme_card(self, name, text_c, bg_c, ctrl_c, link_c, colorize):
        """添加一个主题卡片。"""
        card = tk.Frame(self._theme_list_frame, bg=Colors.CARD_BG,
                        highlightbackground=Colors.BORDER, highlightthickness=1)
        card.pack(fill="x", pady=(0, 8))
        inner = tk.Frame(card, bg=Colors.CARD_BG)
        inner.pack(fill="x", padx=16, pady=12)

        del_btn = tk.Button(inner, text="✕", font=Fonts.SMALL, bg=Colors.CARD_BG,
                            fg=Colors.TEXT_MUTED, bd=0, cursor="hand2",
                            command=lambda: card.destroy())
        del_btn.pack(anchor="e")

        fields = {}

        # 主题名
        row0 = tk.Frame(inner, bg=Colors.CARD_BG)
        row0.pack(fill="x", pady=2)
        tk.Label(row0, text="主题名称", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=14, anchor="w").pack(side="left")
        var_name = tk.StringVar(value=name)
        self._make_entry(row0, var_name, width=30)
        fields["Name"] = var_name

        # 颜色行
        color_items = [
            ("文字颜色", "TextColor", text_c),
            ("背景颜色", "BackgroundColor", bg_c),
            ("控件背景", "ControlBackgroundColor", ctrl_c),
            ("链接颜色", "LinkColor", link_c),
        ]

        for label, key, val in color_items:
            row = tk.Frame(inner, bg=Colors.CARD_BG)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, font=Fonts.SMALL, bg=Colors.CARD_BG,
                     fg=Colors.TEXT_SECONDARY, width=14, anchor="w").pack(side="left")
            color_btn = ColorButton(row, color_str=val)
            color_btn.pack(side="left")
            fields[key] = color_btn

        # ColorizeControls
        row_c = tk.Frame(inner, bg=Colors.CARD_BG)
        row_c.pack(fill="x", pady=2)
        tk.Label(row_c, text="着色控件", font=Fonts.SMALL, bg=Colors.CARD_BG,
                 fg=Colors.TEXT_SECONDARY, width=14, anchor="w").pack(side="left")
        var_colorize = tk.BooleanVar(value=colorize.lower() == "true")
        tk.Checkbutton(row_c, text="ColorizeControls（让菜单、工具栏等也使用主题颜色）",
                       variable=var_colorize, font=Fonts.SMALL,
                       bg=Colors.CARD_BG, fg=Colors.TEXT,
                       selectcolor=Colors.CARD_BG).pack(side="left")
        fields["ColorizeControls"] = var_colorize

        # 预览色块
        preview_frame = tk.Frame(inner, bg=Colors.CARD_BG)
        preview_frame.pack(fill="x", pady=(8, 0))

        def _update_preview():
            for w in preview_frame.winfo_children():
                w.destroy()
            bg = fields["BackgroundColor"].get_value() if hasattr(fields["BackgroundColor"], 'get_value') else bg_c
            text = fields["TextColor"].get_value() if hasattr(fields["TextColor"], 'get_value') else text_c
            link = fields["LinkColor"].get_value() if hasattr(fields["LinkColor"], 'get_value') else link_c
            if bg:
                preview = tk.Frame(preview_frame, bg=bg, padx=12, pady=8)
                preview.pack(side="left", padx=4)
                tk.Label(preview, text="示例文字", bg=bg,
                         fg=text or "#000000", font=Fonts.SMALL).pack()
                tk.Label(preview, text="链接样式", bg=bg,
                         fg=link or "#0000ff", font=Fonts.SMALL).pack()

        _update_preview()

        self._theme_widgets.append((card, fields))

    def _get_array_entries(self, array_name, field_names):
        """从解析树中提取数组类型的条目。"""
        result = []
        for entry in self._parse_tree if hasattr(self, '_parse_tree') else []:
            pass
        # 从 settings_file 的解析树中获取
        for entry in self.settings_file._parse_tree:
            if entry[0] == "struct" and entry[1] == array_name:
                for item in entry[2]:
                    if item[0] == "struct" and item[1] == "":
                        entry_dict = {}
                        for sub in item[2]:
                            if sub[0] == "kv":
                                entry_dict[sub[1]] = sub[2]
                        result.append(entry_dict)
        return result

    def _build_shortcuts_editor(self, page):
        """构建快捷键可视化编辑器。"""
        # 读取现有的自定义快捷键
        existing = self.settings_file.get_shortcuts()

        # 构建命令分组
        groups = {}
        for cmd_id, default_key, desc in COMMANDS_DB:
            # 确定分组
            if cmd_id.startswith("CmdOpen") or cmd_id.startswith("CmdSave") or \
               cmd_id.startswith("CmdClose") or cmd_id.startswith("CmdPrint") or \
               cmd_id.startswith("CmdNew") or cmd_id.startswith("CmdExit") or \
               cmd_id in ("CmdReloadDocument", "CmdRenameFile", "CmdReopenLastClosedFile",
                           "CmdDuplicateInNewWindow", "CmdDuplicateInNewTab",
                           "CmdSelectAll", "CmdCopySelection", "CmdCommandPalette",
                           "CmdShowInFolder", "CmdDeleteFile", "CmdProperties"):
                group = "文件"
            elif cmd_id.startswith("CmdFind"):
                group = "搜索"
            elif cmd_id.startswith("CmdToggle") and ("View" in cmd_id or "Fullscreen" in cmd_id
                                                       or "Presentation" in cmd_id or "Toolbar" in cmd_id
                                                       or "MenuBar" in cmd_id or "Manga" in cmd_id
                                                       or "Links" in cmd_id or "Bookmarks" in cmd_id
                                                       or "TableOfContents" in cmd_id or "Scrollbars" in cmd_id
                                                       or "PageInfo" in cmd_id):
                group = "视图"
            elif cmd_id.startswith("CmdSelectNextTheme"):
                group = "视图"
            elif cmd_id.startswith("CmdSingle") or cmd_id.startswith("CmdFacing") or cmd_id.startswith("CmdBook"):
                group = "视图"
            elif cmd_id.startswith("CmdInvert") or cmd_id.startswith("CmdRotate"):
                group = "视图"
            elif cmd_id.startswith("CmdScroll") or cmd_id.startswith("CmdGoTo") or \
                 cmd_id.startswith("CmdNavigate") or cmd_id.startswith("CmdOpenNext") or \
                 cmd_id.startswith("CmdOpenPrev"):
                group = "导航"
            elif "Tab" in cmd_id and cmd_id.startswith("Cmd"):
                group = "标签页"
            elif cmd_id.startswith("CmdZoom"):
                group = "缩放"
            elif cmd_id.startswith("CmdFavorite"):
                group = "收藏夹"
            elif cmd_id.startswith("CmdCreateAnnot") or cmd_id.startswith("CmdDeleteAnnotation") or \
                 cmd_id.startswith("CmdSaveAnnotations") or cmd_id.startswith("CmdEditAnnotations") or \
                 cmd_id.startswith("CmdShowAnnotations") or cmd_id.startswith("CmdHideAnnotations") or \
                 cmd_id.startswith("CmdToggleShowAnnotations"):
                group = "批注"
            elif "Translate" in cmd_id or "Search" in cmd_id or "OpenWith" in cmd_id or \
                 "SendByEmail" in cmd_id:
                group = "外部应用"
            else:
                group = "其他"

            if group not in groups:
                groups[group] = []

            # 获取当前快捷键（用户自定义 > 默认）
            current_key = default_key
            if cmd_id in existing:
                user_key = existing[cmd_id].get("Key", "").strip()
                if user_key:
                    current_key = user_key

            groups[group].append((cmd_id, default_key, current_key, desc))

        # 存储所有输入框变量，用于保存时收集
        self._shortcut_vars: dict[str, tk.StringVar] = {}

        # 提示信息
        hint_frame = tk.Frame(page, bg=Colors.ACCENT_LIGHT)
        hint_frame.pack(fill="x", padx=28, pady=(0, 12))
        tk.Label(hint_frame, text=(
            "💡 修改快捷键后点击「保存」即可生效，无需重启 SumatraPDF。\n"
            "留空表示使用默认快捷键，输入 CmdNone 可禁用该快捷键。"
        ), font=Fonts.SMALL, bg=Colors.ACCENT_LIGHT, fg=Colors.ACCENT,
            justify="left", padx=16, pady=10).pack(anchor="w")

        # 表头
        header_frame = tk.Frame(page, bg=Colors.BG)
        header_frame.pack(fill="x", padx=28, pady=(0, 4))
        tk.Label(header_frame, text="命令", font=Fonts.SMALL_MUTED,
                 bg=Colors.BG, fg=Colors.TEXT_MUTED, width=28, anchor="w").pack(side="left")
        tk.Label(header_frame, text="说明", font=Fonts.SMALL_MUTED,
                 bg=Colors.BG, fg=Colors.TEXT_MUTED, width=20, anchor="w").pack(side="left")
        tk.Label(header_frame, text="默认快捷键", font=Fonts.SMALL_MUTED,
                 bg=Colors.BG, fg=Colors.TEXT_MUTED, width=16, anchor="w").pack(side="left")
        tk.Label(header_frame, text="当前快捷键", font=Fonts.SMALL_MUTED,
                 bg=Colors.BG, fg=Colors.TEXT_MUTED, width=16, anchor="w").pack(side="left")

        # 按分组显示
        group_order = ["文件", "搜索", "视图", "导航", "标签页", "缩放", "收藏夹", "批注", "外部应用", "其他"]
        for group_name in group_order:
            if group_name not in groups:
                continue
            cmds = groups[group_name]

            group_frame = tk.Frame(page, bg=Colors.CARD_BG,
                                   highlightbackground=Colors.BORDER, highlightthickness=1)
            group_frame.pack(fill="x", padx=28, pady=(0, 8))
            group_inner = tk.Frame(group_frame, bg=Colors.CARD_BG)
            group_inner.pack(fill="x", padx=16, pady=10)

            tk.Label(group_inner, text=group_name, font=Fonts.BODY_BOLD,
                     bg=Colors.CARD_BG, fg=Colors.ACCENT).pack(anchor="w", pady=(0, 6))

            for cmd_id, default_key, current_key, desc in cmds:
                row = tk.Frame(group_inner, bg=Colors.CARD_BG)
                row.pack(fill="x", pady=1)

                # 命令 ID
                tk.Label(row, text=cmd_id, font=("Consolas", 9),
                         bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED, width=28, anchor="w").pack(side="left")

                # 说明
                tk.Label(row, text=desc, font=Fonts.SMALL,
                         bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY, width=20, anchor="w").pack(side="left")

                # 默认快捷键
                tk.Label(row, text=default_key if default_key else "—", font=Fonts.SMALL,
                         bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED, width=16, anchor="w").pack(side="left")

                # 当前快捷键（可编辑）
                var = tk.StringVar(value=current_key)
                self._shortcut_vars[cmd_id] = (var, default_key)

                entry_frame = tk.Frame(row, bg=Colors.INPUT_BORDER, padx=1, pady=1)
                entry_frame.pack(side="left")
                entry = tk.Entry(entry_frame, textvariable=var, font=Fonts.SMALL, width=16,
                                 bg=Colors.INPUT_BG, fg=Colors.TEXT, bd=0,
                                 highlightthickness=1, highlightcolor=Colors.INPUT_FOCUS,
                                 highlightbackground=Colors.INPUT_BORDER)
                entry.pack(fill="x", padx=2, pady=2)

                # 如果与默认不同，高亮显示
                if current_key != default_key:
                    entry.configure(fg=Colors.ACCENT)

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

        # 收集快捷键设置
        if hasattr(self, '_shortcut_vars') and self._shortcut_vars:
            shortcuts = []
            for cmd_id, (var, default_key) in self._shortcut_vars.items():
                key_val = var.get().strip()
                if key_val and key_val != default_key:
                    # 用户自定义了快捷键
                    shortcuts.append({"Cmd": cmd_id, "Key": key_val})
                elif key_val == default_key and default_key:
                    # 保持默认（不写入 Shortcuts 数组）
                    pass
            # 如果有任何自定义快捷键，写入
            # 也保留已有的带参数的命令（如 CmdCreateAnnotHighlight #00ff00）
            existing = self.settings_file.get_shortcuts()
            for cmd_id, info in existing.items():
                full_cmd = info.get("Cmd", "")
                if " " in full_cmd:  # 带参数的命令
                    # 检查用户是否修改了这个
                    if cmd_id in self._shortcut_vars:
                        user_key = self._shortcut_vars[cmd_id][0].get().strip()
                        if user_key:
                            shortcuts.append({"Cmd": full_cmd, "Key": user_key})
                    else:
                        shortcuts.append(info)
            self.settings_file.set_shortcuts(shortcuts)

        # 收集外部查看器
        if hasattr(self, '_viewer_widgets'):
            viewers = []
            for card, fields in self._viewer_widgets:
                if not card.winfo_exists():
                    continue
                cmd = fields["CommandLine"].get().strip()
                if cmd:
                    viewers.append({
                        "CommandLine": cmd,
                        "Name": fields["Name"].get().strip(),
                        "Filter": fields["Filter"].get().strip(),
                        "Key": fields["Key"].get().strip(),
                    })
            self._set_array_entries("ExternalViewers", viewers)

        # 收集选中文字处理
        if hasattr(self, '_selection_widgets'):
            handlers = []
            for card, fields in self._selection_widgets:
                if not card.winfo_exists():
                    continue
                url = fields["URL"].get().strip()
                if url:
                    handlers.append({
                        "URL": url,
                        "Name": fields["Name"].get().strip(),
                        "Key": fields["Key"].get().strip(),
                    })
            self._set_array_entries("SelectionHandlers", handlers)

        # 收集主题
        if hasattr(self, '_theme_widgets'):
            themes = []
            for card, fields in self._theme_widgets:
                if not card.winfo_exists():
                    continue
                name = ""
                entry_dict = {}
                for k, v in fields.items():
                    if k == "Name":
                        name = v.get().strip() if isinstance(v, tk.StringVar) else ""
                        entry_dict[k] = name
                    elif isinstance(v, ColorButton):
                        entry_dict[k] = v.get_value()
                    elif isinstance(v, tk.BooleanVar):
                        entry_dict[k] = "true" if v.get() else "false"
                    elif isinstance(v, tk.StringVar):
                        entry_dict[k] = v.get().strip()
                if name:
                    themes.append(entry_dict)
            self._set_array_entries("Themes", themes)

    def _set_array_entries(self, array_name, entries):
        """将数组条目写入设置文件的解析树。"""
        new_items = []
        for entry in entries:
            entry_items = []
            for k, v in entry.items():
                if v:
                    entry_items.append(("kv", k, v))
            new_items.append(("struct", "", entry_items))

        # 在解析树中找到并替换
        for i, entry in enumerate(self.settings_file._parse_tree):
            if entry[0] == "struct" and entry[1] == array_name:
                self.settings_file._parse_tree[i] = (entry[0], entry[1], new_items)
                return

        # 没找到，添加到末尾
        insert_idx = len(self.settings_file._parse_tree)
        for i in range(len(self.settings_file._parse_tree) - 1, -1, -1):
            if self.settings_file._parse_tree[i][0] == "comment":
                insert_idx = i
            else:
                break
        self.settings_file._parse_tree.insert(insert_idx, ("struct", array_name, new_items))

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
