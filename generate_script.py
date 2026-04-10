# -*- coding: utf-8 -*-
"""
主持稿生成模块 - 将Markdown新闻转换为口语化播报稿
"""

import re
import os
from datetime import datetime
import config


def remove_markdown_formatting(text):
    """去除Markdown格式标记"""
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        # 跳过Markdown标题标记（#, ##, ###等）
        line = re.sub(r'^#{1,6}\s+', '', line)
        
        # 去除加粗标记 **text**
        line = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
        
        # 去除斜体标记 *text* 或 _text_
        line = re.sub(r'\*(.*?)\*', r'\1', line)
        line = re.sub(r'_(.*?)_', r'\1', line)
        
        # 去除链接 [text](url)
        line = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', line)
        
        # 去除图片 ![alt](url)
        line = re.sub(r'!\[.*?\]\(.*?\)', '', line)
        
        # 去除代码标记 `code`
        line = re.sub(r'`(.*?)`', r'\1', line)
        
        # 去除HTML标签
        line = re.sub(r'<.*?>', '', line)
        
        # 去除"新闻简介："、"影响分析："、"新闻来源："等标签词
        line = re.sub(r'新闻简介[：:]*', '', line)
        line = re.sub(r'影响分析[：:]*', '', line)
        line = re.sub(r'新闻来源[：:]*', '', line)
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def clean_punctuation(text):
    """根据规则清理标点符号"""
    result = []
    for char in text:
        if char in config.PUNCTUATION_RULES:
            if config.PUNCTUATION_RULES[char]:
                if char == '；':
                    result.append('。')
                else:
                    result.append(char)
        else:
            result.append(char)
    
    return ''.join(result)


def extract_category(text):
    """提取当前栏目名称"""
    # 匹配 "一、国际政治" 或 "## 国际政治" 等格式
    match = re.search(r'[#\d\s]*([\u4e00-\u9fa5]{2,6})(?:新闻|动态|事件|方面)', text)
    if match:
        return match.group(1)
    return None


def add_transitions(text):
    """在栏目开始处添加过渡语"""
    lines = text.split('\n')
    result_lines = []
    current_category = None
    categories_found = set()
    
    # 定义栏目关键词和对应的过渡语
    category_keywords = {
        '国际政治': '好的，现在为您播报今天的重点新闻，首先是国际政治方面。',
        '全球经济': '接下来我们来看看全球经济的动态。',
        '科技动态': '科技领域今天有什么新消息呢，让我们一起来了解。',
        '国家政策': '现在为您解读今天的政策动态。',
        '国内重要事件': '最后让我们关注一下国内的最新消息。',
    }
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # 检测栏目标题（如 "一、国际政治" 或 "## 全球经济"）
        category_match = re.match(r'^([一二三四五六七八九十]+)[、.]\s*([\u4e00-\u9fa5]{2,6})(?:新闻|动态|事件)?', stripped)
        if category_match:
            current_category = category_match.group(2)
            # 如果有对应的过渡语，则添加
            if current_category in category_keywords:
                result_lines.append('')
                result_lines.append(category_keywords[current_category])
                result_lines.append('')
            result_lines.append(line)
            categories_found.add(current_category)
            continue
        
        # 检测简单栏目标题（如 "## 全球经济"）
        for cat_name in category_keywords.keys():
            if cat_name in stripped and len(stripped) < 10:
                if cat_name not in categories_found:
                    categories_found.add(cat_name)
                    result_lines.append('')
                    result_lines.append(category_keywords[cat_name])
                    result_lines.append('')
                break
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def process_text_content(text):
    """处理文字内容，清理不需要的符号"""
    # 保留的文字内容处理
    text = clean_punctuation(text)
    
    # 将多个空白字符替换为单个空格
    text = re.sub(r'\s+', ' ', text)
    
    # 清理多余的空格
    text = re.sub(r'\s+([，。、！？])', r'\1', text)
    text = re.sub(r'([，。、！？])\s+', r'\1', text)
    
    return text


def convert_to_script(markdown_file, output_file=None):
    """
    将Markdown新闻文件转换为口语化主持稿
    
    Args:
        markdown_file: Markdown文件路径
        output_file: 输出主持稿文件路径，None则自动生成
    
    Returns:
        主持稿文件路径
    """
    # 读取Markdown文件
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去除Markdown格式
    content = remove_markdown_formatting(content)
    
    # 添加过渡语
    content = add_transitions(content)
    
    # 处理文字内容
    content = process_text_content(content)
    
    # 清理多余的空行
    lines = [line for line in content.split('\n') if line.strip()]
    content = '\n'.join(lines)
    
    # 生成主持稿
    script_content = []
    
    # 添加开场白（如果配置了）
    if config.INTRO:
        script_content.append(config.INTRO)
        script_content.append('')
    
    script_content.append(content)
    
    # 添加结束语（如果配置了）
    if config.OUTRO:
        script_content.append('')
        script_content.append(config.OUTRO)
    
    final_script = '\n'.join(script_content)
    
    # 如果没有指定输出文件，自动生成
    if output_file is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
        base_dir = os.path.dirname(markdown_file)
        output_file = os.path.join(base_dir, f'{date_str}_News_Script.txt')
    
    # 保存主持稿
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_script)
    
    print(f"主持稿已生成: {output_file}")
    return output_file


def main():
    """测试函数"""
    # 获取今天的日期
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 构建文件路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    news_file = os.path.join(base_dir, 'output', f'{date_str}_Daily_News.md')
    
    if os.path.exists(news_file):
        output_file = os.path.join(base_dir, 'output', f'{date_str}_News_Script.txt')
        result = convert_to_script(news_file, output_file)
        print(f"主持稿已保存到: {result}")
    else:
        print(f"新闻文件不存在: {news_file}")


if __name__ == '__main__':
    main()
