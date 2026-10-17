"""
Coverr 免费视频源采集 — 获取高清 MP4 视频链接并更新数据库
"""
import requests
import pymysql
import time
import random
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'video_platform',
    'charset': 'utf8mb4',
}


def fetch_coverr_videos(pages=3):
    """从 Coverr API 获取视频列表"""
    videos = []
    for page in range(1, pages + 1):
        url = f'https://coverr.co/api/videos?page={page}&per_page=30'
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            data = r.json()
            hits = data.get('hits', [])
            videos.extend(hits)
            print(f'  第{page}页: 获取 {len(hits)} 条')
            time.sleep(1)
        except Exception as e:
            print(f'  第{page}页失败: {e}')
    return videos


def get_video_url(base_filename, quality='1080p'):
    """构造 Coverr 视频 CDN URL"""
    # 检查是否有4K
    if quality == '4k':
        return f'https://cdn.coverr.co/videos/{base_filename}/4k.mp4'
    return f'https://cdn.coverr.co/videos/{base_filename}/1080p.mp4'


def verify_url(url, timeout=10):
    """验证视频URL是否可访问"""
    try:
        r = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            size = int(r.headers.get('Content-Length', 0))
            return True, size
        # 有些返回301后HEAD不跟随，用GET试
        r2 = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        if r2.status_code == 200:
            size = int(r2.headers.get('Content-Length', 0))
            r2.close()
            return True, size
        return False, 0
    except Exception as e:
        return False, 0


def generate_tags_from_coverr_tags(tags_list):
    """将Coverr标签转为中文友好的标签"""
    if not tags_list:
        return ''

    # 常见映射
    tag_map = {
        'nature': '自然', 'landscape': '风景', 'travel': '旅行',
        'city': '城市', 'people': '人物', 'beach': '海滩',
        'beautiful': '美丽', 'sea': '海洋', 'sunset': '日落',
        'sunrise': '日出', 'ocean': '海洋', 'water': '水',
        'mountain': '山', 'forest': '森林', 'sky': '天空',
        'clouds': '云', 'night': '夜晚', 'stars': '星空',
        'animals': '动物', 'food': '美食', 'music': '音乐',
        'dance': '舞蹈', 'sport': '运动', 'business': '商业',
        'technology': '科技', 'abstract': '抽象', 'art': '艺术',
        'background': '背景', 'loop': '循环', 'cinematic': '电影感',
        'aerial': '航拍', 'drone': '无人机', 'slow motion': '慢动作',
        'time lapse': '延时', 'timelapse': '延时',
        'video': '视频', 'stock': '素材', 'free': '免费',
        '4k': '4K', 'hd': '高清',
    }

    result = []
    for tag in tags_list[:5]:  # 最多取5个
        tag_lower = tag.lower()
        result.append(tag_map.get(tag_lower, tag))

    return ','.join(result)


def main():
    print('Coverr 视频源采集')
    print('=' * 40)

    # 1. 获取视频列表
    print('\n1. 获取视频列表...')
    videos = fetch_coverr_videos(pages=3)
    print(f'\n共获取 {len(videos)} 条视频')

    # 2. 收集可用的视频URL
    print('\n2. 验证视频URL...')
    valid_videos = []
    for v in videos:
        base_fn = v.get('base_filename', '')
        if not base_fn:
            continue

        # 优先4K，不行就用1080p
        url = get_video_url(base_fn, '4k')
        ok, size = verify_url(url)
        if not ok:
            url = get_video_url(base_fn, '1080p')
            ok, size = verify_url(url)

        if ok:
            width = v.get('max_width', 0)
            height = v.get('max_height', 0)
            valid_videos.append({
                'url': url,
                'title': v.get('title', ''),
                'width': width,
                'height': height,
                'size_mb': round(size / 1024 / 1024, 1),
                'duration': round(float(v.get('duration', 0)), 1),
                'tags': generate_tags_from_coverr_tags(v.get('tags', [])),
                'is_premium': v.get('is_premium', False),
            })
            quality = '4K' if '4k' in url else '1080p'
            print(f'  + [{quality}] {v["title"][:30]:30s} {size/1024/1024:.1f}MB')
        else:
            print(f'  - 不可用: {v.get("title","")[:30]}')

    print(f'\n有效视频: {len(valid_videos)} 条')

    if not valid_videos:
        print('没有可用视频，退出')
        return

    # 3. 更新数据库
    print('\n3. 更新数据库...')
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 获取所有需要更新video_url的视频 (排除已有的示例数据)
    cursor.execute('SELECT id, title FROM sys_video ORDER BY id')
    all_videos = cursor.fetchall()
    print(f'数据库现有 {len(all_videos)} 条视频')

    updated = 0
    for i, (vid, title) in enumerate(all_videos):
        if i >= len(valid_videos):
            break

        v = valid_videos[i]
        sql = 'UPDATE sys_video SET video_url = %s WHERE id = %s'
        cursor.execute(sql, (v['url'], vid))

        # 也更新标签
        if v['tags']:
            sql2 = 'UPDATE sys_video SET tags = CONCAT(tags, %s) WHERE id = %s AND tags = %s'
            cursor.execute(sql2, (',' + v['tags'], vid, ''))

        conn.commit()
        updated += 1
        quality = '4K' if '4k' in v['url'] else '1080p'
        print(f'  + [ID={vid}] {title[:20]:20s} <- {quality} {v["size_mb"]}MB')

    print(f'\n== 更新完成: {updated} 条视频已设置播放地址')

    # 统计
    cursor.execute('SELECT COUNT(*) FROM sys_video WHERE video_url IS NOT NULL AND video_url != ""')
    has_video = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM sys_video WHERE video_url LIKE "%4k%"')
    has_4k = cursor.fetchone()[0]
    print(f'  有播放地址: {has_video} 条 (其中4K: {has_4k} 条)')

    conn.close()


if __name__ == '__main__':
    main()
