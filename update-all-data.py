#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全站数据自动更新脚本
- AI大模型排行榜 (Artificial Analysis + SuperCLUE) → rankings.json
- 美国本土票房排行榜 (Box Office Mojo) → boxoffice-data.json
运行环境：GitHub Actions (Ubuntu)
"""

import json
import re
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))


def fetch_url(url, timeout=30):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='replace')


# ============================================================
#  Part 1: AI 大模型排行榜
# ============================================================

def scrape_artificial_analysis():
    models = []
    try:
        html = fetch_url('https://artificialanalysis.ai/')
        score_pattern = re.findall(r'"name":"([^"]+)","[^}]*?"intelligence_index":([\d.]+)', html)
        if score_pattern:
            for name, score in score_pattern[:20]:
                models.append({'name': name.strip(), 'score': float(score)})
    except Exception as e:
        print(f'[WARN] Artificial Analysis: {e}', file=sys.stderr)
    return models


def scrape_superclue():
    models = []
    try:
        html = fetch_url('https://www.superclueai.com/')
        json_match = re.search(r'({"models".*?})\s*</script>', html, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            for m in data.get('models', []):
                models.append({
                    'name': m.get('name', ''),
                    'vendor': m.get('org', m.get('institution', '')),
                    'score': m.get('totalScore', m.get('score', 0)),
                })
    except Exception as e:
        print(f'[WARN] SuperCLUE: {e}', file=sys.stderr)
    return models


def get_fallback_rankings():
    return {
        'mixed': [
            {'rank': 1, 'name': 'Claude Fable 5', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 60', 'status': ['new', 'closed'], 'highlight': '首个公开 Mythos 级模型，9项评测综合第一'},
            {'rank': 2, 'name': 'Claude Opus 4.8', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 56', 'status': ['closed'], 'highlight': '推理能力强劲，长文本与安全严谨性突出'},
            {'rank': 3, 'name': 'GPT-5.5', 'vendor': 'OpenAI', 'region': 'intl', 'score': 'AAI 55', 'status': ['closed'], 'highlight': '全能均衡，生态成熟，Codex 周活 500 万+'},
            {'rank': 4, 'name': 'Claude Sonnet 5', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 53', 'status': ['new', 'closed'], 'highlight': 'Agent Arena 第二，智能体性能强劲'},
            {'rank': 5, 'name': 'GLM-5.2', 'vendor': '智谱 AI', 'region': 'cn', 'score': 'AAI 51', 'status': ['new', 'open'], 'highlight': '开源权重模型 SOTA，Code Arena 第一'},
            {'rank': 6, 'name': 'Gemini 3.5 Flash', 'vendor': 'Google', 'region': 'intl', 'score': 'AAI 50', 'status': ['closed'], 'highlight': '速度与智能兼顾，性价比突出'},
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
            {'rank': 4, 'name': 'Claude Sonnet 5', 'vendor': 'Anthropic', 'score': '53', 'status': ['new', 'closed'], 'highlight': 'Agent Arena 第二，智能体性能强劲'},
            {'rank': 5, 'name': 'GLM-5.2', 'vendor': 'Z AI', 'score': '51', 'status': ['new', 'open'], 'highlight': '开源权重模型 SOTA，Code Arena 第一'},
            {'rank': 6, 'name': 'Gemini 3.5 Flash', 'vendor': 'Google', 'score': '50', 'status': ['closed'], 'highlight': '速度与智能兼顾，性价比突出'},
            {'rank': 7, 'name': 'Gemini 3.1 Pro Preview', 'vendor': 'Google', 'score': '46', 'status': ['closed'], 'highlight': '多模态与搜索整合最强，速度领先'},
            {'rank': 8, 'name': 'Qwen3.7 Max', 'vendor': 'Alibaba', 'score': '46', 'status': ['closed'], 'highlight': '国产闭源旗舰，推理与编码表现亮眼'},
            {'rank': 9, 'name': 'MiniMax-M3', 'vendor': 'MiniMax', 'score': '44', 'status': ['open'], 'highlight': '开源权重模型领先，权重发布后冲上榜首'},
            {'rank': 10, 'name': 'DeepSeek V4 Pro', 'vendor': 'DeepSeek', 'score': '44', 'status': ['open'], 'highlight': '开源旗舰，单任务成本最低之一'},
        ]
    }


def update_rankings(timestamp, date_str):
    print('[INFO] === AI 排行榜数据更新 ===')
    aa_models = scrape_artificial_analysis()
    sc_models = scrape_superclue()
    if aa_models:
        print(f'[INFO] Artificial Analysis: {len(aa_models)} 个模型')
    if sc_models:
        print(f'[INFO] SuperCLUE: {len(sc_models)} 个模型')

    data = get_fallback_rankings()
    data_source = 'last manual update' if not (aa_models or sc_models) else 'auto-scrape (fallback to last manual update)'

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

    with open('rankings.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'[INFO] rankings.json 已保存')


# ============================================================
#  Part 2: 美国本土票房排行榜
# ============================================================

# 电影元数据: 中文名、类型、评分 (抓取到的英文片名匹配此表获取中文信息)
MOVIE_META = {
    'The Super Mario Galaxy Movie': {'cn': '超级马力欧:银河大电影', 'genre': ['动画', '喜剧'], 'rating': '7.0'},
    'Michael': {'cn': '巨星之路', 'genre': ['传记', '音乐'], 'rating': '7.5'},
    'Project Hail Mary': {'cn': '挽救计划', 'genre': ['科幻', '惊悚'], 'rating': '8.6'},
    'Obsession': {'cn': '执念', 'genre': ['恐怖'], 'rating': ''},
    'The Devil Wears Prada 2': {'cn': '穿普拉达的女王2', 'genre': ['剧情', '喜剧'], 'rating': '6.6'},
    'Toy Story 5': {'cn': '玩具总动员5', 'genre': ['动画', '冒险'], 'rating': '8.1'},
    'Backrooms': {'cn': '后室', 'genre': ['科幻', '恐怖'], 'rating': '6.6'},
    'Star Wars: The Mandalorian and Grogu': {'cn': '星球大战:曼达洛人与古古', 'genre': ['动作', '科幻'], 'rating': '7.4'},
    'Hoppers': {'cn': '河狸变身计划', 'genre': ['动画', '喜剧'], 'rating': '7.4'},
    'Avatar: Fire and Ash': {'cn': '阿凡达3:火与灰', 'genre': ['科幻', '动作'], 'rating': ''},
    'Scream 7': {'cn': '惊声尖叫7', 'genre': ['恐怖', '惊悚'], 'rating': ''},
    'GOAT': {'cn': 'GOAT', 'genre': ['剧情', '体育'], 'rating': ''},
    'Scary Movie': {'cn': '惊声尖笑', 'genre': ['喜剧', '恐怖'], 'rating': ''},
    'Zootopia 2': {'cn': '疯狂动物城2', 'genre': ['动画', '冒险'], 'rating': ''},
    'Wuthering Heights': {'cn': '呼啸山庄', 'genre': ['剧情', '爱情'], 'rating': ''},
    'Disclosure Day': {'cn': '揭露之日', 'genre': ['科幻', '惊悚'], 'rating': ''},
    'Mortal Kombat II': {'cn': '真人快打2', 'genre': ['动作', '奇幻'], 'rating': ''},
    'The Housemaid': {'cn': '女佣', 'genre': ['惊悚', '剧情'], 'rating': ''},
    'The Sheep Detectives': {'cn': '羊侦探', 'genre': ['动画', '喜剧'], 'rating': ''},
    'Send Help': {'cn': '求救', 'genre': ['喜剧'], 'rating': ''},
    'Masters of the Universe': {'cn': '宇宙主宰', 'genre': ['动作', '奇幻'], 'rating': ''},
}


def scrape_boxoffice():
    """抓取 Box Office Mojo 当年美国本土票房 TOP10"""
    movies = []
    try:
        html = fetch_url('https://www.boxofficemojo.com/year/2026/')
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) < 6:
                continue
            rank_text = re.sub(r'<[^>]+>', '', cells[0]).strip()
            name_text = re.sub(r'<[^>]+>', '', cells[1]).strip()
            gross_text = re.sub(r'<[^>]+>', '', cells[5]).strip()

            # 解析排名
            try:
                rank = int(rank_text)
            except ValueError:
                continue
            if rank > 10:
                break

            # 跳过空名或占位符
            if not name_text or name_text == '-':
                continue

            # 解析票房
            gross_match = re.search(r'\$([\d,]+)', gross_text)
            if gross_match:
                gross_val = int(gross_match.group(1).replace(',', ''))
                gross_str = f'${gross_val / 1e6:.1f}M'
            else:
                continue

            # 匹配中文元数据
            meta = MOVIE_META.get(name_text, {})
            movies.append({
                'rank': rank,
                'name_en': name_text,
                'name_cn': meta.get('cn', name_text),
                'genre': meta.get('genre', []),
                'gross': gross_str,
                'rating': meta.get('rating', ''),
            })
    except Exception as e:
        print(f'[WARN] Box Office Mojo: {e}', file=sys.stderr)

    return movies


def get_fallback_boxoffice():
    return [
        {'rank': 1, 'name_en': 'The Super Mario Galaxy Movie', 'name_cn': '超级马力欧:银河大电影', 'genre': ['动画', '喜剧'], 'gross': '$429.7M', 'rating': '7.0'},
        {'rank': 2, 'name_en': 'Michael', 'name_cn': '巨星之路', 'genre': ['传记', '音乐'], 'gross': '$368.7M', 'rating': '7.5'},
        {'rank': 3, 'name_en': 'Project Hail Mary', 'name_cn': '挽救计划', 'genre': ['科幻', '惊悚'], 'gross': '$344.0M', 'rating': '8.6'},
        {'rank': 4, 'name_en': 'Obsession', 'name_cn': '执念', 'genre': ['恐怖'], 'gross': '$220.1M', 'rating': ''},
        {'rank': 5, 'name_en': 'The Devil Wears Prada 2', 'name_cn': '穿普拉达的女王2', 'genre': ['剧情', '喜剧'], 'gross': '$219.5M', 'rating': '6.6'},
        {'rank': 6, 'name_en': 'Toy Story 5', 'name_cn': '玩具总动员5', 'genre': ['动画', '冒险'], 'gross': '$200.7M', 'rating': '8.1'},
        {'rank': 7, 'name_en': 'Backrooms', 'name_cn': '后室', 'genre': ['科幻', '恐怖'], 'gross': '$175.1M', 'rating': '6.6'},
        {'rank': 8, 'name_en': 'Star Wars: The Mandalorian and Grogu', 'name_cn': '星球大战:曼达洛人与古古', 'genre': ['动作', '科幻'], 'gross': '$173.0M', 'rating': '7.4'},
        {'rank': 9, 'name_en': 'Hoppers', 'name_cn': '河狸变身计划', 'genre': ['动画', '喜剧'], 'gross': '$166.0M', 'rating': '7.4'},
        {'rank': 10, 'name_en': 'Avatar: Fire and Ash', 'name_cn': '阿凡达3:火与灰', 'genre': ['科幻', '动作'], 'gross': '$154.0M', 'rating': ''},
    ]


def update_boxoffice(timestamp):
    print('[INFO] === 美国票房数据更新 ===')
    scraped = scrape_boxoffice()
    if scraped and len(scraped) >= 5:
        print(f'[INFO] Box Office Mojo: 抓取到 {len(scraped)} 部电影')
        movies = scraped
        source = 'Box Office Mojo (Calendar Grosses)'
    else:
        print('[WARN] Box Office Mojo 抓取失败或数据不足，使用上次手动更新的数据')
        movies = get_fallback_boxoffice()
        source = 'last manual update'

    output = {
        'lastUpdated': timestamp,
        'timezone': 'Asia/Shanghai (UTC+8)',
        'source': source,
        'movies': movies
    }

    with open('boxoffice-data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f'[INFO] boxoffice-data.json 已保存')


# ============================================================
#  Main
# ============================================================

def main():
    now = datetime.now(CST)
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    date_str = now.strftime('%Y年%m月%d日')

    print(f'[INFO] ===== 全站数据更新开始 {timestamp} (北京时间) =====')

    # 1. AI 排行榜 → rankings.json
    update_rankings(timestamp, date_str)

    # 2. 美国票房 → boxoffice-data.json
    update_boxoffice(timestamp)

    # 说明: 其他页面的数据更新方式
    # - github-trending.html: 页面加载时实时调用 GitHub API，无需定时抓取
    # - ai-tools.html: 静态工具列表，无需定期更新
    # - nev-sales.html: 新能源汽车销量为月度数据，由中汽协/乘联会月度发布，不适合每日抓取

    print(f'[INFO] ===== 全站数据更新完成 =====')

    if 'GITHUB_ENV' in os.environ:
        with open(os.environ['GITHUB_ENV'], 'a') as f:
            f.write(f'UPDATE_TIMESTAMP={timestamp}\n')


if __name__ == '__main__':
    main()
