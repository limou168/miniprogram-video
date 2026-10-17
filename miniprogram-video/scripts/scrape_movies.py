"""
豆瓣电影爬虫 v2 — 从 Top250 列表页直接获取完整影视元数据
输出: SQL INSERT 语句，可直接导入 video_platform 数据库
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

CATEGORY_MAP = {
    '电影': 1, '电视剧': 2, '动漫': 3, '综艺': 4, '纪录片': 5,
}

# 豆瓣分类关键字 -> 我们的分类
CATEGORY_KEYWORDS = {
    2: ['电视剧', '剧集', '连续剧', 'series', 'tv', '电视'],
    3: ['动画', '动漫', 'anime', '卡通'],
    4: ['综艺', '真人秀', '脱口秀', 'variety'],
    5: ['纪录片', '纪实', 'documentary'],
}


def classify_movie(tags, area):
    """根据标签和地区推断分类"""
    combined = tags + ' ' + area
    combined_lower = combined.lower()
    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in combined or kw in combined_lower:
                return cat_id
    return 1  # 默认电影


def parse_p_tag(p_tag):
    """从列表页的 p 标签解析信息"""
    raw = p_tag.text.strip() if p_tag else ''
    if not raw:
        return {}

    # 替换 \xa0 为空格
    raw = raw.replace('\xa0', ' ')

    lines = [l.strip() for l in raw.split('\n') if l.strip()]

    result = {
        'director': '',
        'actors': '',
        'year': 0,
        'area': '',
        'tags': '',
        'duration': '',
    }

    for line in lines:
        # 第一行: 导演 / 主演
        if '导演' in line or '主演' in line:
            # 提取导演（取中文名部分，到英文或空格前结束）
            dm = re.search(r'导演[：:]?\s*([一-鿿·]{2,12})', line)
            if dm:
                result['director'] = dm.group(1).strip()
            # 提取主演（取前3个中文名）
            actor_part = line.split('主演')[1] if '主演' in line else ''
            # 按 / 分割每个人
            actor_items = actor_part.split('/')
            actors_cn = []
            for item in actor_items:
                item = item.strip()
                # 提取中文名
                cn_match = re.search(r'([一-鿿·　]{2,10})', item)
                if cn_match:
                    actors_cn.append(cn_match.group(1))
            result['actors'] = ','.join(actors_cn[:3]) if actors_cn else ''
            continue

        # 第二行: 年份 / 地区 / 类型
        year_m = re.search(r'(\d{4})', line)
        if year_m:
            result['year'] = int(year_m.group(1))

        # 地区 (在年份之后的内容)
        parts = re.split(r'[/|]', line)
        area_parts = []
        tag_parts = []
        for p in parts:
            p = p.strip()
            if re.search(r'[一-鿿]', p):
                # 包含中文
                if any(kw in p for kw in ['中国', '美国', '日本', '香港', '台湾',
                                          '法国', '英国', '德国', '韩国', '印度',
                                          '意大利', '西班牙', '加拿大', '澳大利亚',
                                          '俄罗斯', '巴西', '泰国']):
                    area_parts.append(p.strip())
                else:
                    tag_parts.append(p.strip())

        if area_parts:
            result['area'] = ' '.join(area_parts)
        if tag_parts:
            result['tags'] = ','.join([t for t in tag_parts if t])

    return result


def scrape_page(start=0):
    """爬取一页豆瓣 Top250"""
    url = f'https://movie.douban.com/top250?start={start}'
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'lxml')

    items = soup.select('.grid_view .item')
    movies = []

    for item in items:
        # 标题
        title_tag = item.select_one('.title')
        if not title_tag:
            continue
        title = title_tag.text.strip()
        cn_title = title.split('\xa0/\xa0')[0] if '\xa0' in title else title

        # 评分
        rating_tag = item.select_one('.rating_num')
        score = rating_tag.text.strip() if rating_tag else '0'

        # 封面 (使用大图)
        img_tag = item.select_one('img')
        cover_url = img_tag.get('src', '') if img_tag else ''
        cover_url = cover_url.replace('/s_ratio_poster/', '/l_ratio_poster/') if cover_url else ''

        # 简介
        quote_tag = item.select_one('.quote .inq')
        description = quote_tag.text.strip() if quote_tag else ''

        # 从 p 标签解析详细信息
        bd = item.select_one('.bd')
        p_tag = bd.select_one('p') if bd else None
        info = parse_p_tag(p_tag) if p_tag else {}

        # 推断分类
        category_id = classify_movie(info.get('tags', ''), info.get('area', ''))

        movie = {
            'title': cn_title,
            'cover_url': cover_url,
            'score': score,
            'description': description,
            'director': info.get('director', ''),
            'actors': info.get('actors', ''),
            'year': info.get('year', 0),
            'area': info.get('area', ''),
            'duration': info.get('duration', ''),
            'category_id': category_id,
            'tags': info.get('tags', ''),
        }
        movies.append(movie)

    return movies


def generate_sql(movies, batch_size=20):
    """生成 SQL INSERT 语句"""
    lines = [
        "-- ============================================",
        "-- 豆瓣电影 Top250 爬虫导入",
        f"-- 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "-- ============================================",
        "",
        "USE video_platform;",
        "",
        "INSERT INTO sys_video (title, category_id, cover_url, video_url, description, "
        "director, actors, year, area, duration, score, tags, is_recommend, play_count) VALUES",
    ]

    values = []
    for i, m in enumerate(movies[:batch_size]):
        desc_escaped = m['description'].replace("'", "''")
        tags_escaped = m['tags'].replace("'", "''")
        actors_escaped = m['actors'].replace("'", "''")
        director_escaped = m['director'].replace("'", "''")

        # 视频URL使用占位，后续可以替换
        video_url = "https://www.w3schools.com/html/mov_bbb.mp4"
        is_recommend = 1 if i < 5 else 0
        play_count = random.randint(100000, 3000000)

        val = (
            f"('{m['title']}', {m['category_id']}, "
            f"'{m['cover_url']}', '{video_url}', "
            f"'{desc_escaped}', '{director_escaped}', "
            f"'{actors_escaped}', {m['year']}, '{m['area']}', "
            f"'{m['duration']}', {m['score']}, "
            f"'{tags_escaped}', {is_recommend}, {play_count})"
        )
        values.append(val)

    lines.append(",\n".join(values) + ";")
    lines.append("")
    lines.append(f"-- 共导入 {len(values)} 条数据 (来源: 豆瓣电影 Top250)")
    return "\n".join(lines)


def main():
    print("豆瓣电影爬虫 v2 — 从列表页直接采集")
    print("=" * 40)

    all_movies = []

    # 爬取前2页 Top250 (50条)
    for page in range(0, 250, 25):
        print(f"\n--- 爬取第 {page//25 + 1} 页...")
        try:
            movies = scrape_page(start=page)
            all_movies.extend(movies)
            for m in movies:
                print(f"  + {m['title']} | {m['score']}分 | {m['director']}")
            time.sleep(random.uniform(1.0, 2.0))
        except Exception as e:
            print(f"  - 爬取失败: {e}")
            break

    print(f"\n== 共获取 {len(all_movies)} 条数据")

    # 输出统计
    categories = {}
    for m in all_movies:
        cat_name = {1: '电影', 2: '电视剧', 3: '动漫', 4: '综艺', 5: '纪录片'}.get(m['category_id'], '其他')
        categories[cat_name] = categories.get(cat_name, 0) + 1
    print(f"分类分布: {categories}")

    if not all_movies:
        print("没有获取到数据，请检查网络或重试")
        return

    # 生成SQL
    sql = generate_sql(all_movies, batch_size=250)

    output_path = "E:/project/miniprogram-video/scripts/douban_movies.sql"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sql)
    print(f"\n== SQL 已保存到: {output_path}")

    # 打印前5条预览
    print("\n--- 前5条预览 ---")
    for m in all_movies[:5]:
        print(f"  {m['title']} | {m['score']}分 | 导演: {m['director']} | {m['year']}年 | {m['area']}")
        if m['actors']:
            print(f"    主演: {m['actors']}")
        if m['tags']:
            print(f"    标签: {m['tags']}")


if __name__ == '__main__':
    main()
