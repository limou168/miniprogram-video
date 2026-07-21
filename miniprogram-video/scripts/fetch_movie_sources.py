"""
从量子资源API获取真实影视播放链接并更新数据库
"""
import requests
import pymysql
import time
import re

HEADERS = {'User-Agent': 'Mozilla/5.0'}
API_BASE = 'https://cj.lziapi.com/api.php/provide/vod/at/json/'

DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': '123456',
    'database': 'video_platform', 'charset': 'utf8mb4',
}


def search_movie(title):
    """搜索电影获取播放链接和完整信息"""
    url = f'{API_BASE}?wd={title}&pagesize=1'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        videos = data.get('list', [])
        if videos:
            v = videos[0]
            play_url = v.get('vod_play_url', '')
            first_url = ''
            if play_url:
                segs = play_url.split('#')
                for seg in segs:
                    # 格式：集数$URL 或 日期$URL
                    parts = seg.split('$')
                    if len(parts) >= 2:
                        first_url = parts[-1].strip()
                        break
                if not first_url and segs:
                    first_url = segs[0].strip()

            return {
                'vod_name': v.get('vod_name', ''),
                'vod_url': first_url,
                'vod_pic': v.get('vod_pic', ''),
                'vod_director': v.get('vod_director', ''),
                'vod_actor': v.get('vod_actor', ''),
                'vod_content': v.get('vod_content', ''),
                'vod_year': v.get('vod_year', ''),
                'vod_area': v.get('vod_area', ''),
                'vod_class': v.get('vod_class', ''),
                'vod_remarks': v.get('vod_remarks', ''),
            }
    except Exception as e:
        return None
    return None


def verify_url(url):
    """验证m3u8链接是否可访问"""
    if not url:
        return False
    try:
        r = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://cj.lziapi.com/',
        }, timeout=10)
        return r.status_code == 200
    except:
        return False


def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 获取所有需要更新video_url的视频
    cursor.execute('SELECT id, title FROM sys_video ORDER BY id')
    all_videos = cursor.fetchall()
    print(f'数据库现有 {len(all_videos)} 条视频\n')

    updated = 0
    not_found = 0
    failed_urls = []

    for vid, title in all_videos:
        print(f'[{vid:3d}] 搜索: {title}...', end=' ')

        result = search_movie(title)

        if result and result['vod_url']:
            # 验证链接
            if verify_url(result['vod_url']):
                # 更新video_url
                sql = 'UPDATE sys_video SET video_url = %s WHERE id = %s'
                cursor.execute(sql, (result['vod_url'], vid))

                # 如果现有字段为空，用API数据补充
                # 更新封面（如果豆瓣封面是占位符或不含lzipic）
                if result['vod_pic']:
                    sql2 = 'UPDATE sys_video SET cover_url = %s WHERE id = %s AND cover_url LIKE "%%picsum%%"'
                    cursor.execute(sql2, (result['vod_pic'], vid))

                conn.commit()
                updated += 1
                print(f'OK - m3u8')
            else:
                failed_urls.append((vid, title, result['vod_url']))
                print(f'URL不可访问')
        elif result:
            print(f'无播放链接')
            not_found += 1
        else:
            print(f'未搜索到')
            not_found += 1

        time.sleep(0.5)  # 礼貌延迟

    print(f'\n=== 结果 ===')
    print(f'更新成功: {updated} 条')
    print(f'未找到/无链接: {not_found} 条')

    if failed_urls:
        print(f'\n链接不可用 ({len(failed_urls)} 条):')
        for vid, title, url in failed_urls:
            print(f'  [{vid}] {title}: {url[:60]}...')

    # 最终统计
    cursor.execute('SELECT COUNT(*) FROM sys_video WHERE video_url LIKE "%%.m3u8%%" OR video_url LIKE "%%cdn.coverr%%"')
    with_url = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM sys_video WHERE video_url LIKE "%%m3u8%%"')
    m3u8_count = cursor.fetchone()[0]
    print(f'\n有播放地址: {with_url} 条 (其中m3u8: {m3u8_count} 条)')

    conn.close()


if __name__ == '__main__':
    main()
