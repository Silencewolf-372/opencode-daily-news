# -*- coding: utf-8 -*-
"""
配置文件 - Daily News Agent
"""

# MiniMax API配置
MINIMAX_API_KEY = "YOUR_MINIMAX_API_KEY"  # 请替换为你的 MiniMax API Key
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic/v1"
MINIMAX_MODEL = "MiniMax-M2.7"  # MiniMax可用模型
MINIMAX_MAX_TOKENS = 1500  # 单次总结限制字数

# 邮箱配置
EMAIL_HOST = "smtp.163.com"
EMAIL_PORT = 465
EMAIL_USER = "your_email@example.com"  # 请替换为你的发送邮箱
EMAIL_PASSWORD = "YOUR_EMAIL_PASSWORD"  # 请替换为你的邮箱授权码
EMAIL_TO = "your_email@example.com"  # 请替换为接收邮箱

# 邮件主题格式
EMAIL_SUBJECT_PREFIX = "【每日新闻】"

# TTS配置
TTS_VOICE = "zh-CN-XiaoxiaoNeural"
TTS_OUTPUT_DIR = "./output"

# 新闻配置
NEWS_OUTPUT_DIR = "./output"

# 新闻分类配置
NEWS_CATEGORIES = {
    "国际政治": {"min": 6, "max": 8},
    "全球经济": {"min": 3, "max": 4},
    "科技动态": {"min": 2, "max": 3},
    "国家政策": {"min": 2, "max": 3},
    "国内重要事件": {"min": 2, "max": 3}
}

# 主持稿过渡语配置
TRANSITION_PHRASES = {
    "国际政治": "好的，现在为您播报今天的重点新闻，首先是国际政治方面。",
    "全球经济": "接下来我们来看看全球经济的动态。",
    "科技动态": "科技领域今天有什么新消息呢，让我们一起来了解。",
    "国家政策": "现在为您解读今天的政策动态。",
    "国内重要事件": "最后让我们关注一下国内的最新消息。",
    "default": "现在让我们继续播报下一条新闻。"
}

# 主持稿开场白（可选，设置为空表示不使用）
INTRO = ""

# 主持稿结束语（可选，设置为空表示不使用）
OUTRO = ""

# 标点符号处理规则
# True = 保留该符号，False = 删除或替换
PUNCTUATION_RULES = {
    "：": False,  # 删除冒号
    "；": True,   # 替换为句号（在处理时转换）
    "，": True,   # 保留逗号
    "。": True,   # 保留句号
    "！": True,   # 保留感叹号
    "？": True,   # 保留问号
    "：": False,  # 删除冒号
    "（": False,  # 删除左括号
    "）": False,  # 删除右括号
    "【": False,  # 删除方括号
    "】": False,  # 删除方括号
    '"': False,   # 删除双引号
    '"': False,   # 删除双引号
    ''': False,  # 删除单引号
    ''': False,  # 删除单引号
    "—": False,  # 删除破折号
    "-": False,   # 删除连字符
    "/": False,   # 删除斜杠
    "\\": False,  # 删除反斜杠
    "*": False,   # 删除星号（Markdown粗体标记）
    "#": False,   # 删除井号（Markdown标题标记）
}
