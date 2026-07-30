"""
全量同步量子API视频数据（适配你的表结构）
"""
import requests
import pymysql
import time
import json
import xml.etree.ElementTree as ET
import re
import traceback

HEADERS = {'User-Agent': 'Mozilla/5.0'}
API_BASE = 'https://cj.lziapi.com/api.php/provide/vod/at/xml/'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'video_platform',
    'charset': 'utf8mb4',
}

PAGE_SIZE = 20  # API 默认每页20，保持
MAX_RETRIES = 3

def fetch_page(page=1, pagesize=PAGE_SIZE):
    print(f"  请求URL: {API_BASE}?page={page}&pagesize={pagesize}")
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(f'{API_BASE}?page={page}&pagesize={pagesize}', headers=HEADERS, timeout=15)
            resp.encoding = 'utf-8'
            print(f"  HTTP状态码: {resp.status_code}")
            if resp.status_code != 200:
                print(f"  状态码非200，重试...")
                time.sleep(2)
                continue
            text = resp.text.strip()
            print(f"  原始响应前200字符: {text[:200]}")
            # 尝试JSON
            try:
                data = json.loads(text)
                videos = data.get('list') or data.get('data') or data.get('vod_list') or data.get('videos')
                if videos and isinstance(videos, list):
                    return videos
                if isinstance(data, list):
                    return data
                print("  JSON解析成功但未找到视频列表")
                return []
            except json.JSONDecodeError:
                # 尝试XML
                try:
                    root = ET.fromstring(text)
                    videos = []
                    for video in root.findall('.//video'):
                        v = {}
                        for child in video:
                            v[child.tag] = child.text or ''
                        videos.append(v)
                    if videos:
                        return videos
                    print("  XML解析成功但未找到video节点")
                    return []
                except ET.ParseError as e:
                    print(f"  XML解析失败: {e}")
                    return []
        except Exception as e:
            print(f"  请求异常: {e}")
            traceback.print_exc()
            time.sleep(2)
    return None

def parse_episodes(play_url_str):
    episodes = []
    if not play_url_str:
        return episodes
    segments = play_url_str.split('#')
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if '$' in seg:
            parts = seg.split('$', 1)
            title = parts[0].strip()
            url = parts[1].strip()
            if url.startswith('http'):
                num = None
                match = re.search(r'第?(\d+)\s*集?', title)
                if match:
                    num = int(match.group(1))
                else:
                    nums = re.findall(r'\d+', title)
                    if nums:
                        num = int(nums[0])
                episodes.append((num, title, url))
        else:
            if seg.startswith('http'):
                episodes.append((None, '第1集', seg))
    # 处理编号
    for i, (num, title, url) in enumerate(episodes, start=1):
        if num is None:
            episodes[i-1] = (i, title, url)
    used = set()
    new_eps = []
    for num, title, url in episodes:
        while num in used:
            num += 1
        used.add(num)
        new_eps.append((num, title, url))
    return new_eps

def clear_tables(cursor):
    cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
    cursor.execute('TRUNCATE TABLE sys_video_episode')
    cursor.execute('TRUNCATE TABLE sys_video')
    cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
    print("已清空表")

def get_category_id(cursor, class_name):
    """
    根据分类名称获取或创建分类ID
    如果传入空字符串，返回默认分类ID（比如1）
    你可以根据实际分类表调整
    """
    if not class_name:
        return 1  # 默认分类
    
    # 查询是否已存在该分类（假设你有 sys_category 表）
    cursor.execute('SELECT id FROM sys_category WHERE name = %s', (class_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # 不存在则创建新分类（如果不需要自动创建，就返回默认ID）
    # 这里演示自动创建，如果你不想自动创建，可以去掉注释的代码，直接 return 1
    # cursor.execute('INSERT INTO sys_category (name) VALUES (%s)', (class_name,))
    # conn.commit()
    # return cursor.lastrowid
    return 1  # 暂时返回默认分类ID

def insert_video(cursor, video_data):
    """
    插入视频基本信息，返回自增ID
    字段映射关系：
    - vod_name/name → title
    - vod_pic/pic → cover_url
    - vod_play_url/play_url → video_url (存第一集链接)
    - vod_content/content → description
    - vod_director/director → director
    - vod_actor/actor → actors
    - vod_year/year → year (转整数)
    - vod_area/area → area
    - vod_class/class → 用于确定 category_id
    - vod_remarks/remarks → 忽略，或可拼入 tags
    """
    play_str = video_data.get('vod_play_url') or video_data.get('play_url') or ''
    eps = parse_episodes(play_str)
    first_url = eps[0][2] if eps else ''
    
    title = video_data.get('vod_name') or video_data.get('name') or ''
    cover = video_data.get('vod_pic') or video_data.get('pic') or ''
    desc = video_data.get('vod_content') or video_data.get('content') or ''
    director = video_data.get('vod_director') or video_data.get('director') or ''
    actors = video_data.get('vod_actor') or video_data.get('actor') or ''
    year_str = video_data.get('vod_year') or video_data.get('year') or ''
    area = video_data.get('vod_area') or video_data.get('area') or ''
    class_name = video_data.get('vod_class') or video_data.get('class') or ''
    remarks = video_data.get('vod_remarks') or video_data.get('remarks') or ''
    
    # 年份转整数
    try:
        year = int(year_str) if year_str else 0
    except:
        year = 0
    
    # 获取分类ID
    category_id = get_category_id(cursor, class_name)
    
    # 如果有 remarks，可以拼接到 tags 或 description 里
    tags = class_name  # 分类作为标签
    
    sql = """
        INSERT INTO sys_video 
        (title, category_id, cover_url, video_url, description, director, actors, 
         year, area, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        title,
        category_id,
        cover,
        first_url,
        desc,
        director,
        actors,
        year,
        area,
        tags
    ))
    return cursor.lastrowid

def insert_episodes(cursor, video_id, episodes):
    if not episodes:
        return
    sql = """
        INSERT INTO sys_video_episode 
        (video_id, episode_number, episode_title, video_url) 
        VALUES (%s, %s, %s, %s)
    """
    data = [(video_id, num, title, url) for num, title, url in episodes]
    cursor.executemany(sql, data)

def main():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("数据库连接成功")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        traceback.print_exc()
        input("按任意键退出...")
        return

    cursor = conn.cursor()

    try:
        clear_tables(cursor)
        conn.commit()
    except Exception as e:
        print(f"清空表失败: {e}")
        traceback.print_exc()
        input("按任意键退出...")
        return

    page = 1
    total_videos = 0
    total_episodes = 0

    while True:
        print(f"\n>>> 正在拉取第 {page} 页")
        try:
            videos = fetch_page(page, PAGE_SIZE)
        except Exception as e:
            print(f"获取第{page}页异常: {e}")
            traceback.print_exc()
            break

        if videos is None:
            print("请求失败，终止")
            break
        if not videos:
            print("本页无数据，结束")
            break

        print(f"本页获取到 {len(videos)} 条视频")
        for idx, v in enumerate(videos, 1):
            if idx % 10 == 0 or idx == len(videos):
                print(f"  处理第 {idx}/{len(videos)} 条: {v.get('vod_name', '未知')[:30]}...")
            try:
                video_id = insert_video(cursor, v)
                play_str = v.get('vod_play_url') or v.get('play_url') or ''
                eps = parse_episodes(play_str)
                if eps:
                    insert_episodes(cursor, video_id, eps)
                    total_episodes += len(eps)
                total_videos += 1
            except Exception as e:
                print(f"处理视频 {v.get('vod_name', '未知')} 时出错:")
                traceback.print_exc()
                conn.rollback()
        try:
            conn.commit()
        except Exception as e:
            print(f"提交事务失败: {e}")
            traceback.print_exc()
            conn.rollback()
            break

        print(f"第 {page} 页完成，累计视频 {total_videos}，集数 {total_episodes}")

        if len(videos) < PAGE_SIZE:
            break
        page += 1
        time.sleep(0.5)

    # 最终统计
    try:
        cursor.execute('SELECT COUNT(*) FROM sys_video')
        vc = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM sys_video_episode')
        ec = cursor.fetchone()[0]
        print(f"\n=== 最终统计 ===")
        print(f"视频数: {vc}")
        print(f"集数: {ec}")
    except Exception as e:
        print(f"统计失败: {e}")
        traceback.print_exc()

    conn.close()
    input("\n按任意键退出...")

if __name__ == '__main__':
    main()