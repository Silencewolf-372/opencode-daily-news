# -*- coding: utf-8 -*-
"""
TTS语音生成模块 - 使用Edge TTS将文字转换为语音
"""

import asyncio
import os
from datetime import datetime
import edge_tts
import config


async def generate_speech(text_file, output_file=None, voice=None):
    """
    使用Edge TTS将文字文件转换为语音
    
    Args:
        text_file: 文字稿文件路径
        output_file: 输出MP3文件路径，None则自动生成
        voice: 语音名称，None则使用配置中的默认语音
    
    Returns:
        生成的MP3文件路径
    """
    # 读取文字稿
    with open(text_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 使用配置的语音
    if voice is None:
        voice = config.TTS_VOICE
    
    # 如果没有指定输出文件，自动生成
    if output_file is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
        base_dir = os.path.dirname(text_file)
        output_file = os.path.join(base_dir, f'{date_str}_每日新闻.mp3')
    
    print(f"正在生成语音，使用语音: {voice}")
    print(f"文字长度: {len(text)} 字符")
    
    # 创建Edge TTS通讯对象
    communicate = edge_tts.Communicate(text, voice)
    
    # 生成语音文件
    await communicate.save(output_file)
    
    print(f"语音文件已生成: {output_file}")
    return output_file


def generate_speech_sync(text_file, output_file=None, voice=None):
    """同步版本的语音生成"""
    return asyncio.run(generate_speech(text_file, output_file, voice))


def main():
    """测试函数"""
    # 获取今天的日期
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 构建文件路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_file = os.path.join(base_dir, 'output', f'{date_str}_News_Script.txt')
    
    if os.path.exists(script_file):
        output_file = os.path.join(base_dir, 'output', f'{date_str}_每日新闻.mp3')
        result = generate_speech_sync(script_file, output_file)
        print(f"语音文件已保存到: {result}")
    else:
        print(f"文字稿文件不存在: {script_file}")


if __name__ == '__main__':
    main()
