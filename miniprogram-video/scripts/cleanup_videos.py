"""
清理非正片内容：影视解说、预告、花絮、片花、预告片、宣传片、彩蛋、幕后等
"""
import pymysql

DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': '123456',
    'database': 'video_platform', 'charset': 'utf8mb4',
}

# 需要清理的关键词（标题匹配）
DIRTY_KEYWORDS = [
    '解说', '预告', '花絮', '片花', '预告片', '宣传片',
    '彩蛋', '幕后', '制作特辑', '精彩片段', '精华版',
    '预告花絮', '先导片', '抢先看', '独家揭秘',
    '拍摄花絮', '探班', '发布会', '首映礼',
    '主题曲', 'MV', '推广曲', '片尾曲',
    '专访', '访谈', '见面会',
    '速看', '盘点', '混剪', '集锦',
    '纪录片',  # 如果标题只含"纪录片"的也清理（后面有正式分类）
]

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. 统计清理前数据
    cursor.execute('SELECT COUNT(*) FROM sys_video')
    before_total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM sys_video_episode')
    before_eps = cursor.fetchone()[0]

    # 2. 找出需要删除的视频ID
    all_ids = set()
    conditions = []
    for kw in DIRTY_KEYWORDS:
        like_expr = f"title LIKE '%{kw}%'"
        conditions.append(like_expr)

    where = ' OR '.join(conditions)
    cursor.execute(f'SELECT id, title, category_id FROM sys_video WHERE {where}')
    dirty = cursor.fetchall()

    print(f'找到 {len(dirty)} 部需要清理的视频：')
    for vid, title, cat in dirty:
        print(f'  #{vid} [{cat}] {title}')
        all_ids.add(vid)

    if not all_ids:
        print('没有需要清理的视频')
        conn.close()
        return

    # 3. 删除对应的剧集
    id_list = ','.join(str(i) for i in all_ids)
    cursor.execute(f'DELETE FROM sys_video_episode WHERE video_id IN ({id_list})')
    del_eps = cursor.rowcount
    print(f'\n删除剧集: {del_eps} 条')

    # 4. 删除视频
    cursor.execute(f'DELETE FROM sys_video WHERE id IN ({id_list})')
    del_vids = cursor.rowcount
    print(f'删除视频: {del_vids} 部')

    # 5. 提交
    conn.commit()

    # 6. 统计清理后
    cursor.execute('SELECT COUNT(*) FROM sys_video')
    after_total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM sys_video_episode')
    after_eps = cursor.fetchone()[0]
    cursor.execute('SELECT c.name, COUNT(v.id) FROM sys_video v JOIN sys_category c ON v.category_id=c.id GROUP BY c.id ORDER BY c.id')

    print(f'\n=== 清理完成 ===')
    print(f'视频: {before_total} → {after_total} (减少 {before_total - after_total})')
    print(f'剧集: {before_eps} → {after_eps} (减少 {before_eps - after_eps})')
    print(f'\n各分类分布:')
    for name, cnt in cursor.fetchall():
        print(f'  {name}: {cnt}')

    conn.close()


if __name__ == '__main__':
    main()
