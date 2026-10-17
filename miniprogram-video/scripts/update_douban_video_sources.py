"""
从量子资源 API 获取豆瓣电影的真实视频源（HLS m3u8 格式），更新数据库
- 搜索豆瓣电影标题
- 获取详情，优先选择 lzm3u8 来源（索引.m3u8），回退到 share 来源
- 更新 sys_video.video_url
"""
import requests
import pymysql
import time
import re

API_BASE = 'https://cj.lziapi.com/api.php/provide/vod/at/json/'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
DELAY = 0.3

DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': '123456',
    'database': 'video_platform', 'charset': 'utf8mb4',
}

def get_first_m3u8_url(play_url):
    """
    从 play_url 提取 m3u8 格式的播放地址
    优先取第二个来源 (lzm3u8) 的 index.m3u8
    """
    if not play_url:
        return None

    # 多个来源用 $$$ 分隔
    sources = play_url.split('$$$')

    # 优先找包含 m3u8 的来源
    for src in sources:
        src = src.strip()
        if 'index.m3u8' in src or '.m3u8' in src:
            # 取第一集
            first_ep = src.split('#')[0].strip()
            if '$' in first_ep:
                _, url = first_ep.split('$', 1)
                url = url.strip()
                if url:
                    return url

    # 回退：取第一个来源的第一集
    first_source = sources[0].strip()
    first_ep = first_source.split('#')[0].strip()
    if '$' in first_ep:
        _, url = first_ep.split('$', 1)
        return url.strip()
    return None


def search_movie(keyword):
    """搜索电影，返回匹配结果列表"""
    url = f'{API_BASE}?ac=list&wd={keyword}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        if data.get('list'):
            return data['list']
    except Exception as e:
        print(f'    [搜索失败] {e}')
    return []


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 找出所有占位视频或 share 格式的豆瓣视频
    cur.execute("""
        SELECT id, title, year, video_url FROM sys_video
        WHERE (video_url LIKE '%w3schools%' OR video_url LIKE '%mov_bbb%'
               OR (video_url LIKE '%lzcdn%' AND video_url NOT LIKE '%.m3u8%'
                   AND id >= 5916))
        ORDER BY id
    """)
    movies = cur.fetchall()
    total = len(movies)
    print(f'共找到 {total} 条待更新的视频记录')

    success = 0
    not_found = 0
    errors = []

    for idx, (vid, title, year, old_url) in enumerate(movies):
        print(f'\n[{idx+1}/{total}] ID={vid} {title}...', end=' ')

        results = search_movie(title)
        if not results:
            print('❌ 未找到')
            not_found += 1
            errors.append((vid, title, 'API未找到'))
            time.sleep(DELAY)
            continue

        # 精确匹配
        matched = None
        for item in results:
            api_title = item.get('vod_name', '')
            api_year = item.get('vod_year', '')
            if re.sub(r'[\s:：]', '', api_title) == re.sub(r'[\s:：]', '', title):
                if not year or not api_year or str(api_year) == str(year):
                    matched = item
                    break

        if not matched:
            matched = results[0]

        vod_id = matched['vod_id']
        time.sleep(DELAY)

        # 获取详情
        r2 = requests.get(f'{API_BASE}?ac=detail&ids={vod_id}', headers=HEADERS, timeout=15)
        try:
            detail = r2.json()
            item = detail.get('list', [{}])[0]
        except:
            print(f'❌ 详情解析失败')
            errors.append((vid, title, '详情解析失败'))
            continue

        play_url = item.get('vod_play_url', '')
        video_url = get_first_m3u8_url(play_url)

        if not video_url:
            print('❌ 无播放地址')
            errors.append((vid, title, '无播放地址'))
            not_found += 1
            continue

        # 更新数据库
        try:
            cur.execute("UPDATE sys_video SET video_url = %s WHERE id = %s", (video_url, vid))
            conn.commit()
            source_type = 'm3u8' if '.m3u8' in video_url else 'share'
            print(f'✅ [{source_type}] {video_url[:70]}...')
            success += 1
        except Exception as e:
            conn.rollback()
            print(f'❌ 更新失败: {e}')
            errors.append((vid, title, str(e)))

    print('\n\n========== 结果统计 ==========')
    print(f'总记录: {total}')
    print(f'成功更新: {success}')
    print(f'未找到: {not_found}')
    if errors:
        print(f'\n错误:')
        for vid, title, err in errors[:5]:
            print(f'  ID={vid} {title}: {err}')
        if len(errors) > 5:
            print(f'  ... 还有 {len(errors)-5} 条')

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
