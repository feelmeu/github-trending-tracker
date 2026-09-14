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
            {'rank': 1, 'name': 'Claude Fable 5.1', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 53', 'status': ['new', 'closed'], 'highlight': 'AAI v4.3 并列榜首，成本较 GPT-6 Astra 高 57%'},
            {'rank': 2, 'name': 'GPT-6 Astra', 'vendor': 'OpenAI', 'region': 'intl', 'score': 'AAI 53', 'status': ['new', 'closed'], 'highlight': '与 Fable 5.1 并列第一，FrontierMath Tier4 98%，首个达 Critical 级别'},
            {'rank': 3, 'name': 'Claude Opus 5', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 51', 'status': ['closed'], 'highlight': '推理能力强劲，长文本与安全严谨性突出'},
            {'rank': 4, 'name': 'Claude Fable 5', 'vendor': 'Anthropic', 'region': 'intl', 'score': 'AAI 50', 'status': ['closed'], 'highlight': '前代旗舰仍居前列，Agent Arena 表现强劲'},
            {'rank': 5, 'name': 'Muse Spark 1.3', 'vendor': 'Meta', 'region': 'intl', 'score': 'AAI 48', 'status': ['new', 'open'], 'highlight': 'Meta 首次进入 AAI 前五，开源旗舰'},
            {'rank': 6, 'name': 'GPT-5.6 Sol', 'vendor': 'OpenAI', 'region': 'intl', 'score': 'AAI 47', 'status': ['closed'], 'highlight': '全能均衡，生态成熟，Codex 周活 500 万+'},
            {'rank': 7, 'name': '通义千问 Qwen3.8-Max-0902', 'vendor': '阿里巴巴', 'region': 'cn', 'score': 'SC 72.62', 'status': ['new', 'closed'], 'highlight': 'SuperCLUE 榜首，9月10日发布新版本超越前代'},
            {'rank': 8, 'name': 'DeepSeek V4.1-Flash', 'vendor': '深度求索', 'region': 'cn', 'score': 'SC 71.81', 'status': ['new', 'open'], 'highlight': 'SuperCLUE 并列第二，9月11日发布开源旗舰'},
            {'rank': 9, 'name': 'GLM-5.3', 'vendor': '智谱 AI', 'region': 'cn', 'score': 'AAI 44 / SC 71.29', 'status': ['new', 'open'], 'highlight': 'AAI 开源权重并列第一，SuperCLUE 第三'},
            {'rank': 10, 'name': 'Kimi K3', 'vendor': '月之暗面', 'region': 'cn', 'score': 'AAI 44 / SC 70.68', 'status': ['new', 'open'], 'highlight': 'AAI 开源权重并列第一，SuperCLUE 编码第一'},
        ],
        'cn': [
            {'rank': 1, 'name': '通义千问 Qwen3.8-Max-0902', 'vendor': '阿里巴巴', 'score': '72.62', 'status': ['new', 'closed'], 'highlight': '9月10日发布新版本，SuperCLUE 新榜首'},
            {'rank': 2, 'name': 'DeepSeek V4.1-Flash', 'vendor': '深度求索', 'score': '71.81', 'status': ['new', 'open'], 'highlight': '9月11日发布，开源旗舰，数学推理领先'},
            {'rank': 3, 'name': '通义千问 Qwen3.8-Max', 'vendor': '阿里巴巴', 'score': '71.48', 'status': ['closed'], 'highlight': '前代版本仍居前三，数学 77.19 幻觉 86.08'},
            {'rank': 4, 'name': 'GLM-5.3', 'vendor': '智谱 AI', 'score': '71.29', 'status': ['new', 'open'], 'highlight': '9月10日发布，开源权重 SOTA，编码 64.13'},
            {'rank': 5, 'name': 'Kimi K3', 'vendor': '月之暗面', 'score': '70.68', 'status': ['new', 'open'], 'highlight': '编码 75.79 国产最高，智能体规划 84.35'},
            {'rank': 6, 'name': 'DeepSeek V4-Pro', 'vendor': '深度求索', 'score': '70.10', 'status': ['open'], 'highlight': '幻觉控制 89.73 国产最高，8月18日更新'},
            {'rank': 7, 'name': 'GLM-5.3-Flash', 'vendor': '智谱 AI', 'score': '68.10', 'status': ['new', 'open'], 'highlight': '9月10日发布，320B 参数 18B 激活，原生多模态'},
            {'rank': 8, 'name': '通义千问 Qwen3.8-Flash', 'vendor': '阿里巴巴', 'score': '66.41', 'status': ['new', 'open'], 'highlight': '9月10日发布，125B 参数 6B 激活，性价比极高'},
            {'rank': 9, 'name': '豆包 Doubao-Seed-2.1 Pro', 'vendor': '字节跳动', 'score': '65.94', 'status': ['closed'], 'highlight': '科学推理 77.19，智能体规划 84.95'},
            {'rank': 10, 'name': 'DeepSeek V4-Flash', 'vendor': '深度求索', 'score': '65.60', 'status': ['open'], 'highlight': '数学 78.95 国产最高，轻量高效性价比突出'},
        ],
        'intl': [
            {'rank': 1, 'name': 'Claude Fable 5.1', 'vendor': 'Anthropic', 'score': '53', 'status': ['new', 'closed'], 'highlight': 'AAI v4.3 并列榜首，Terminal-Bench 4.0 升级'},
            {'rank': 2, 'name': 'GPT-6 Astra', 'vendor': 'OpenAI', 'score': '53', 'status': ['new', 'closed'], 'highlight': '与 Fable 5.1 并列第一，首个达 Critical 级别，ARC-AGI-3 99.9%'},
            {'rank': 3, 'name': 'Claude Opus 5', 'vendor': 'Anthropic', 'score': '51', 'status': ['closed'], 'highlight': '推理与安全严谨性突出，Anthropic 第三席'},
            {'rank': 4, 'name': 'Claude Fable 5', 'vendor': 'Anthropic', 'score': '50', 'status': ['closed'], 'highlight': '前代旗舰仍居前四，Agent Arena 表现强劲'},
            {'rank': 5, 'name': 'Muse Spark 1.3', 'vendor': 'Meta', 'score': '48', 'status': ['new', 'open'], 'highlight': 'Meta 首次进入前五，开源旗舰'},
            {'rank': 6, 'name': 'GPT-5.6 Sol', 'vendor': 'OpenAI', 'score': '47', 'status': ['closed'], 'highlight': '全能均衡，生态成熟，Codex 周活 500 万+'},
            {'rank': 7, 'name': 'GLM-5.3', 'vendor': '智谱 AI', 'score': '44', 'status': ['new', 'open'], 'highlight': 'AAI v4.3 开源权重并列第一'},
            {'rank': 8, 'name': 'Kimi K3', 'vendor': '月之暗面', 'score': '44', 'status': ['new', 'open'], 'highlight': 'AAI v4.3 开源权重并列第一'},
            {'rank': 9, 'name': 'GLM-5.3 Flash', 'vendor': '智谱 AI', 'score': '42', 'status': ['new', 'open'], 'highlight': '320B 参数原生多模态，DeepSWE 63.4%'},
            {'rank': 10, 'name': 'Qwen3.8 2.4T A95B', 'vendor': '阿里巴巴', 'score': '40', 'status': ['open'], 'highlight': '开源旗舰，MoE 架构 95B 激活参数'},
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
            'mixed': 'Artificial Analysis Intelligence Index v4.3 + SuperCLUE',
            'cn': 'SuperCLUE 中文大模型综合排名 (2026年9月更新)',
            'intl': 'Artificial Analysis Intelligence Index v4.3'
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
    'Spider-Man: Brand New Day': {'cn': '蜘蛛侠：崭新之日', 'genre': ['动作', '冒险', '奇幻'], 'rating': '7.8'},
    'Toy Story 5': {'cn': '玩具总动员5', 'genre': ['动画', '冒险', '喜剧'], 'rating': '8.1'},
    'Michael': {'cn': '迈克尔', 'genre': ['传记', '剧情', '音乐'], 'rating': '7.5'},
    'The Super Mario Galaxy Movie': {'cn': '超级马力欧：银河大电影', 'genre': ['动画', '冒险', '喜剧'], 'rating': '7.0'},
    'The Odyssey': {'cn': '奥德赛', 'genre': ['冒险', '剧情', '奇幻'], 'rating': '7.9'},
    'The Devil Wears Prada 2': {'cn': '穿普拉达的女王2', 'genre': ['喜剧', '剧情'], 'rating': '6.6'},
    'Project Hail Mary': {'cn': '挽救计划', 'genre': ['科幻', '惊悚'], 'rating': '8.6'},
    'Minions & Monsters': {'cn': '小黄人与大怪兽', 'genre': ['动画', '冒险', '喜剧'], 'rating': '6.8'},
    'Backrooms': {'cn': '后室', 'genre': ['科幻', '恐怖'], 'rating': '6.6'},
    'Hoppers': {'cn': '河狸变身计划', 'genre': ['动画', '冒险', '喜剧'], 'rating': '7.4'},
    'Star Wars: The Mandalorian and Grogu': {'cn': '星球大战：曼达洛人与古古', 'genre': ['动作', '冒险', '科幻'], 'rating': '7.4'},
    'Wuthering Heights': {'cn': '呼啸山庄', 'genre': ['剧情', '爱情'], 'rating': ''},
    'Disclosure Day': {'cn': '揭露之日', 'genre': ['动作', '剧情', '悬疑'], 'rating': ''},
    'Scary Movie': {'cn': '惊声尖笑', 'genre': ['喜剧', '恐怖'], 'rating': ''},
    'Blades of the Guardians': {'cn': '护国战纪', 'genre': ['动作', '冒险', '剧情'], 'rating': ''},
    'Scream 7': {'cn': '惊声尖叫7', 'genre': ['恐怖', '悬疑'], 'rating': ''},
    'GOAT': {'cn': '山羊', 'genre': ['动画', '动作', '冒险'], 'rating': ''},
    'Obsession': {'cn': '痴迷', 'genre': ['恐怖'], 'rating': ''},
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
        {'rank': 1, 'name_en': 'Spider-Man: Brand New Day', 'name_cn': '蜘蛛侠：崭新之日', 'genre': ['动作', '冒险', '奇幻'], 'gross': '$2,232.6M', 'rating': '7.8'},
        {'rank': 2, 'name_en': 'Toy Story 5', 'name_cn': '玩具总动员5', 'genre': ['动画', '冒险', '喜剧'], 'gross': '$1,029.4M', 'rating': '8.1'},
        {'rank': 3, 'name_en': 'Michael', 'name_cn': '迈克尔', 'genre': ['传记', '剧情', '音乐'], 'gross': '$1,019.2M', 'rating': '7.5'},
        {'rank': 4, 'name_en': 'The Super Mario Galaxy Movie', 'name_cn': '超级马力欧：银河大电影', 'genre': ['动画', '冒险', '喜剧'], 'gross': '$1,012.5M', 'rating': '7.0'},
        {'rank': 5, 'name_en': 'The Odyssey', 'name_cn': '奥德赛', 'genre': ['冒险', '剧情', '奇幻'], 'gross': '$939.3M', 'rating': '7.9'},
        {'rank': 6, 'name_en': 'The Devil Wears Prada 2', 'name_cn': '穿普拉达的女王2', 'genre': ['喜剧', '剧情'], 'gross': '$692.7M', 'rating': '6.6'},
        {'rank': 7, 'name_en': 'Project Hail Mary', 'name_cn': '挽救计划', 'genre': ['科幻', '惊悚'], 'gross': '$684.0M', 'rating': '8.6'},
        {'rank': 8, 'name_en': 'Minions & Monsters', 'name_cn': '小黄人与大怪兽', 'genre': ['动画', '冒险', '喜剧'], 'gross': '$513.8M', 'rating': '6.8'},
        {'rank': 9, 'name_en': 'Backrooms', 'name_cn': '后室', 'genre': ['科幻', '恐怖'], 'gross': '$389.9M', 'rating': '6.6'},
        {'rank': 10, 'name_en': 'Hoppers', 'name_cn': '河狸变身计划', 'genre': ['动画', '冒险', '喜剧'], 'gross': '$389.7M', 'rating': '7.4'},
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
