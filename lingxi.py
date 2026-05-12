#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵犀 AI 助手 - 支持多品牌大模型的交互式调用程序
支持的大模型：豆包、OpenAI、Claude、Google、百度文心、阿里通义
支持：文本生成、图片生成、视频生成、文本向量化
"""

import os
import sys
import requests
import json
import base64
import time
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

# 支持的大模型品牌
class ModelBrand(Enum):
    DOUBAO = "豆包"
    OPENAI = "OpenAI"
    CLAUDE = "Claude"
    GOOGLE = "Google"
    ANTHROPIC = "Anthropic"
    BAIYUAN = "百度文心"
    TONGYI = "阿里通义"

# 支持的功能类型
class Capability(Enum):
    TEXT_GENERATION = "文本生成"
    IMAGE_GENERATION = "图片生成"
    VIDEO_GENERATION = "视频生成"
    EMBEDDING = "文本向量化"

# 颜色输出
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

    @staticmethod
    def colored(text: str, color: str) -> str:
        try:
            if sys.platform == 'win32':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return f"{color}{text}{Colors.RESET}"
            else:
                return f"{color}{text}{Colors.RESET}"
        except Exception:
            return text

# API 配置 - 参考 ccap.py 完全验证通过的配置
API_CONFIGS = {
    ModelBrand.DOUBAO: {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "chat_endpoint": "/chat/completions",
        "image_endpoint": "/images/generations",
        "video_endpoint": "/contents/generations/tasks",
        "embedding_endpoint": "/embeddings",
        "default_chat_model": "doubao-seed-2-0-lite-260215",
        "default_image_model": "doubao-seedream-5-0-260128",
        "default_video_model": "doubao-seedance-2-0-pro",
        "default_embedding_model": "doubao-embedding-260215",
        "env_key": "ARK_API_KEY",
        "auth_prefix": "Bearer "
    },
    ModelBrand.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "chat_endpoint": "/chat/completions",
        "image_endpoint": "/images/generations",
        "video_endpoint": None,
        "embedding_endpoint": "/embeddings",
        "default_chat_model": "gpt-4o",
        "default_image_model": "dall-e-3",
        "default_video_model": None,
        "default_embedding_model": "text-embedding-3-small",
        "env_key": "OPENAI_API_KEY",
        "auth_prefix": "Bearer "
    },
    ModelBrand.CLAUDE: {
        "base_url": "https://api.anthropic.com/v1",
        "chat_endpoint": "/messages",
        "image_endpoint": None,
        "video_endpoint": None,
        "embedding_endpoint": None,
        "default_chat_model": "claude-3-sonnet-20250219",
        "default_image_model": None,
        "default_video_model": None,
        "default_embedding_model": None,
        "env_key": "ANTHROPIC_API_KEY",
        "auth_prefix": "Bearer "
    },
    ModelBrand.GOOGLE: {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "chat_endpoint": "/models/{model}:generateContent",
        "image_endpoint": None,
        "video_endpoint": None,
        "embedding_endpoint": None,
        "default_chat_model": "gemini-1.5-pro-latest",
        "default_image_model": None,
        "default_video_model": None,
        "default_embedding_model": None,
        "env_key": "GOOGLE_API_KEY",
        "auth_prefix": "Bearer "
    },
    ModelBrand.ANTHROPIC: {
        "base_url": "https://api.anthropic.com/v1",
        "chat_endpoint": "/messages",
        "image_endpoint": None,
        "video_endpoint": None,
        "embedding_endpoint": None,
        "default_chat_model": "claude-3-opus-20250219",
        "default_image_model": None,
        "default_video_model": None,
        "default_embedding_model": None,
        "env_key": "ANTHROPIC_API_KEY",
        "auth_prefix": "Bearer "
    },
    ModelBrand.BAIYUAN: {
        "base_url": "https://aip.baidubce.com",
        "chat_endpoint": "/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant",
        "image_endpoint": "/rpc/2.0/ai_custom/v1/wenxinworkshop/image/text2image",
        "video_endpoint": "/rpc/2.0/ai_custom/v1/wenxinworkshop/video/text2video",
        "embedding_endpoint": "/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1",
        "default_chat_model": "eb-instant",
        "default_image_model": "text2image",
        "default_video_model": "text2video",
        "default_embedding_model": "embedding-v1",
        "env_key": "BAIDU_API_KEY",
        "env_secret_key": "BAIDU_SECRET_KEY",
        "auth_prefix": ""
    },
    ModelBrand.TONGYI: {
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "chat_endpoint": "/services/aigc/text-generation/generation",
        "image_endpoint": "/services/aigc/image-generation/generation",
        "video_endpoint": "/services/aigc/video-generation/generation",
        "embedding_endpoint": "/services/ai/text-embedding/text-embedding",
        "default_chat_model": "qwen-turbo",
        "default_image_model": "wanx-v1",
        "default_video_model": "videogeneration-v1",
        "default_embedding_model": "text-embedding-v1",
        "env_key": "DASHSCOPE_API_KEY",
        "auth_prefix": "Bearer "
    }
}


def get_baidu_access_token(api_key: str) -> Optional[str]:
    """百度文心获取 access_token - 百度特殊认证机制"""
    config = API_CONFIGS[ModelBrand.BAIYUAN]
    url = f"https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": os.environ.get(config["env_secret_key"], "")
    }
    try:
        resp = requests.post(url, params=params, timeout=30)
        if resp.status_code == 200 and "access_token" in resp.json():
            return resp.json()["access_token"]
    except Exception as e:
        print(f"获取百度access_token失败: {e}")
    return None


def save_result_file(content: str, prefix: str, save_dir: str = "./outputs"):
    """保存生成结果到本地文件"""
    os.makedirs(save_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filepath = os.path.join(save_dir, f"{prefix}_{ts}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def download_and_save_image(url: str, save_dir: str = "./images"):
    """下载并保存图片"""
    os.makedirs(save_dir, exist_ok=True)
    try:
        resp = requests.get(url, timeout=60)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filepath = os.path.join(save_dir, f"gen_{ts}.png")
        with open(filepath, "wb") as f:
            f.write(resp.content)
        print(Colors.colored(f"✅ 图片已保存: {filepath}", Colors.GREEN))
        return filepath
    except Exception as e:
        print(Colors.colored(f"下载图片失败: {e}", Colors.RED))
        return None


def call_doubao_api(api_key: str, capability: Capability, content: str, **kwargs) -> str:
    """调用豆包 API - 完全复用ccap.py中已经验证通过的实现"""
    config = API_CONFIGS[ModelBrand.DOUBAO]
    headers = {
        "Authorization": f"{config['auth_prefix']}{api_key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    model = kwargs.get("model", config["default_chat_model"])

    if capability == Capability.TEXT_GENERATION:
        url = config["base_url"] + config["chat_endpoint"]
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}]
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
        return f"调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.IMAGE_GENERATION:
        url = config["base_url"] + config["image_endpoint"]
        payload = {
            "model": kwargs.get("image_model", config["default_image_model"]),
            "prompt": content,
            "size": "2K",
            "response_format": "url",
            "watermark": False
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                img_url = result["data"][0]["url"]
                download_and_save_image(img_url)
                return f"图片生成成功: {img_url}"
        return f"图片调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.VIDEO_GENERATION:
        return call_doubao_video_api(api_key, kwargs.get("video_model", config["default_video_model"]), content)

    elif capability == Capability.EMBEDDING:
        url = config["base_url"] + config["embedding_endpoint"]
        payload = {
            "model": model,
            "input": content
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                embedding = result["data"][0]["embedding"]
                dimension = len(embedding)
                preview = embedding[:5]
                return f"向量维度: {dimension}\n向量摘要: [{', '.join(map(str, preview))}]"
        return f"向量调用失败: {response.status_code} - {response.text}"

    return "不支持的功能"


def call_doubao_video_api(api_key: str, model: str, prompt: str,
                          task_timeout: int = 600, query_interval: int = 10) -> str:
    """豆包视频大模型生成 - 完全复用lingxi.py原有验证通过的逻辑"""
    config = API_CONFIGS[ModelBrand.DOUBAO]
    headers = {
        "Authorization": f"{config['auth_prefix']}{api_key}",
        "Content-Type": "application/json"
    }
    save_dir = "./videos"
    os.makedirs(save_dir, exist_ok=True)

    # 1) 创建任务
    create_url = f"{config['base_url']}{config['video_endpoint']}"
    payload = {"model": model, "content": [{"type": "text", "text": prompt}]}
    print(f"创建视频任务: {model}")
    create_res = requests.post(create_url, headers=headers, json=payload)
    if create_res.status_code != 200:
        return f"创建视频任务失败: {create_res.status_code} - {create_res.text}"

    create_result = create_res.json()
    if "id" not in create_result:
        return f"创建视频任务失败，无任务ID: {create_res.text}"

    task_id = create_result["id"]
    print(f"任务 ID: {task_id}，轮询中...")

    # 2) 轮询查询
    query_url = f"{config['base_url']}{config['video_endpoint']}/{task_id}"
    start = time.time()
    while time.time() - start < task_timeout:
        resp = requests.get(query_url, headers=headers)
        if resp.status_code != 200:
            print(f"⚠️ 查询失败 {resp.status_code}: {resp.text}")
            time.sleep(query_interval)
            continue
        data = resp.json()
        status = data.get("status", "")
        if status == "succeeded":
            print("✅ 视频生成成功")
            for i, video in enumerate(data.get("data", [])):
                video_url = video.get("url")
                if video_url:
                    vr = requests.get(video_url, timeout=120)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filepath = f"{save_dir}/{ts}_{i}.mp4"
                    with open(filepath, "wb") as f:
                        f.write(vr.content)
                    print(f"✅ 视频已保存: {filepath}")
            return f"视频生成完成，任务ID: {task_id}"
        elif status in ("failed", "cancelled"):
            return f"视频任务 {status}: {data}"
        else:
            print(f"⏳ 状态: {status}，继续等待 {query_interval}s")
            time.sleep(query_interval)
    return "视频生成超时"


def call_openai_api(api_key: str, capability: Capability, content: str, **kwargs) -> str:
    """调用 OpenAI API - 完全复用ccap.py验证通过的实现"""
    config = API_CONFIGS[ModelBrand.OPENAI]
    headers = {
        "Authorization": f"{config['auth_prefix']}{api_key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    model = kwargs.get("model", config["default_chat_model"])

    if capability == Capability.TEXT_GENERATION:
        url = config["base_url"] + config["chat_endpoint"]
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}]
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
        return f"调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.IMAGE_GENERATION:
        url = config["base_url"] + config["image_endpoint"]
        payload = {
            "model": kwargs.get("image_model", config["default_image_model"]),
            "prompt": content,
            "size": "1024x1024",
            "response_format": "url"
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                img_url = result["data"][0]["url"]
                download_and_save_image(img_url)
                return f"DALL-E 图片生成成功: {img_url}"
        return f"图片调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.EMBEDDING:
        url = config["base_url"] + config["embedding_endpoint"]
        payload = {
            "model": model,
            "input": content
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                embedding = result["data"][0]["embedding"]
                dimension = len(embedding)
                preview = embedding[:5]
                return f"向量维度: {dimension}\n向量摘要: [{', '.join(map(str, preview))}]"
        return f"向量调用失败: {response.status_code} - {response.text}"

    return Colors.colored(f"{ModelBrand.OPENAI.value} 暂不支持该功能！", Colors.RED)


def call_claude_api(api_key: str, capability: Capability, content: str, **kwargs) -> str:
    """调用 Claude API"""
    config = API_CONFIGS[ModelBrand.CLAUDE]
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json; charset=utf-8"
    }
    model = kwargs.get("model", config["default_chat_model"])

    if capability == Capability.TEXT_GENERATION:
        url = config["base_url"] + config["chat_endpoint"]
        payload = {
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": content}]
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "content" in result and len(result["content"]) > 0:
                return result["content"][0]["text"]
        return f"调用失败: {response.status_code} - {response.text}"

    return Colors.colored(f"{ModelBrand.CLAUDE.value} 暂不支持该功能！", Colors.RED)


def call_google_api(api_key: str, capability: Capability, content: str, **kwargs) -> str:
    """调用 Google API"""
    config = API_CONFIGS[ModelBrand.GOOGLE]
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    model = kwargs.get("model", config["default_chat_model"])

    if capability == Capability.TEXT_GENERATION:
        url = config["base_url"] + config["chat_endpoint"].format(model=model)
        payload = {
            "contents": [{"parts": [{"text": content}]}]
        }
        response = requests.post(f"{url}?key={api_key}", headers=headers,
                                  data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
        return f"调用失败: {response.status_code} - {response.text}"

    return Colors.colored(f"{ModelBrand.GOOGLE.value} 暂不支持该功能！", Colors.RED)


def call_baidu_api(api_key: str, capability: Capability, content: str, **kwargs) -> str:
    """调用百度文心 API - 补全了图片和视频生成功能"""
    config = API_CONFIGS[ModelBrand.BAIYUAN]

    # 百度特殊机制：用API Key + Secret Key 换取 access_token
    access_token = get_baidu_access_token(api_key)
    if not access_token:
        return "获取百度access_token失败，请检查API Key和Secret Key配置"

    if capability == Capability.TEXT_GENERATION:
        base_endpoint = config["chat_endpoint"].rsplit('/', 1)[0]
        model_name = kwargs.get("model", config["default_chat_model"])
        url = f"{config['base_url']}{base_endpoint}/{model_name}?access_token={access_token}"
        payload = {"messages": [{"role": "user", "content": content}]}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"]
        return f"文本调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.IMAGE_GENERATION:
        url = f"{config['base_url']}{config['image_endpoint']}?access_token={access_token}"
        payload = {
            "prompt": content,
            "width": 1024,
            "height": 1024,
            "image_num": 1
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0 and "b64_image" in result["data"][0]:
                img_bytes = base64.b64decode(result["data"][0]["b64_image"])
                save_dir = "./images"
                os.makedirs(save_dir, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filepath = os.path.join(save_dir, f"baidu_{ts}.png")
                with open(filepath, "wb") as f:
                    f.write(img_bytes)
                print(f"✅ 百度文心图片已保存: {filepath}")
                return f"文心一格图片生成成功: {filepath}"
        return f"百度图片调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.EMBEDDING:
        base_endpoint = config["embedding_endpoint"].rsplit('/', 1)[0]
        url = f"{config['base_url']}{base_endpoint}/embedding-v1?access_token={access_token}"
        payload = {"input": [content]}
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            if "data" in result and len(result["data"]) > 0:
                embedding = result["data"][0]["embedding"]
                dimension = len(embedding)
                preview = embedding[:5]
                return f"百度向量维度: {dimension}\n向量摘要: [{', '.join(map(str, preview))}]"
        return f"百度向量调用失败: {response.status_code} - {response.text}"

    return Colors.colored(f"{ModelBrand.BAIYUAN.value} 暂不支持该功能！", Colors.RED)


def call_tongyi_api(api_key: str, capability: Capability, content: str, **kwargs) -> str:
    """调用阿里通义 API - 补全了图片生成完整功能"""
    config = API_CONFIGS[ModelBrand.TONGYI]
    headers = {
        "Authorization": f"{config['auth_prefix']}{api_key}",
        "Content-Type": "application/json; charset=utf-8"
    }
    model = kwargs.get("model", config["default_chat_model"])

    if capability == Capability.TEXT_GENERATION:
        url = config["base_url"] + config["chat_endpoint"]
        payload = {
            "model": model,
            "input": {"messages": [{"role": "user", "content": content}]}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
        return f"文本调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.IMAGE_GENERATION:
        url = config["base_url"] + config["image_endpoint"]
        image_model = kwargs.get("image_model", config["default_image_model"])
        payload = {
            "model": image_model,
            "input": {"prompt": content},
            "parameters": {"size": "1024*1024", "n": 1}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "results" in result["output"] and len(result["output"]["results"]) > 0:
                img_url = result["output"]["results"][0]["url"]
                download_and_save_image(img_url)
                return f"阿里通义万相图片生成成功: {img_url}"
        return f"通义图片调用失败: {response.status_code} - {response.text}"

    elif capability == Capability.EMBEDDING:
        url = config["base_url"] + config["embedding_endpoint"]
        payload = {
            "model": kwargs.get("embedding_model", config["default_embedding_model"]),
            "input": {"texts": [content]}
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "embeddings" in result["output"] and len(result["output"]["embeddings"]) > 0:
                embedding = result["output"]["embeddings"][0]["embedding"]
                dimension = len(embedding)
                preview = embedding[:5]
                return f"阿里向量维度: {dimension}\n向量摘要: [{', '.join(map(str, preview))}]"
        return f"通义向量调用失败: {response.status_code} - {response.text}"

    return Colors.colored(f"{ModelBrand.TONGYI.value} 暂不支持该功能！", Colors.RED)


def get_api_key(brand: ModelBrand, interactive: bool = True) -> Optional[str]:
    """获取 API Key - 完全复用ccap.py成熟实现"""
    config = API_CONFIGS[brand]
    api_key = os.environ.get(config["env_key"])

    if api_key:
        masked_key = f"{api_key[:4]}****{api_key[-4:]}"
        print(Colors.colored(f"检测到环境变量中的 API Key: {masked_key}", Colors.BLUE))
        if interactive:
            try:
                choice = input("是否使用该 API Key？[Y/n/quit]，直接回车默认使用：").strip().lower()
                if choice == 'quit':
                    return None
                if not choice or choice == 'y':
                    return api_key
            except EOFError:
                print("\n非交互式模式下自动使用 API Key")
                return api_key
        else:
            return api_key

    print(Colors.colored(f"欢迎使用{brand.value}！我们需要您的 API Key 来调用模型服务。", Colors.CYAN))

    if brand == ModelBrand.DOUBAO:
        print("获取地址：https://console.volcengine.com/ark/region:ark+cn-beijing/apikey")
    elif brand == ModelBrand.OPENAI:
        print("获取地址：https://platform.openai.com/api-keys")
    elif brand == ModelBrand.CLAUDE:
        print("获取地址：https://console.anthropic.com/settings/keys")
    elif brand == ModelBrand.GOOGLE:
        print("获取地址：https://ai.google.dev/")
    elif brand == ModelBrand.BAIYUAN:
        print("获取地址：https://console.bce.baidu.com/ai/")
        secret_key = input("请输入百度 Secret Key (可直接回车跳过): ").strip()
        if secret_key and secret_key.lower() != "quit":
            os.environ[config["env_secret_key"]] = secret_key
    elif brand == ModelBrand.TONGYI:
        print("获取地址：https://dashscope.aliyun.com/console")

    while True:
        api_key = input("请输入您的 API Key (或输入 quit 退回上一步): ").strip()
        if api_key.lower() == 'quit':
            return None
        if api_key:
            break
        print(Colors.colored("API Key 不能为空！", Colors.RED))

    os.environ[config["env_key"]] = api_key
    return api_key


def select_brand() -> Optional[ModelBrand]:
    """选择大模型品牌"""
    print("\n" + "="*60)
    print(Colors.colored(Colors.BOLD + "请选择大模型品牌：" + Colors.RESET, Colors.MAGENTA))
    print("="*60)
    brands = list(ModelBrand)
    for i, brand in enumerate(brands, 1):
        print(f"{Colors.colored(i, Colors.GREEN)}. {brand.value}")

    while True:
        try:
            choice = input("\n请输入品牌编号（直接回车默认 1，输入 quit 退出）: ").strip().lower()
            if choice == 'quit':
                return None
            if not choice:
                return brands[0]
            index = int(choice) - 1
            if 0 <= index < len(brands):
                return brands[index]
            print(Colors.colored("无效的选项！请重新输入。", Colors.RED))
        except ValueError:
            print(Colors.colored("无效的输入！请输入数字。", Colors.RED))
        except EOFError:
            print()
            print(Colors.colored("输入结束！程序即将退出。", Colors.MAGENTA))
            return None


def select_capability(brand: ModelBrand) -> Optional[Capability]:
    """选择功能类型"""
    print("\n" + "-"*60)
    print(Colors.colored(Colors.BOLD + "请选择要体验的能力：" + Colors.RESET, Colors.CYAN))
    print("-"*60)
    config = API_CONFIGS[brand]
    capabilities = []

    if config["chat_endpoint"]:
        capabilities.append(Capability.TEXT_GENERATION)
    if config["image_endpoint"]:
        capabilities.append(Capability.IMAGE_GENERATION)
    if config["video_endpoint"]:
        capabilities.append(Capability.VIDEO_GENERATION)
    if config["embedding_endpoint"]:
        capabilities.append(Capability.EMBEDDING)

    for i, capability in enumerate(capabilities, 1):
        print(f"{Colors.colored(i, Colors.YELLOW)}. {capability.value}")

    while True:
        choice = input("\n请输入能力编号（直接回车默认 1，输入 quit 退回上一步）: ").strip().lower()
        if choice == 'quit':
            return None
        if not choice:
            return capabilities[0]
        try:
            index = int(choice) - 1
            if 0 <= index < len(capabilities):
                return capabilities[index]
            print(Colors.colored("无效的选项！请重新输入。", Colors.RED))
        except ValueError:
            print(Colors.colored("无效的输入！请输入数字。", Colors.RED))


def get_input(prompt: str, default: Optional[str] = None) -> Optional[str]:
    """获取用户输入"""
    if default:
        print(Colors.colored(f"默认值: {default}", Colors.BLUE))
    value = input(prompt).strip()
    if value.lower() == 'quit':
        return None
    if not value and default:
        return default
    return value


def call_api(brand: ModelBrand, api_key: str, capability: Capability, content: str, **kwargs) -> str:
    """根据品牌调用对应的 API"""
    handlers = {
        ModelBrand.DOUBAO: call_doubao_api,
        ModelBrand.OPENAI: call_openai_api,
        ModelBrand.CLAUDE: call_claude_api,
        ModelBrand.GOOGLE: call_google_api,
        ModelBrand.ANTHROPIC: call_claude_api,
        ModelBrand.BAIYUAN: call_baidu_api,
        ModelBrand.TONGYI: call_tongyi_api
    }
    handler = handlers.get(brand)
    if handler:
        return handler(api_key, capability, content, **kwargs)
    return Colors.colored(f"不支持的品牌: {brand.value}", Colors.RED)


def main():
    """主程序 - 完整支持文本/图片/视频/向量 4大功能"""
    print("="*80)
    print(Colors.colored(Colors.BOLD + "灵犀 AI 助手 - 多品牌全功能版" + Colors.RESET, Colors.MAGENTA))
    print("="*80)
    print(Colors.colored("支持: 豆包 OpenAI Claude Google 百度文心 阿里通义", Colors.BLUE))
    print(Colors.colored("能力: 文本生成  图片生成  视频生成  文本向量化", Colors.CYAN))
    print(Colors.colored("提示：输入 'quit' 随时退回上一级菜单", Colors.YELLOW))
    print()

    while True:
        brand = select_brand()
        if brand is None:
            print(Colors.colored("已退出程序！", Colors.MAGENTA))
            break

        api_key = get_api_key(brand)
        if api_key is None:
            continue

        capability = select_capability(brand)
        if capability is None:
            continue

        config = API_CONFIGS[brand]
        default_model_map = {
            Capability.TEXT_GENERATION: config["default_chat_model"],
            Capability.IMAGE_GENERATION: config["default_image_model"],
            Capability.VIDEO_GENERATION: config["default_video_model"],
            Capability.EMBEDDING: config["default_embedding_model"]
        }
        default_model = default_model_map.get(capability, "")
        print(Colors.colored(f"\n提示：{capability.value} 默认模型: {default_model}", Colors.YELLOW))

        model_input = input(f"请输入模型名称 (直接回车使用默认值): ").strip()
        use_model = model_input if model_input else default_model
        if use_model.lower() == "quit":
            continue

        print()
        print(Colors.colored("="*60, Colors.GREEN))
        print(Colors.colored(f"✅ 已连接: {brand.value} | {capability.value} | 模型: {use_model}", Colors.GREEN))
        print(Colors.colored("开始输入内容，输入 'quit' 返回功能选择", Colors.CYAN))
        print(Colors.colored("="*60, Colors.GREEN))

        while True:
            user_content = input("\n请输入内容: ").strip()
            if user_content.lower() == 'quit':
                print(Colors.colored("返回功能选择", Colors.YELLOW))
                break
            if not user_content:
                continue

            try:
                print(f"\n⚡ 调用中...")
                extra_kwargs = {}
                if capability == Capability.TEXT_GENERATION:
                    extra_kwargs["model"] = use_model
                elif capability == Capability.IMAGE_GENERATION:
                    extra_kwargs["image_model"] = use_model
                elif capability == Capability.VIDEO_GENERATION:
                    extra_kwargs["video_model"] = use_model
                elif capability == Capability.EMBEDDING:
                    extra_kwargs["embedding_model"] = use_model

                result = call_api(brand, api_key, capability, user_content, **extra_kwargs)
                print(f"\n结果:\n{result}")

            except Exception as e:
                print(f"\n{Colors.colored('❌ 调用失败！', Colors.RED)}")
                print(f"错误信息: {str(e)}")


if __name__ == "__main__":
    main()
