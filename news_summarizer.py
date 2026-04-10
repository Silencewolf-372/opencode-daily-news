# -*- coding: utf-8 -*-
"""
新闻总结模块 - 使用MiniMax API对新闻内容进行总结
支持MiniMax新API格式（anthropic风格）
"""

import requests
import json
import re
from typing import Dict, Optional

try:
    import config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False


class NewsSummarizer:
    """使用MiniMax API总结新闻内容"""
    
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        self.api_key = api_key or (config.MINIMAX_API_KEY if HAS_CONFIG else None)
        self.base_url = base_url or (config.MINIMAX_BASE_URL if HAS_CONFIG else "https://api.minimaxi.com/anthropic/v1")
        self.model = model or (config.MINIMAX_MODEL if HAS_CONFIG else "MiniMax-M2.7")
        self.max_tokens = config.MINIMAX_MAX_TOKENS if HAS_CONFIG else 1500
        self.session = requests.Session()
    
    def summarize(self, title: str, content: str, category: str = "综合") -> Dict:
        """
        使用AI总结新闻内容
        
        Args:
            title: 新闻标题
            content: 新闻正文内容
            category: 新闻分类
        
        Returns:
            dict: {
                "summary": "新闻简介",
                "impact": "影响分析", 
                "sources": ["来源1", "来源2"]
            }
        """
        if not self.api_key:
            return self._fallback_summary(title, category)
        
        truncated_content = content[:1500] if len(content) > 1500 else content
        
        prompt = f"""你是一个专业的新闻总结助手。请根据以下新闻内容，按照指定格式生成新闻简介和影响分析。

## 新闻信息
- 分类：{category}
- 标题：{title}

## 新闻正文
{truncated_content}

## 输出要求
请严格按照以下JSON格式返回，不要添加任何其他内容：
{{
    "summary": "新闻简介，请用5-8句话描述新闻的主要内容，包括人物、时间、地点、事件等关键信息。",
    "impact": "影响分析，请用5-8句话分析该新闻的影响意义，包括政治、经济、社会等层面。",
    "sources": ["新闻来源网站名称"]
}}

只返回JSON格式，不要有其他任何文字。"""
        
        try:
            response = self._call_api(prompt)
            if response:
                return response
            else:
                return self._fallback_summary(title, category)
        except Exception as e:
            print(f"  [WARN] AI总结失败: {str(e)}")
            return self._fallback_summary(title, category)
    
    def _call_api(self, prompt: str) -> Optional[Dict]:
        """调用MiniMax API（anthropic风格）"""
        url = f"{self.base_url}/messages"
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        try:
            response = self.session.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if response.status_code == 200:
                # 解析anthropic格式的响应
                if "content" in result:
                    for item in result["content"]:
                        if item.get("type") == "text":
                            text = item["text"]
                            return self._parse_response(text)
                
                print(f"  [WARN] API响应格式异常: {result}")
                return None
            else:
                print(f"  [ERROR] HTTP错误: {response.status_code} - {result}")
                return None
                
        except Exception as e:
            print(f"  [ERROR] API调用异常: {str(e)}")
            return None
    
    def _parse_response(self, text: str) -> Optional[Dict]:
        """解析API响应文本"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试提取JSON
            json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # 尝试提取关键字段
            summary_match = re.search(r'"summary"\s*[:：]\s*"([^"]+)"', text)
            impact_match = re.search(r'"impact"\s*[:：]\s*"([^"]+)"', text)
            
            if summary_match and impact_match:
                return {
                    "summary": summary_match.group(1),
                    "impact": impact_match.group(1),
                    "sources": ["新闻来源"]
                }
        
        return None
    
    def _fallback_summary(self, title: str, category: str) -> Dict:
        """当AI总结失败时使用的备用方案"""
        return {
            "summary": f"这是一条{category}新闻，标题为：{title}。详细内容请访问新闻来源查看。",
            "impact": f"该新闻属于{category}类别，对相关领域可能产生一定影响。",
            "sources": ["新闻来源"]
        }


def test_summarizer():
    """测试总结功能"""
    summarizer = NewsSummarizer()
    
    test_title = "美军在伊朗周边海域展开营救行动"
    test_content = """
    美军在伊朗周边海域展开了一场高风险营救行动，目标是寻找一名失踪的美国飞行员。
    此次行动导致多架美军飞机被击落，造成美军人员伤亡。伊朗方面宣称成功击落执行救援任务的运输机等多架飞机，
    损失价值超过4亿美元。这一事件标志着美伊对抗从外交层面直接升级为军事冲突。
    美军此次行动暴露了其在伊朗周边军事存在的脆弱性。伊朗方面态度强硬，表示整个中东将可能成为美以的"地狱"。
    """
    
    print("测试新闻总结功能...")
    result = summarizer.summarize(test_title, test_content, "国际政治")
    print(f"结果: {result}")
    
    return result


if __name__ == "__main__":
    test_summarizer()
