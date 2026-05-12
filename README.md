# 灵犀代码诊断助手 VS Code 插件

基于多品牌大模型API的代码问题诊断VS Code插件，支持自动诊断代码运行错误、逻辑问题、代码可读性，并为无注释的代码自动添加单行注释。

## 功能特性

- ✅ 代码运行错误诊断
- ✅ 代码逻辑问题分析
- ✅ 自动为无注释代码添加单行注释
- ✅ 支持 7 大主流品牌大模型
- ✅ 中文友好提示
- ✅ VS Code 右键菜单直接操作

## 安装方法

### 方法一：直接安装 VSIX 包（推荐）

1. 下载插件包 `lingxi-code-diagnoser-x.x.x.vsix`（请确保是最新版本）
2. 打开 VS Code，使用快捷键 `Ctrl+Shift+P` 打开命令面板
3. 输入 "Extensions: Install from VSIX" 并回车
4. 选择下载好的插件包文件

### 方法二：从源代码安装（适合开发）

1. 在项目根目录运行：
   ```bash
   cd c:\Users\Lenovo\Desktop\lingxi\code-diagnose-vscode-extension
   npm install
   ```
2. 按 `F5` 运行调试，VS Code 会打开一个扩展开发测试窗口
3. 在测试窗口中右键代码文件即可使用

## 使用方法

### 1. 右键菜单

在打开的代码文件中，右键点击代码区域，选择要使用的功能：

- **灵犀代码诊断助手：诊断当前代码** - 检查代码运行错误
- **灵犀代码诊断助手：为代码添加单行注释** - 自动添加注释
- **灵犀代码诊断助手：使用豆包诊断** - 强制使用豆包大模型

### 2. 命令面板

使用 `Ctrl+Shift+P` 打开命令面板，输入 "灵犀" 查找命令。

### 3. 快捷键

- `Ctrl+Shift+;` (Windows/Linux) 或 `Cmd+Shift+;` (Mac) - 诊断当前代码

## 配置说明

使用 `Ctrl+,` 打开设置，搜索 "lingxi-code-diagnoser" 进行配置：

| 配置项 | 默认值 | 说明 |
|--------|-------|------|
| lingxi-code-diagnoser.pythonPath | python3 | Python 解释器路径 |
| lingxi-code-diagnoser.workingDirectory | 空 | 灵犀项目根目录，默认自动检测 |

## 依赖

- **Python 3.8+** - 需要与运行 lingxi.py 相同的解释器
- **VS Code 1.80+** - 建议使用最新版本

## 常见问题

### Q: 为什么提示找不到 lingxi.py？

A: 请确保你已经正确设置了 `workingDirectory` 配置项，指向包含 `lingxi.py` 文件的目录。

### Q: 为什么没有反应？

A: 请检查 VS Code 的 "Output" → "Lingxi Code Diagnoser" 输出窗口，查看具体的错误信息。

### Q: 为什么 API 调用失败？

A: 请先运行一次独立的 lingxi.py 程序，确保已经设置好正确的 API Key。

## 支持语言

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Java (.java)
- C/C++ (.c, .cpp, .h)
- Go (.go)
- Rust (.rs)
- HTML (.html)
- CSS (.css)

## 许可证

MIT

---

**注意：** 使用前请确保你已阅读相关大模型的使用条款，并遵守当地法律法规。
