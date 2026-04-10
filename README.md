# Daily News Agent for Opencode

自动化新闻收集、整理、播报和推送的 opencode skill。当用户询问"今天有什么新闻"时，自动从多个新闻源获取当日重点新闻，生成口语化播报稿，并通过邮件推送到手机。

## 功能特性

- **多源新闻获取**: 新华网、人民网、央视新闻、澎湃新闻、新浪新闻、BBC News、CNN、Reuters 等
- **AI 新闻总结**: 使用 MiniMax API 对新闻进行智能总结
- **口语化主持稿**: 自动生成适合 TTS 朗读的播报脚本
- **语音播报**: 使用 Edge TTS 生成 MP3 语音文件
- **邮件推送**: 自动发送包含新闻报告和语音附件的邮件

## 安装

```bash
npx skills add Silencewolf-372/opencode-daily-news@daily-news -g -y
```

## 配置

### 1. 编辑配置文件

安装后，编辑项目中的 `config.py` 文件，填入你的配置信息：

```python
# MiniMax API 配置
MINIMAX_API_KEY = "你的MiniMax API Key"

# 邮箱配置
EMAIL_HOST = "smtp.163.com"      # 邮箱 SMTP 服务器
EMAIL_PORT = 465                  # 端口（163邮箱用465）
EMAIL_USER = "your_email@163.com" # 发送邮箱地址
EMAIL_PASSWORD = "your_auth_code" # 邮箱授权码（不是登录密码）
EMAIL_TO = "receive@163.com"      # 接收邮箱地址
```

### 2. 获取 MiniMax API Key

1. 访问 [MiniMax 开放平台](https://platform.minimaxi.com/)
2. 注册/登录账号
3. 在控制台创建 API Key
4. 将 API Key 填入 `config.py`

### 3. 获取邮箱授权码

**以 163 邮箱为例：**

1. 登录 [mail.163.com](https://mail.163.com/)
2. 点击"设置" → "POP3/SMTP/IMAP"
3. 开启"SMTP服务"
4. 获取"授权码"
5. 将授权码填入 `config.py` 的 `EMAIL_PASSWORD`

**其他邮箱服务类似，需要开启 SMTP 服务并获取授权码。**

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

安装并配置完成后，当 opencode 用户询问新闻时，Agent 会自动：

1. 从多个新闻源获取当日新闻
2. 使用 AI 总结每条新闻
3. 生成口语化播报稿
4. 生成 TTS 语音文件
5. 发送邮件到指定邮箱

## 文件结构

```
├── AGENTS.md           # Agent 详细工作流程
├── SKILL.md            # Skill 元数据
├── README.md           # 本文件
├── main.py             # 主执行入口
├── config.py           # 配置文件（需用户填写）
├── news_fetcher.py     # 新闻获取模块
├── news_summarizer.py  # AI 新闻总结模块
├── generate_script.py  # 口语化主持稿生成
├── tts_generator.py    # Edge TTS 语音生成
├── mail_sender.py      # 邮件发送模块
└── requirements.txt    # Python 依赖
```

## 依赖说明

| 依赖 | 版本 | 用途 |
|------|------|------|
| httpx | >=0.25.0 | HTTP 客户端（新闻抓取）|
| beautifulsoup4 | >=4.12.0 | HTML 解析 |
| edge-tts | >=6.1.0 | 微软 TTS 语音合成 |
| pyperclip | >=1.8.0 | 剪贴板操作 |
| requests | >=2.31.0 | HTTP 请求 |

## 常见问题

### Q: 邮件发送失败？
A: 检查邮箱配置是否正确，特别是 `EMAIL_PASSWORD` 需要填写**授权码**而不是登录密码。

### Q: AI 总结失败？
A: 检查 `MINIMAX_API_KEY` 是否正确填写，或 API Key 是否已过期/额度用完。

### Q: TTS 语音生成失败？
A: 确保已安装 `edge-tts`：`pip install edge-tts`

### Q: 可以只使用部分功能吗？
A: 可以。修改 `main.py` 中的执行流程，可以单独使用新闻获取、AI总结、语音生成等模块。

## 许可证

MIT License