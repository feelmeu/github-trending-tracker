#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 大模型排行榜数据抓取脚本
数据来源：Artificial Analysis Intelligence Index, SuperCLUE
运行环境：GitHub Actions (Ubuntu)
输出：rankings.json
"""

import json
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

#北京时间
CST = timezone(timedelta(hours=8))

def fetch_url(url, timeout=30):
    """获取URL内容"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='replace')

def scrape_artificial_analysis():
    """抓取 Artificial Analysis Intelligence Index 排行榜"""
    models = []
    try:
        html = fetch_url('https://artificialanalysis.ai/')
        # 提取模型名称和分数
        # 页面中的数据格式：模型名后跟分数
        # 尝试从 Intelligence Index 部分提取
        # 查找模型列表模式
        patterns = [
            # 匹配模型卡片中的名称
            r'data-model-name="([^"]+)"[^]*?data-score="([\d.]+)"',
        ]

        # 提取所有模型名称
        model_names = re.findall(r'href="/models/([a-z0-9\-]+)"[^>]*>([^<]+)</a>', html, re.IGNORECASE)

        # 尝试从图表数据中提取
        # Intelligence Index 数据通常在 JavaScript 变量中
        score_pattern = re.findall(r'"name":"([^"]+)","[^}]*?"intelligence_index":([\d.]+)', html)

        if score_pattern:
            for name, score in score_pattern[:20]:
                models.append({
                    'name': name.strip(),
                    'score': float(score),
                    'source': 'Artificial Analysis Intelligence Index v4.1'
                })
    except Exception as e:
        print(f'[WARN] Artificial Analysis scrape failed: {e}', file=sys.stderr)

    return models

def scrape_superclue():
    """抓取 SuperCLUE 中文大模型排行榜"""
    models = []
    try:
        html = fetch_url('https://www.superclueai.com/')
        # SuperCLUE 页面包含表格数据
        # 提取模型名称、机构和总分
        # 查找表格行中的数据
        # 格式：模型名称 | 机构 | 开/闭源 | 总分 | ...

        # 尝试提取 JSON 数据（页面可能内嵌数据）
        json_match = re.search(r'({"models".*?})\s*</script>', html, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            for m in data.get('models', []):
                models.append({
                    'name': m.get('name', ''),
                    'vendor': m.get('org', m.get('institution', '')),
                    'score': m.get('totalScore', m.get('score', 0)),
                    'source': 'SuperCLUE'
                })

        # 如果JSON提取失败，尝试从表格HTML提取
        if not models:
            # 匹配表格行
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
            for row in rows:
                cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
                cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                if len(cells) >= 5:
                    # 尝试识别模型名和分数
                    name = cells[1] if len(cells) > 1 else ''
                    vendor = cells[2] if len(cells) > 2 else ''
                    score_str = cells[4] if len(cells) > 4 else ''
                    try:
                        score = float(score_str)
                        if score > 0 and name:
                            models.append({
                                'name': name,
                                'vendor': vendor,
                                'score': score,
                                'source': 'SuperCLUE'
                            })
                    except ValueError:
                        pass
    except Exception as e:
        print(f'[WARN] SuperCLUE scrape failed: {e}', file=sys.stderr)

    return models

def get_fallback_data():
    """如果抓取失败，返回上次手动更新的静态数据"""
    return {
        'mixed': [
            {'rank': 1, 'name': 'Claude Fable 5', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 60', 'status': ['new', 'closed'], 'highlight': '首个公开 Mythos 级模型，9项评测综合第一'},
            {'rank': 2, 'name': 'Claude Opus 4.8', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 56', 'status': ['closed'], 'highlight': '推理能力强劲，长文本与安全严谨性突出'},
            {'rank': 3, 'name': 'GPT-5.5', 'vendor': 'OpenAI', 'region': 'intl', 'score': 'AAI 55', 'status': ['closed'], 'highlight': '全能均衡，生态成熟，Codex 周活 500 万+'},
            {'rank': 4, 'name': 'GLM-5.2', 'vendor': '智谱 AI', 'region': 'cn', 'score': 'AAI 51', 'status': ['new', 'open'], 'highlight': '开源权重模型 SOTA，全球第四，编程第4'},
            {'rank': 5, 'name': 'Gemini 3.5 Flash', 'vendor': 'Google', 'region': 'intl', 'score': 'AAI 50', 'status': ['closed'], 'highlight': '速度与智能兼顾，性价比突出'},
            {'rank': 6, 'name': 'Claude Sonnet 4.6', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 47', 'status': ['closed'], 'highlight': '自适应推理，编码与智能体能力均衡'},
            {'rank': 7, 'name': 'Gemini 3.1 Pro Preview', 'vendor': 'Google', 'region': 'intl', 'score': 'AAI 46', 'status': ['closed'], 'highlight': '多模态与搜索整合最强，速度领先'},
            {'rank': 8, 'name': '通义千问 Qwen3.7-Max', 'vendor': '阿里巴巴', 'region': 'cn', 'score': 'AAI 46 / SC 70.22', 'status': ['closed'], 'highlight': '国产闭源旗舰，数学 82.46 并列最高'},
            {'rank': 9, 'name': 'DeepSeek V4-Pro', 'vendor': '深度求索', 'region': 'cn', 'score': 'AAI 44 / SC 70.48', 'status': ['open'], 'highlight': '国产开源第一，单任务成本最低之一'},
            {'rank': 10, 'name': 'MiniMax M3', 'vendor': '稀宇科技', 'region': 'cn', 'score': 'AAI 44 / SC 60.37', 'status': ['open'], 'highlight': '开源模型，权重发布后冲上 AAI 榜首'},
        ],
        'cn': [
            {'rank': 1, 'name': 'DeepSeek V4-Pro', 'vendor': '深度求索', 'score': '70.48', 'status': ['open'], 'highlight': '国产开源第一，数学 71.93，智能体 78.12'},
            {'rank': 2, 'name': '通义千问 Qwen3.7-Max', 'vendor': '阿里巴巴', 'score': '70.22', 'status': ['closed'], 'highlight': '数学 82.46 并列最高，科学推理 73.68'},
            {'rank': 3, 'name': '豆包 Doubao-Seed-2.0 Pro', 'vendor': '字节跳动', 'score': '69.96', 'status': ['closed'], 'highlight': '科学推理 75.44，智能体 75.77 表现稳定'},
            {'rank': 4, 'name': 'Kimi K2.6', 'vendor': '月之暗面', 'score': '68.66', 'status': ['open'], 'highlight': '智能体 80.95 国产最高，代码 75.79'},
            {'rank': 5, 'name': 'DeepSeek V4-Flash', 'vendor': '深度求索', 'score': '67.49', 'status': ['open'], 'highlight': '数学 82.69 国产最高，轻量高效'},
            {'rank': 6, 'name': '通义千问 Qwen3.6-Max', 'vendor': '阿里巴巴', 'score': '67.04', 'status': ['closed'], 'highlight': '幻觉控制 85.14，智能体 83.41'},
            {'rank': 7, 'name': '豆包 Doubao-Seed-2.0 Lite', 'vendor': '字节跳动', 'score': '66.12', 'status': ['closed'], 'highlight': '轻量版性价比突出，科学推理 71.93'},
            {'rank': 8, 'name': 'GLM-5.1', 'vendor': '智谱 AI', 'score': '63.24', 'status': ['open'], 'highlight': '开源模型稳定表现，代码 70.80'},
            {'rank': 9, 'name': '文心一言 ERNIE 5.1', 'vendor': '百度', 'score': '63.12', 'status': ['closed'], 'highlight': '指令遵循 47.62，中文理解能力强'},
            {'rank': 10, 'name': 'MiniMax M3', 'vendor': '稀宇科技', 'score': '60.37', 'status': ['open'], 'highlight': '开源模型，智能体 75.91 表现突出'},
        ],
        'intl': [
            {'rank': 1, 'name': 'Claude Fable 5', 'vendor': 'Anthropic', 'score': '60', 'status': ['new', 'closed'], 'highlight': '首个公开 Mythos 级模型，9项评测综合第一'},
            {'rank': 2, 'name': 'Claude Opus 4.8', 'vendor': 'Anthropic', 'score': '56', 'status': ['closed'], 'highlight': '推理能力强劲，长文本与安全严谨性突出'},
            {'rank': 3, 'name': 'GPT-5.5', 'vendor': 'OpenAI', 'score': '55', 'status': ['closed'], 'highlight': '全能均衡，生态成熟，Codex 周活 500 万+'},
            {'rank': 4, 'name': 'GLM-5.2', 'vendor': 'Z AI', 'score': '51', 'status': ['new', 'open'], 'highlight': '开源权重模型 SOTA，全球第四'},
            {'rank': 5, 'name': 'Gemini 3.5 Flash', 'vendor': 'Google', 'score': '50', 'status': ['closed'], 'highlight': '速度与智能兼顾，性价比突出'},
            {'rank': 6, 'name': 'Claude Sonnet 4.6', 'vendor': 'Anthropic', 'score': '47', 'status': ['closed'], 'highlight': '自适应推理，编码与智能体能力均衡'},
            {'rank': 7, 'name': 'Gemini 3.1 Pro Preview', 'vendor': 'Google', 'score': '46', 'status': ['closed'], 'highlight': '多模态与搜索整合最强，速度领先'},
            {'rank': 8, 'name': 'Qwen3.7 Max', 'vendor': 'Alibaba', 'score': '46', 'status': ['closed'], 'highlight': '国产闭源旗舰，推理与编码表现亮眼'},
            {'rank': 9, 'name': 'MiniMax-M3', 'vendor': 'MiniMax', 'score': '44', 'status': ['open'], 'highlight': '开源权重模型领先，权重发布后冲上榜首'},
            {'rank': 10, 'name': 'DeepSeek V4 Pro', 'vendor': 'DeepSeek', 'score': '44', 'status': ['open'], 'highlight': '开源旗舰，单任务成本最低之一'},
        ]
    }

def main():
    now = datetime.now(CST)
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    date_str = now.strftime('%Y年%m月%d日')

    print(f'[INFO] 开始抓取排行榜数据 - {timestamp} (北京时间)')

    # 尝试抓取
    aa_models = []
    sc_models = []
    scrape_success = False

    try:
        aa_models = scrape_artificial_analysis()
        if aa_models:
            print(f'[INFO] Artificial Analysis: 获取到 {len(aa_models)} 个模型')
            scrape_success = True
    except Exception as e:
        print(f'[ERROR] Artificial Analysis 抓取失败: {e}', file=sys.stderr)

    try:
        sc_models = scrape_superclue()
        if sc_models:
            print(f'[INFO] SuperCLUE: 获取到 {len(sc_models)} 个模型')
            scrape_success = True
    except Exception as e:
        print(f'[ERROR] SuperCLUE 抓取失败: {e}', file=sys.stderr)

    # 使用抓取到的数据或回退数据
    if scrape_success and (aa_models or sc_models):
        # 这里可以添加将抓取数据转换为统一格式的逻辑
        # 目前先使用回退数据，因为网页结构解析可能不稳定
        print('[INFO] 抓取成功，但使用上次手动更新的稳定数据（网页结构可能变化）')
        data = get_fallback_data()
        data_source = 'auto-scrape (fallback to last manual update)'
    else:
        print('[WARN] 所有抓取均失败，使用上次手动更新的静态数据')
        data = get_fallback_data()
        data_source = 'last manual update'

    output = {
        'lastUpdated': timestamp,
        'timezone': 'Asia/Shanghai (UTC+8)',
        'dateStr': date_str,
        'dataSource': data_source,
        'sources': {
            'mixed': 'Artificial Analysis Intelligence Index v4.1 + SuperCLUE',
            'cn': 'SuperCLUE 中文大模型综合排名 (2026年5月测评)',
            'intl': 'Artificial Analysis Intelligence Index v4.1'
        },
        'rankings': data
    }

    output_path = 'rankings.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'[INFO] 数据已保存到 {output_path}')
    print(f'[INFO] 抓取时间: {timestamp}')

    # 同时输出到 GitHub Actions 环境变量
    if 'GITHUB_ENV' in __import__('os').environ:
        with open(__import__('os').environ['GITHUB_ENV'], 'a') as f:
            f.write(f'SCRAPE_TIMESTAMP={timestamp}\n')

if __name__ == '__main__':
    main()
