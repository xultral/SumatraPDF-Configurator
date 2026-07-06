# SumatraPDF Configurator

SumatraPDF 高级设置可视化编辑工具，替代手动编辑文本配置文件。

> **基于 SumatraPDF 3.6 版本设置文档编写**
>
> 官方文档: https://www.sumatrapdfreader.org/settings/settings3-6
>
> ⚠️ SumatraPDF 的设置项可能随版本更新发生变化。如遇到新版本新增或修改的设置，
> 请参考[最新官方文档](https://www.sumatrapdfreader.org/settings/settings)并更新本工具中的设置定义。

## 下载

- [最新 Release](https://github.com/xultral/SumatraPDF-Configurator/releases) — 下载 EXE 即用，无需安装 Python
- 或直接运行源码：`python SumatraPDF-Settings-Editor.py`

## 功能

### 可视化编辑器

- **简单设置** — 布尔值用自定义大复选框，枚举用下拉框，颜色用颜色选择器（带预览色块）
- **快捷键编辑器** — 显示所有 100+ 个命令，可直接修改快捷键绑定，带中文说明
- **外部查看器** — 可视化添加/编辑外部程序（预置 Adobe Acrobat、Foxit、PDF-XChange）
- **选中文字处理** — 可视化添加翻译/搜索服务（预置 Google 翻译、DeepL、百度、Wikipedia）
- **自定义主题** — 可视化创建颜色主题（预置 Solarized Dark、Dracula、Nord、One Dark 等）
- **保留结构** — 保存时不破坏原文件的注释和格式
- **自动检测** — 自动查找安装版/便携版的设置文件位置

### 分类浏览（15 个分类）

| 分类 | 设置项数 | 说明 |
|------|---------|------|
| 常规 | 10 | 自动更新、标签页、会话恢复、语言 |
| 页面显示 | 8 | 页面布局、缩放、滚动、抗锯齿 |
| 工具栏与侧边栏 | 13 | 工具栏、菜单栏、侧边栏、标签页、字体 |
| 主题与外观 | 3 | 主题 (light/dark/darker)、背景色 |
| PDF / XPS / DjVu 页面 | 8 | 文字/背景颜色、边距、渐变、滚动条 |
| 电子书 | 5 | 字体、布局、自定义 CSS |
| 漫画与图片 | 3 | 边距、漫画模式 |
| CHM 帮助文件 | 1 | 是否用 PDF 渲染方式 |
| PDF 批注 | 12 | 高亮/下划线/删除线颜色、文本批注 |
| LaTeX 正向搜索 | 4 | 高亮样式、颜色 |
| 打印 | 1 | 默认缩放方式 |
| 快捷键 | 100+ | 可视化编辑器，带命令参考表 |
| 外部查看器 | — | 可视化编辑器，带预设模板 |
| 选中文字处理 | — | 可视化编辑器，带预设模板 |
| 自定义主题 | — | 可视化编辑器，带预设主题 |
| 高级选项 | 9 | DPI、TeX、密码、Esc 退出等 |

## 使用方法

### 环境要求

- Python 3.8+（tkinter 和 Pillow 为依赖）
- 或直接下载 EXE（无需任何依赖）

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

## 打包 EXE

```bash
pip install pyinstaller pillow
python -m PyInstaller --onefile --windowed --name SumatraPDF-Settings-Editor --icon logo.png --add-data "logo.png;." --exclude-module numpy --exclude-module pandas --exclude-module matplotlib --exclude-module pygame --exclude-module psutil -y SumatraPDF-Settings-Editor.py
```

生成的 EXE 在 `dist/SumatraPDF-Settings-Editor.exe`。

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
