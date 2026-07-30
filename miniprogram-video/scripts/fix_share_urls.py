"""
从 share HTML 页面提取隐藏的 m3u8 地址，更新数据库
适用于 API 没有提供 m3u8 源的视频
"""
import requests
import pymysql
import time
import re
from urllib.parse import urlparse

DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': '123456',
    'database': 'video_platform', 'charset': 'utf8mb4',
}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
DELAY = 0.5

def extract_m3u8_from_share(share_url):
    """从 share HTML 页面提取 m3u8 地址"""
    try:
        r = requests.get(share_url, headers=HEADERS, timeout=15)
        html = r.text
        main_match = re.search(r'var main = \"(.+?)\"', html)
        if main_match:
            main_path = main_match.group(1)
            parsed = urlparse(share_url)
            base = f'{parsed.scheme}://{parsed.netloc}'
            full_url = base + main_path
            # 移除 sign 参数（不需要签名也能访问）
            full_url = re.sub(r'\?sign=[^&]+', '', full_url)
            return full_url
        return None
    except Exception as e:
        print(f'    提取失败: {e}')
        return None

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 找出所有 share 格式的 URL（不含 m3u8）
    cur.execute("""
        SELECT id, title, video_url FROM sys_video
        WHERE video_url LIKE '%share%' AND video_url NOT LIKE '%.m3u8%'
        ORDER BY id
    """)
    records = cur.fetchall()
    total = len(records)
    print(f'共找到 {total} 条 share 格式视频记录')

    success = 0
    failed = 0
    skipped = 0

    for idx, (vid, title, old_url) in enumerate(records):
        print(f'[{idx+1}/{total}] ID={vid} {str(title)[:30]}...', end=' ')

        # 如果URL后面有#第二集之类的内容，只保留share URL部分
        clean_url = old_url.split('#')[0]

        m3u8_url = extract_m3u8_from_share(clean_url)
        if not m3u8_url:
            print('❌ 无法提取m3u8')
            failed += 1
            time.sleep(DELAY)
            continue

        try:
            cur.execute("UPDATE sys_video SET video_url = %s WHERE id = %s", (m3u8_url, vid))
            conn.commit()
            print(f'✅ {m3u8_url[:60]}...')
            success += 1
        except Exception as e:
            conn.rollback()
            print(f'❌ 数据库错误: {e}')
            failed += 1

        time.sleep(DELAY)

    print(f'\n========== 结果 ==========')
    print(f'总计: {total}')
    print(f'成功: {success}')
    print(f'失败: {failed}')
    print(f'跳过: {skipped}')

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
