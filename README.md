# SumatraPDF Configurator

SumatraPDF 高级设置可视化编辑工具，替代手动编辑文本配置文件。

> **基于 SumatraPDF 3.6 版本设置文档编写**
>
> 官方文档: https://www.sumatrapdfreader.org/settings/settings3-6
>
> ⚠️ SumatraPDF 的设置项可能随版本更新发生变化。如遇到新版本新增或修改的设置，
> 请参考[最新官方文档](https://www.sumatrapdfreader.org/settings/settings)并更新本工具中的设置定义。

## 功能

- **可视化编辑** — 图形界面修改 SumatraPDF 所有高级设置
- **分类浏览** — 17 个分类、117 个设置项，一目了然
- **智能控件** — 布尔值用复选框，枚举用下拉框，颜色用颜色选择器
- **保留结构** — 保存时不破坏原文件的注释和格式
- **自动检测** — 自动查找安装版/便携版的设置文件位置
- **高 DPI 支持** — 高分屏下界面清晰

## 截图

```
┌──────────────┬──────────────────────────────────────────────┐
│ 设置分类      │ 常规                                         │
│              │                                              │
│ ▶ 常规       │  每天检查一次更新                              │
│   显示与缩放  │  CheckForUpdates                             │
│   界面与交互  │  ☐ 启用                                      │
│   颜色与主题  │  ─────────────────────────────────────────── │
│   固定页面 UI │  在标签页中打开文档（而非新窗口）               │
│   电子书 UI   │  UseTabs                                     │
│   漫画书 UI   │  ☑ 启用                                      │
│   图片 UI     │  ─────────────────────────────────────────── │
│   批注        │  ...                                         │
│   正向搜索    │                                              │
│   打印        │                                              │
│   全屏模式    │                                              │
│   AI 聊天     │                                              │
│   专家/内部   │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

## 使用方法

### 环境要求

- Python 3.8+（tkinter 已包含在标准 Python 发行版中）

### 运行

```bash
# 自动检测设置文件
python SumatraPDF-Settings-Editor.py

# 指定设置文件路径
python SumatraPDF-Settings-Editor.py "C:\Users\你的用户名\AppData\Local\SumatraPDF\SumatraPDF-settings.txt"
```

### 设置文件位置

| 版本 | 路径 |
|------|------|
| 安装版 | `%LOCALAPPDATA%\SumatraPDF\SumatraPDF-settings.txt` |
| 便携版 | 与 `SumatraPDF.exe` 同目录 |

## 分类说明

| 分类 | 说明 |
|------|------|
| 常规 | 自动更新、标签页、语言、会话恢复 |
| 显示与缩放 | 页面布局、缩放、平滑滚动、滚动条 |
| 界面与交互 | 工具栏、菜单栏、侧边栏、字体、朗读 |
| 颜色与主题 | 主题 (light/dark/darker)、窗口背景色 |
| 固定页面 UI | 文字/背景/选中颜色、边距、渐变 |
| 电子书 UI | 字体大小、布局、自定义 CSS |
| 漫画书 UI | 边距、漫画模式 |
| 图片 UI | 背景色、默认缩放 |
| CHM UI | 是否使用固定页面 UI |
| 批注 | 高亮/下划线/删除线颜色、自由文本设置 |
| 正向搜索 | LaTeX 正向搜索高亮样式 |
| 打印 | 默认缩放和逐份打印 |
| 全屏模式 | 工具栏/菜单栏显示 |
| AI 聊天 | Claude Code / Grok Build / Codex Build 配置 |
| 专家/内部 | DPI、JavaScript、TeX、翻译语言等 |

## 其他工具

| 文件 | 说明 |
|------|------|
| `bin2coff.c` | 将二进制文件转换为 COFF 格式 |
| `sizer/` | 分析可执行文件大小 |
| `efi/` | EFI 文件解析工具 |
| `regress/` | 回归测试工具 |
| `test_sort.go` | Go 排序测试 |

## 许可证

MIT License

## 适配新版本

当 SumatraPDF 发布新版本并更新设置时，需要修改 `SumatraPDF-Settings-Editor.py` 中的 `SETTINGS_META` 列表来添加或更新设置项。

参考文档:
- [最新设置文档](https://www.sumatrapdfreader.org/settings/settings)
- [3.6 版本文档](https://www.sumatrapdfreader.org/settings/settings3-6)
