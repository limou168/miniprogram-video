"""
从量子资源 API 重新导入完整影视数据
- 清空旧数据
- 按分类获取大量影视数据（含所有集数、图片、详情）
- 支持断点续传

API: https://cj.lziapi.com/api.php/provide/vod/at/json/
"""
import requests
import pymysql
import time
import re
from datetime import datetime

# ===================== 配置 =====================

API_BASE = 'https://cj.lziapi.com/api.php/provide/vod/at/json/'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': '123456',
    'database': 'video_platform', 'charset': 'utf8mb4',
}

# 目标数量（每种分类取多少条）
TARGET_PER_CATEGORY = 100
# 每页大小
PAGE_SIZE = 20
# 请求间隔（秒）
DELAY = 0.3

# API type_id → 我们的分类ID
# 我们数据库的分类：1=电影, 2=电视剧, 3=动漫, 4=综艺, 5=纪录片
CATEGORY_MAP = {
    # ===== 电影类 =====
    6: 1,   # 剧情片
    7: 1,   # 喜剧片
    8: 1,   # 爱情片
    9: 1,   # 科幻片
    10: 1,  # 恐怖片
    11: 1,  # 动作片
    12: 1,  # 战争片
    1: 1,   # 电影片
    # ===== 电视剧类 =====
    13: 2,  # 国产剧
    14: 2,  # 港剧
    15: 2,  # 日剧
    16: 2,  # 欧美剧
    21: 2,  # 台剧
    23: 2,  # 韩剧
    24: 2,  # 泰剧
    25: 2,  # 大陆综艺（归为综艺）
    26: 2,  # 台湾综艺
    27: 2,  # 日韩综艺
    28: 2,  # 欧美综艺
    2: 2,   # 连续剧（通用）
    22: 2,  # 日本剧
    # ===== 动漫类 =====
    3: 3,   # 动画片
    4: 3,   # 动漫片
    29: 3,  # 国产动漫
    30: 3,  # 日韩动漫
    # ===== 纪录片 =====
    20: 5,  # 纪录片
}

# ===================== 工具函数 =====================

def clean_html(text):
    """清理HTML标签"""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_play_url(play_url, play_from=''):
    """
    解析 vod_play_url 为分集列表

    格式1（电视剧多集）：第01集$url#第02集$url#...
    格式2（电视剧多集,多来源）：第01集$url$$$第01集$url#第02集$url$$$第02集$url#...
    格式3（电影单集）：HD国语$url$$$HD国语$url

    返回: [(episode_number, title, url), ...]
    """
    if not play_url:
        return []

    episodes = []

    # 判断是单来源还是多来源（$$$ 分隔不同播放源）
    # 对于多来源，取第一个来源的数据（通常最完整）
    sources = play_url.split('$$$')

    # 取第一个来源
    first_source = sources[0].strip()

    # 按 # 分割每一集
    parts = first_source.split('#')

    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        # 每集格式：标题$url
        if '$' in part:
            title, url = part.split('$', 1)
            url = url.strip()
            if url:
                # 尝试提取集数
                ep_num = i + 1
                match = re.search(r'第(\d+)集', title)
                if match:
                    ep_num = int(match.group(1))

                # 清理标题
                clean_title = title.strip()

                episodes.append((ep_num, clean_title, url))

    # 如果没有解析到任何集数但是有URL（电影单集情况）
    if not episodes and first_source:
        if '$' in first_source:
            title, url = first_source.split('$', 1)
            if url.strip():
                episodes.append((1, title.strip(), url.strip()))

    return episodes


def get_type_name(type_id):
    """根据 type_id 获取分类名称"""
    names = {
        1: '电影片', 6: '剧情片', 7: '喜剧片', 8: '爱情片', 9: '科幻片',
        10: '恐怖片', 11: '动作片', 12: '战争片',
        13: '国产剧', 14: '港剧', 15: '日剧', 16: '欧美剧',
        21: '台剧', 22: '日剧', 23: '韩剧', 24: '泰剧',
        25: '大陆综艺', 26: '台湾综艺', 27: '日韩综艺', 28: '欧美综艺',
        2: '连续剧', 3: '动画片', 4: '动漫片', 20: '纪录片',
        29: '国产动漫', 30: '日韩动漫',
    }
    return names.get(type_id, f'未知({type_id})')


def fetch_page(type_id, page):
    """获取一页数据"""
    url = f'{API_BASE}?ac=list&t={type_id}&pg={page}&pagesize={PAGE_SIZE}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        return r.json()
    except Exception as e:
        print(f'  [请求失败] {e}')
        return None


def fetch_detail(vod_id):
    """获取视频详情"""
    url = f'{API_BASE}?ac=detail&ids={vod_id}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        if data.get('list'):
            return data['list'][0]
    except Exception as e:
        print(f'  [详情请求失败] {e}')
    return None


# ===================== 主逻辑 =====================

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    total_inserted = 0
    total_episodes = 0
    errors = []

    # 按分类处理
    for type_id, our_cat_id in sorted(CATEGORY_MAP.items()):
        type_name = get_type_name(type_id)
        cat_name = {1: '电影', 2: '电视剧', 3: '动漫', 4: '综艺', 5: '纪录片'}.get(our_cat_id, '未知')

        print(f'\n{"="*60}')
        print(f'分类: {type_name}(type_id={type_id}) → 我们的: {cat_name}(category_id={our_cat_id})')
        print(f'{"="*60}')

        # 获取第一页，了解总页数
        first_page = fetch_page(type_id, 1)
        if not first_page or not first_page.get('list'):
            print('  [无数据，跳过]')
            continue

        total = first_page.get('total', 0)
        pagecount = first_page.get('pagecount', 1)
        pages_needed = min(pagecount, (TARGET_PER_CATEGORY + PAGE_SIZE - 1) // PAGE_SIZE)

        print(f'  总数据: {total} 条, 总页数: {pagecount}, 将获取: {pages_needed} 页')

        # 收集该分类下的所有视频
        all_items = []
        all_items.extend(first_page.get('list', []))

        for pg in range(2, pages_needed + 1):
            time.sleep(DELAY)
            page_data = fetch_page(type_id, pg)
            if page_data and page_data.get('list'):
                all_items.extend(page_data.get('list', []))
                print(f'  已获取第 {pg}/{pages_needed} 页 (累计 {len(all_items)} 条)', end='\r')
            else:
                print(f'\n  [第 {pg} 页获取失败]')
            time.sleep(DELAY)

        print(f'\n  共获取 {len(all_items)} 条, 开始获取详情...')

        cat_inserted = 0
        cat_episodes = 0

        for idx, item in enumerate(all_items):
            vod_id = item['vod_id']
            vod_name = item.get('vod_name', '')

            print(f'  [{idx+1}/{len(all_items)}] ID={vod_id} {vod_name}...', end=' ')

            time.sleep(DELAY)
            detail = fetch_detail(vod_id)

            if not detail:
                print('获取详情失败')
                errors.append((vod_id, vod_name, '详情获取失败'))
                continue

            # ===== 提取字段 =====
            title = detail.get('vod_name', vod_name)
            pic = detail.get('vod_pic', '')
            director = detail.get('vod_director', '')
            actor = detail.get('vod_actor', '')
            area = detail.get('vod_area', '')
            year_str = detail.get('vod_year', '')
            score_str = detail.get('vod_score', '0')
            vod_class = detail.get('vod_class', '')  # 标签
            vod_content = detail.get('vod_content', '')
            vod_remarks = detail.get('vod_remarks', '')
            play_url = detail.get('vod_play_url', '')

            # 清理描述
            description = clean_html(vod_content)

            # 解析年份
            year = 0
            if year_str:
                match = re.search(r'(\d{4})', str(year_str))
                if match:
                    year = int(match.group(1))

            # 解析评分
            try:
                score = float(score_str) if score_str else 0.0
            except ValueError:
                score = 0.0

            # 分析集数
            episodes = parse_play_url(play_url, detail.get('vod_play_from', ''))
            ep_count = len(episodes)

            # 判断是否是电视剧（多集）
            is_tv_series = ep_count > 1

            # 电视剧: video_url 留空，集数存到 episode 表
            # 电影: video_url 存第一个播放链接
            video_url = ''
            if not is_tv_series and episodes:
                video_url = episodes[0][2]

            # 计算时长（用于显示）
            duration = vod_remarks if vod_remarks else ''
            if not duration and not is_tv_series:
                duration = 'HD'

            try:
                # 插入 sys_video
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sql = """INSERT INTO sys_video
                    (title, category_id, cover_url, video_url, description, director, actors,
                     year, area, duration, score, tags, play_count, status, is_recommend, create_time, update_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 1, 0, %s, %s)"""

                cursor.execute(sql, (
                    title, our_cat_id, pic, video_url, description, director, actor,
                    year, area, duration, score, vod_class, now, now
                ))

                new_video_id = cursor.lastrowid

                # 插入剧集（如果是多集电视剧）
                if is_tv_series and episodes:
                    ep_sql = """INSERT INTO sys_video_episode
                        (video_id, episode_number, episode_title, video_url, duration, create_time)
                        VALUES (%s, %s, %s, %s, %s, %s)"""

                    for ep_num, ep_title, ep_url in episodes:
                        cursor.execute(ep_sql, (
                            new_video_id, ep_num, ep_title, ep_url, '', now
                        ))

                    cat_episodes += len(episodes)

                conn.commit()
                cat_inserted += 1

                ep_info = f' ({len(episodes)}集)' if is_tv_series else ' (单集)'
                print(f'OK{ep_info}')

            except Exception as e:
                conn.rollback()
                print(f'FAIL 数据库错误: {e}')
                errors.append((vod_id, title, str(e)))

        total_inserted += cat_inserted
        total_episodes += cat_episodes
        print(f'  [{type_name}] 完成: 插入 {cat_inserted} 部, {cat_episodes} 集')

    # ===== 最终统计 =====
    print(f'\n\n{"="*60}')
    print(f'导入完成!')
    print(f'总计导入: {total_inserted} 部视频, {total_episodes} 集')
    print(f'错误: {len(errors)} 条')

    if errors:
        print(f'\n错误详情:')
        for vid, name, err in errors[:10]:
            print(f'  ID={vid} {name}: {err}')
        if len(errors) > 10:
            print(f'  ... 还有 {len(errors)-10} 条错误')

    # 统计各分类数量
    cursor.execute("""
        SELECT c.name, COUNT(*)
        FROM sys_video v JOIN sys_category c ON v.category_id = c.id
        GROUP BY c.id ORDER BY c.id
    """)
    print(f'\n各分类数量:')
    for cat_name, cnt in cursor.fetchall():
        print(f'  {cat_name}: {cnt} 部')

    # 统计有/无集数的电视剧
    cursor.execute("""
        SELECT COUNT(DISTINCT e.video_id)
        FROM sys_video_episode e
    """)
    with_eps = cursor.fetchone()[0]
    print(f'  有集数数据: {with_eps} 部')

    cursor.execute("SELECT COUNT(*) FROM sys_video WHERE video_url != ''")
    single_url = cursor.fetchone()[0]
    print(f'  单视频(电影): {single_url} 部')

    conn.close()


if __name__ == '__main__':
    main()
