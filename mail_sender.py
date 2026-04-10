# -*- coding: utf-8 -*-
"""
邮件发送模块 - 发送包含文字和语音附件的邮件
"""

import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import config


def read_file(file_path, encoding='utf-8'):
    """读取文件内容"""
    with open(file_path, 'r', encoding=encoding) as f:
        return f.read()


def send_email(subject, body_text, body_html=None, attachment_path=None):
    """
    发送邮件
    
    Args:
        subject: 邮件主题
        body_text: 邮件正文（纯文本）
        body_html: 邮件正文HTML版本（可选）
        attachment_path: 附件文件路径（可选）
    
    Returns:
        bool: 发送是否成功
    """
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = config.EMAIL_USER
    msg['To'] = config.EMAIL_TO
    msg['Subject'] = subject
    
    # 添加邮件正文（纯文本）
    if body_text:
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    
    # 添加HTML版本（可选）
    if body_html:
        msg.attach(MIMEText(body_html, 'html', 'utf-8'))
    
    # 添加附件
    if attachment_path and os.path.exists(attachment_path):
        filename = os.path.basename(attachment_path)
        
        with open(attachment_path, 'rb') as f:
            content = f.read()
        
        # 根据文件类型选择正确的MIME类型和创建附件
        if filename.endswith('.mp3'):
            # MP3 文件使用 MIMEAudio
            part = MIMEBase('audio', 'mpeg')
        else:
            # 其他文件使用通用二进制类型
            part = MIMEBase('application', 'octet-stream')
        
        part.set_payload(content)
        encoders.encode_base64(part)
        
        # 使用 RFC 2231 正确编码中文文件名
        import urllib.parse
        encoded_filename = urllib.parse.quote(filename)
        part['Content-Disposition'] = f'attachment; filename*=utf-8\'\'{encoded_filename}'
        
        msg.attach(part)
        
        print(f"已添加附件: {filename}")
    
    try:
        # 创建SMTP SSL连接
        print(f"正在连接 SMTP 服务器: {config.EMAIL_HOST}:{config.EMAIL_PORT}")
        server = smtplib.SMTP_SSL(config.EMAIL_HOST, config.EMAIL_PORT)
        
        # 登录邮箱
        print(f"正在登录邮箱: {config.EMAIL_USER}")
        server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
        
        # 发送邮件
        print(f"正在发送邮件到: {config.EMAIL_TO}")
        server.sendmail(config.EMAIL_USER, config.EMAIL_TO, msg.as_string())
        
        # 关闭连接
        server.quit()
        
        print("邮件发送成功！")
        return True
        
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        return False


def send_daily_news_email(news_file, audio_file=None):
    """
    发送每日新闻邮件
    
    Args:
        news_file: 新闻Markdown文件路径
        audio_file: 语音文件路径（可选）
    
    Returns:
        bool: 发送是否成功
    """
    # 提取日期
    filename = os.path.basename(news_file)
    date_match = filename.split('_')[0] if '_' in filename else ''
    
    # 生成邮件主题
    subject = f"{config.EMAIL_SUBJECT_PREFIX}{date_match}"
    
    # 读取新闻内容作为邮件正文
    body_text = read_file(news_file, 'utf-8')
    
    # 可选：生成简单的HTML版本
    body_html = None
    # body_html = f"""
    # <html>
    # <body>
    # <h2>{subject}</h2>
    # <pre>{body_text}</pre>
    # </body>
    # </html>
    # """
    
    # 发送邮件
    return send_email(subject, body_text, body_html, audio_file)


def main():
    """测试函数"""
    # 获取今天的日期
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 构建文件路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    news_file = os.path.join(base_dir, 'output', f'{date_str}_Daily_News.md')
    audio_file = os.path.join(base_dir, 'output', f'{date_str}_每日新闻.mp3')
    
    if os.path.exists(news_file):
        # 发送带附件的邮件
        audio = audio_file if os.path.exists(audio_file) else None
        send_daily_news_email(news_file, audio)
    else:
        print(f"新闻文件不存在: {news_file}")


if __name__ == '__main__':
    main()
