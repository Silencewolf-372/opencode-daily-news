---
name: daily-news
description: 当用户询问"今天有什么新闻"、"今天世界发生了什么"、"今日重点新闻"或类似问题时，自动执行新闻收集与整理任务，生成当天的重点新闻报告，并通过邮件推送到用户手机。支持国内外新闻源获取、AI新闻总结、口语化主持稿生成和TTS语音播报。
---

# Daily News Skill

当用户使用以下表述时激活本 Skill：
- "今天有什么新闻"
- "今天世界发生了什么"
- "今天国内外有什么新闻"
- "今日重点新闻"
- "最新新闻汇总"
- "给我今天的新闻"
- "新闻播报"
- "发布新闻"

## 使用方法

安装后，opencode 会自动识别用户对新闻的需求并执行本 Skill。

## 文件说明

| 文件 | 功能 |
|------|------|
| `AGENTS.md` | Agent 详细工作流程 |
| `config.py` | 配置文件（需要用户填写自己的 API Key 和邮箱信息） |
| `main.py` | 主执行入口 |
| `news_fetcher.py` | 新闻获取模块 |
| `news_summarizer.py` | AI 新闻总结模块 |
| `generate_script.py` | 口语化主持稿生成 |
| `tts_generator.py` | Edge TTS 语音生成 |
| `mail_sender.py` | 邮件发送模块 |

## 首次使用配置

1. 编辑 `config.py`，填写以下信息：
   - `MINIMAX_API_KEY`: 你的 MiniMax API Key
   - `EMAIL_USER`: 发送邮件的邮箱地址
   - `EMAIL_PASSWORD`: 邮箱授权码（不是登录密码）
   - `EMAIL_TO`: 接收邮件的地址

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 安装命令

```bash
npx skills add Silencewolf-372/opencode-daily-news@daily-news -g -y
```