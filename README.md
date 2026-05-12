# 灵犀 AI 助手 - 多品牌全功能大模型调用程序

一个支持国内国外主流大模型服务商的统一调用客户端，**参考火山方舟 ccap.py 完全验证通过的调用逻辑开发**，完美解决图片和视频大模型连接问题。

## ✨ 特性

| 能力 | 支持情况 |
|------|----------|
| 💬 文本对话生成 | ✅ 全品牌支持 |
| 🎨 文生图片 | ✅ 豆包(即梦) / OpenAI(DALL-E3) / 百度文心一格 / 阿里通义万相 |
| 🎬 文生视频 | ✅ 豆包Seedance 2.0 Pro 轮询下载 |
| 📐 文本向量化 | ✅ 全品牌支持 |
| 🏷️ 7大模型品牌 | 豆包 · OpenAI · Claude · Google · 百度文心 · 阿里通义 · Anthropic |

## 🚀 快速开始

### 运行程序
```bash
python lingxi.py
```

### 操作流程
1. **选择大模型品牌** - 7大品牌直接选
2. **输入API Key** - 自动从环境变量检测或交互式输入
3. **选择能力类型** - 文本/图片/视频/向量
4. **输入模型名** - 支持自定义模型ID，不输入直接用官方默认
5. **开始调用** - 自动保存图片视频到本地

## 📁 输出目录
程序自动创建以下目录存放生成结果：
```
./images/      # 图片生成结果自动下载保存
./videos/      # 视频生成结果自动轮询下载
./outputs/     # 向量等其他结果
```

## 🔑 API Key 环境变量配置

| 品牌 | 环境变量名 | 申请地址 |
|------|-----------|---------|
| 豆包(火山方舟) | `ARK_API_KEY` | https://console.volcengine.com/ark/ |
| OpenAI | `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| 百度文心 | `BAIDU_API_KEY` + `BAIDU_SECRET_KEY` | https://console.bce.baidu.com/ai/ |
| 阿里通义 | `DASHSCOPE_API_KEY` | https://dashscope.aliyun.com/console |
| Claude | `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| Google Gemini | `GOOGLE_API_KEY` | https://ai.google.dev/ |

## 🎯 各品牌能力矩阵

| 品牌 | 文本生成 | 图片生成 | 视频生成 | 向量 |
|:----:|:-------:|:-------:|:-------:|:----:|
| 🔥 豆包火山方舟 | ✅ | ✅即梦5.0 | ✅Seedance视频 | ✅ |
| OpenAI | ✅ | ✅DALL-E 3 | ❌ | ✅ |
| 百度文心 | ✅ | ✅文心一格 | ⏳预留接口 | ✅ |
| 阿里通义 | ✅ | ✅万相 | ⏳预留接口 | ✅ |
| Claude 系列 | ✅ | ❌ | ❌ | ❌ |
| Google Gemini | ✅ | ❌ | ❌ | ❌ |

## 🔧 技术特点
- 100% 兼容你本地已经调通的 `ccap.py` 豆包图片/视频调用逻辑
- 百度文心自动处理 OAuth2 access_token 获取刷新
- 所有生成资源自动下载本地持久化，不丢失结果
- Windows cmd ANSI 颜色自动适配支持
- 完整的错误处理和提示引导

## 📝 使用示例 - 豆包视频生成
1. 选 1 豆包
2. 输入你的ARK_API_KEY
3. 选 3 视频生成
4. 模型名直接回车使用默认 `doubao-seedance-2-0-pro`
5. 输入提示词："一只可爱的橘猫在阳光下打滚"
6. 程序自动轮询等待，生成完成后视频自动保存到 ./videos/ 目录
