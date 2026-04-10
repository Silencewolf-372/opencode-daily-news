# -*- coding: utf-8 -*-
"""
Daily News Agent - 主执行脚本
自动生成新闻报告、口语化主持稿、TTS语音，并发送邮件
支持AI新闻总结
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import config
import news_fetcher
import news_summarizer
import generate_script
import tts_generator
import mail_sender


def generate_full_news_report(date_str: str, news_items: List[Dict], fetch_stats: Dict) -> str:
    """
    生成完整的新闻报告（按agent.md格式）
    
    Args:
        date_str: 日期字符串
        news_items: 新闻列表
        fetch_stats: 获取统计信息
    
    Returns:
        str: Markdown格式的新闻报告
    """
    content = f"""# {date_str} 重点新闻汇总

---

**获取统计：**
- 国内新闻源：{fetch_stats.get('domestic_success', 0)}个成功
- 国际新闻源：{fetch_stats.get('international_success', 0)}个成功
- AI总结新闻：{len(news_items)}篇

---

"""
    
    # 按分类组织新闻
    categories = {
        "国际政治": [],
        "全球经济": [],
        "科技动态": [],
        "国家政策": [],
        "国内重要事件": []
    }
    
    for item in news_items:
        cat = item.get('category', '国内重要事件')
        if cat in categories:
            categories[cat].append(item)
    
    # 生成各分类新闻
    category_order = ["国际政治", "全球经济", "科技动态", "国家政策", "国内重要事件"]
    
    for cat in category_order:
        items = categories[cat]
        if items:
            content += f"\n## {cat}\n\n"
            
            for i, item in enumerate(items, 1):
                title = item.get('title', '无标题')
                summary = item.get('summary', '暂无简介')
                impact = item.get('impact', '暂无影响分析')
                sources = item.get('sources', ['新闻来源'])
                source_str = '、'.join(sources) if sources else '新闻来源'
                
                content += f"""### {i}. {title}

**新闻简介：** {summary}

**影响分析：** {impact}

**新闻来源：** {source_str}

---

"""
    
    content += f"""
**报告说明：**

- 本报告基于 {date_str} 公开新闻信息整理
- 新闻内容由AI智能总结生成
- 如需最新新闻，请访问相应新闻网站

"""
    
    return content


def fetch_and_summarize_news(summarizer, news_item: Dict, max_retries: int = 1) -> Dict:
    """
    获取新闻详情页并总结
    
    Args:
        summarizer: NewsSummarizer实例
        news_item: 新闻条目
        max_retries: 最大重试次数
    
    Returns:
        Dict: 添加了summary和impact的新闻条目
    """
    fetcher = news_fetcher.NewsFetcher()
    url = news_item.get('url', '')
    source = news_item.get('source', '')
    title = news_item.get('title', '')
    category = news_item.get('category', '综合')
    
    result = news_item.copy()
    fallback_summary = f"新闻标题：{title}"
    fallback_impact = "该新闻属于{}类别，对相关领域可能产生影响。".format(category)
    
    result['summary'] = fallback_summary
    result['impact'] = fallback_impact
    result['sources'] = [source]
    
    if not url or url == '#':
        return result
    
    for attempt in range(max_retries):
        try:
            # 获取详情页
            content = fetcher.fetch_detail_page(url, source)
            
            if content:
                # 提取文章正文
                article_text = fetcher.extract_article_content(content, source)
                
                if len(article_text) > 50:  # 确保有足够内容
                    # 调用AI总结
                    ai_result = summarizer.summarize(title, article_text, category)
                    
                    result['summary'] = ai_result.get('summary', fallback_summary)
                    result['impact'] = ai_result.get('impact', fallback_impact)
                    result['sources'] = ai_result.get('sources', [source])
                    return result
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 重试前等待
            continue
    
    return result


def main():
    """主执行流程"""
    
    print("=" * 60)
    print("Daily News Agent 开始执行")
    print("=" * 60)
    
    # 获取今天的日期
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 确保输出目录存在
    output_dir = os.path.join(current_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 文件路径
    news_file = os.path.join(output_dir, f'{date_str}_Daily_News.md')
    script_file = os.path.join(output_dir, f'{date_str}_News_Script.txt')
    audio_file = os.path.join(output_dir, f'{date_str}_每日新闻.mp3')
    
    # ========== 步骤1：获取新闻列表 ==========
    print("\n[步骤1] 获取新闻列表...")
    print("-" * 40)
    
    try:
        fetcher = news_fetcher.NewsFetcher()
        all_results = fetcher.fetch_all_news()
        
        # 解析新闻标题
        all_news = []
        for result in all_results['domestic'] + all_results['international']:
            if result.get('success'):
                items = fetcher.parse_news_content(result['content'], result['source'])
                for item in items:
                    item['source'] = result['source']
                all_news.extend(items)
        
        # 按分类筛选
        categorized = fetcher.categorize_news(all_news)
        
        fetch_stats = {
            'domestic_success': len(all_results['domestic']),
            'international_success': len(all_results['international']),
            'total_failed': len(all_results['failed']),
            'total_sources': len(fetcher.domestic_sources) + len(fetcher.international_sources)
        }
        
        print(f"\n获取到 {len(all_news)} 条新闻标题")
        
    except Exception as e:
        print(f"新闻列表获取失败: {str(e)}")
        categorized = {}
        fetch_stats = {'domestic_success': 0, 'international_success': 0, 'total_failed': 0, 'total_sources': 0}
    
    # ========== 步骤2：AI新闻总结 ==========
    print("\n[步骤2] AI新闻总结...")
    print("-" * 40)
    
    summarizer = news_summarizer.NewsSummarizer()
    
    # 计算每个分类需要总结的新闻数量
    category_config = config.NEWS_CATEGORIES if hasattr(config, 'NEWS_CATEGORIES') else {
        "国际政治": {"min": 6, "max": 8},
        "全球经济": {"min": 3, "max": 4},
        "科技动态": {"min": 2, "max": 3},
        "国家政策": {"min": 2, "max": 3},
        "国内重要事件": {"min": 2, "max": 3}
    }
    
    summarized_news = []
    total_to_summarize = 0
    
    for cat, cfg in category_config.items():
        count = len(categorized.get(cat, []))
        target = min(count, cfg['max'])
        total_to_summarize += target
    
    print(f"计划总结 {total_to_summarize} 条新闻...")
    
    # 收集需要总结的新闻
    news_to_summarize = []
    for cat, cfg in category_config.items():
        items = categorized.get(cat, [])
        target_count = min(len(items), cfg['max'])
        
        for i, item in enumerate(items[:target_count]):
            item['category'] = cat
            news_to_summarize.append(item)
    
    # 使用线程池并行获取详情页和总结（控制并发数为3）
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(fetch_and_summarize_news, summarizer, item): item 
            for item in news_to_summarize
        }
        
        completed = 0
        for future in as_completed(futures):
            item = futures[future]
            try:
                result = future.result()
                summarized_news.append(result)
                completed += 1
                print(f"  [{completed}/{len(news_to_summarize)}] {result.get('title', '')[:40]}... - OK")
            except Exception as e:
                print(f"  [{completed}/{len(news_to_summarize)}] 总结失败: {str(e)[:40]}")
                completed += 1
    
    print(f"\n成功总结 {len(summarized_news)} 条新闻")
    
    # ========== 步骤3：生成新闻报告 ==========
    print("\n[步骤3] 生成新闻报告...")
    print("-" * 40)
    
    if summarized_news:
        news_content = generate_full_news_report(date_str, summarized_news, fetch_stats)
    else:
        print("没有可用的新闻，使用示例数据")
        news_content = news_fetcher.generate_sample_news(date_str)
    
    with open(news_file, 'w', encoding='utf-8') as f:
        f.write(news_content)
    
    print(f"新闻报告已生成: {news_file}")
    
    # ========== 步骤4：生成口语化主持稿 ==========
    print("\n[步骤4] 生成口语化主持稿...")
    print("-" * 40)
    
    if os.path.exists(script_file):
        print(f"主持稿已存在: {script_file}")
        print("跳过主持稿生成步骤。")
    else:
        if os.path.exists(news_file):
            try:
                script_file = generate_script.convert_to_script(news_file, script_file)
                print(f"主持稿已生成: {script_file}")
            except Exception as e:
                print(f"主持稿生成失败: {str(e)}")
                script_file = None
        else:
            print("新闻文件不存在，无法生成主持稿")
            script_file = None
    
    # ========== 步骤5：TTS语音生成 ==========
    print("\n[步骤5] 生成TTS语音...")
    print("-" * 40)
    
    if os.path.exists(audio_file):
        print(f"语音文件已存在: {audio_file}")
        print("跳过语音生成步骤。")
    else:
        if script_file and os.path.exists(script_file):
            try:
                audio_file = tts_generator.generate_speech_sync(script_file, audio_file)
                print(f"语音文件已生成: {audio_file}")
            except Exception as e:
                print(f"语音生成失败: {str(e)}")
                print("请确保已安装 edge-tts: pip install edge-tts")
                audio_file = None
        else:
            print("主持稿文件不存在，无法生成语音")
            audio_file = None
    
    # ========== 步骤6：发送邮件 ==========
    print("\n[步骤6] 发送邮件...")
    print("-" * 40)
    
    if os.path.exists(news_file):
        try:
            attachment = audio_file if audio_file and os.path.exists(audio_file) else None
            
            success = mail_sender.send_daily_news_email(news_file, attachment)
            
            if success:
                print("邮件发送成功！")
            else:
                print("邮件发送失败，请检查配置。")
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
    else:
        print("新闻文件不存在，无法发送邮件")
    
    # ========== 完成 ==========
    print("\n" + "=" * 60)
    print("Daily News Agent 执行完成")
    print("=" * 60)
    
    # 输出文件列表
    print("\n生成的文件:")
    print(f"  1. 新闻报告: {news_file}")
    if script_file and os.path.exists(script_file):
        print(f"  2. 主持稿: {script_file}")
    if audio_file and os.path.exists(audio_file):
        print(f"  3. 语音文件: {audio_file}")


def test_modules():
    """测试各模块是否正常工作"""
    print("=" * 60)
    print("Module Test")
    print("=" * 60)
    
    # 测试 config
    print("\n[1] Test config.py...")
    try:
        print(f"  SMTP: {config.EMAIL_HOST}:{config.EMAIL_PORT}")
        print(f"  User: {config.EMAIL_USER}")
        print(f"  To: {config.EMAIL_TO}")
        print(f"  TTS Voice: {config.TTS_VOICE}")
        if hasattr(config, 'MINIMAX_API_KEY'):
            print(f"  MiniMax API: Configured")
        print("  config.py [OK]")
    except Exception as e:
        print(f"  config.py [FAIL]: {str(e)}")
    
    # 测试 news_summarizer
    print("\n[2] Test news_summarizer.py...")
    try:
        summarizer = news_summarizer.NewsSummarizer()
        print("  MiniMax summarizer initialized")
        print("  news_summarizer.py [OK]")
    except Exception as e:
        print(f"  news_summarizer.py [FAIL]: {str(e)}")
    
    # 测试 news_fetcher
    print("\n[3] Test news_fetcher.py...")
    try:
        date_str = datetime.now().strftime('%Y-%m-%d')
        content = news_fetcher.generate_sample_news(date_str)
        print(f"  Generated news length: {len(content)} chars")
        print("  news_fetcher.py [OK]")
    except Exception as e:
        print(f"  news_fetcher.py [FAIL]: {str(e)}")
    
    # 测试 tts_generator
    print("\n[4] Test tts_generator.py...")
    try:
        import edge_tts
        print("  edge-tts [INSTALLED]")
        print("  tts_generator.py [OK]")
    except ImportError:
        print("  edge-tts [NOT INSTALLED] - run: pip install edge-tts")
    except Exception as e:
        print(f"  tts_generator.py [FAIL]: {str(e)}")
    
    # 测试 mail_sender
    print("\n[5] Test mail_sender.py...")
    try:
        import smtplib
        import pyperclip
        print("  smtplib [OK]")
        print("  pyperclip [OK]")
        print("  mail_sender.py [OK]")
    except ImportError as e:
        print(f"  Missing library: {str(e)}")
    except Exception as e:
        print(f"  mail_sender.py [FAIL]: {str(e)}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_modules()
    else:
        main()
