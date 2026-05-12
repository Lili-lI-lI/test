一、项目概述
灵犀AI助手是一个集成了多个主流AI大模型的多功能工具，支持代码诊断、文本生成、图片生成、视频生成和文本向量化等功能。本项目包含两大部分：

核心Python工具：lingxi.py - 支持通过命令行调用各AI大模型的全功能模块
VSCode扩展：lingxi-code-diagnoser - 集成在VSCode中的代码诊断助手，可直接在编辑器中进行代码错误诊断、逻辑分析和注释添加
支持的AI大模型品牌：豆包、OpenAI、Claude、Google、百度文心、阿里通义

二、系统要求
Python环境：Python 3.7及以上版本
操作系统：Windows 10/11、macOS、Linux
VSCode版本：1.80.0及以上（仅针对VSCode扩展）
网络连接：需要稳定的互联网连接以调用AI大模型API
API密钥：需要对应AI大模型平台的API密钥
三、安装步骤
3.1 Python环境配置
检查Python版本


python --version  # 或 python3 --version
确保版本为3.7及以上，若未安装Python，请从Python官网下载安装

安装依赖库
在项目根目录下运行：


pip install -r requirements.txt
若没有requirements.txt文件，手动安装依赖：


pip install requests python-dotenv
3.2 获取API密钥
根据需要使用的AI大模型，前往对应平台获取API密钥：

模型品牌	获取地址	环境变量名
豆包	火山方舟	ARK_API_KEY
OpenAI	OpenAI平台	OPENAI_API_KEY
Claude	Anthropic平台	ANTHROPIC_API_KEY
Google	AI Studio	GOOGLE_API_KEY
百度文心	百度智能云	BAIDU_API_KEY、BAIDU_SECRET_KEY
阿里通义	阿里云DashScope	DASHSCOPE_API_KEY
3.3 配置环境变量（可选）
为避免每次输入API密钥，可将API密钥设置为环境变量：

Windows系统（命令行）：


setx ARK_API_KEY "your-api-key-here"
setx OPENAI_API_KEY "your-api-key-here"
macOS/Linux系统（终端）：


# 临时生效（当前会话）
export ARK_API_KEY="your-api-key-here"
export OPENAI_API_KEY="your-api-key-here"

# 永久生效（添加到~/.bashrc或~/.zshrc）
echo 'export ARK_API_KEY="your-api-key-here"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
3.4 VSCode扩展安装
方法一：从VSCode市场安装（如果已发布）

打开VSCode，进入扩展市场（Ctrl+Shift+X）
搜索"灵犀代码诊断助手"
点击安装
方法二：手动安装本地包

下载lingxi-code-diagnoser-0.0.1.vsix文件
打开VSCode，按Ctrl+Shift+P打开命令面板
输入"Extensions: Install from VSIX..."
选择下载的VSIX文件完成安装
四、配置说明
4.1 命令行工具配置
命令行工具无需额外配置，运行时会自动检测环境变量中的API密钥，或引导您输入密钥。

4.2 VSCode扩展配置
打开VSCode设置（File > Preferences > Settings）
搜索"灵犀代码诊断助手"
配置以下选项：
Python路径：指定Python解释器路径，默认为"python"
工作目录：指定灵犀项目的根目录（包含lingxi.py的目录）
五、使用方法
5.1 命令行工具使用
启动灵犀AI助手


python lingxi.py
选择AI模型
根据提示输入模型编号选择要使用的AI大模型

选择功能类型
支持以下功能：

文本生成：生成各种类型的文本内容
图片生成：根据文本描述生成图片
视频生成：根据文本描述生成视频（部分模型支持）
文本向量化：将文本转换为向量表示
输入内容并获取结果
根据所选功能输入相应内容，系统会调用AI大模型处理并返回结果

5.2 代码诊断工具使用
通过命令行直接运行代码诊断：


# 诊断代码中的运行时错误
python vscode_plugin/diagnose_code.py your_code.py -t errors

# 诊断代码中的逻辑问题
python vscode_plugin/diagnose_code.py your_code.py -t logic

# 自动为代码添加单行注释
python vscode_plugin/diagnose_code.py your_code.py -t comments -a
参数说明：

-t, --type：诊断类型，可选值：errors(运行错误)、logic(逻辑问题)、comments(补全注释)
-o, --output：指定输出文件路径（JSON格式）
-a, --apply：自动应用注释到代码文件（仅comments类型支持）
-b, --brand：指定使用的AI大模型品牌
5.3 VSCode扩展使用
5.3.1 基础操作
打开要诊断的代码文件
在VSCode中打开需要诊断的代码文件

调用诊断功能
方法一：右键菜单 > 选择相应的诊断功能
方法二：按Ctrl+Shift+; 快捷键直接调用代码诊断
方法三：按Ctrl+Shift+P打开命令面板，输入"灵犀代码诊断助手"选择相应功能

5.3.2 功能说明
诊断当前代码：检测代码中的运行时错误
为代码添加单行注释：自动为无注释的代码添加中文单行注释
使用豆包诊断：使用豆包大模型诊断代码中的运行时错误
5.3.3 查看结果
诊断完成后，结果会显示在VSCode的"Lingxi Code Diagnoser"输出窗口中，包含：

问题所在行号和列号
问题描述
修改建议
六、常见问题
6.1 API密钥相关问题
Q：为什么总是提示API密钥无效？
A：请检查：

API密钥是否正确复制，没有多余空格
密钥对应的账户是否有足够的余额或调用额度
网络是否能正常访问对应AI平台的API服务
部分模型（如百度文心）需要同时提供API Key和Secret Key
6.2 VSCode扩展问题
Q：VSCode扩展提示"未找到lingxi.py"？
A：请在VSCode设置中正确配置工作目录，确保该目录下包含lingxi.py文件。

Q：VSCode扩展运行时出现Python相关错误？
A：请检查：

Python路径配置是否正确
Python环境是否已安装必要的依赖库
确保Python版本符合要求（3.7+）
6.3 其他问题
Q：为什么生成的图片/视频没有保存到本地？
A：请检查：

程序是否有文件写入权限
当前目录下是否有outputs、images、videos目录
网络是否能正常访问AI平台返回的资源链接
Q：为什么调用API时总是超时？
A：请检查：

网络连接是否稳定
是否需要配置代理服务器
AI平台是否有服务中断或限流、

提示：首次使用建议先通过命令行工具测试API密钥是否正常工作，再配置VSCode扩展以获得更好的开发体验。
