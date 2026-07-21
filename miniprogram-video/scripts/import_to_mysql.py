"""从 SQL 文件解析数据并导入 MySQL"""
import pymysql
import re
import random

# 连接数据库
conn = pymysql.connect(
    host='localhost', user='root', password='123456',
    database='video_platform', charset='utf8mb4'
)
cursor = conn.cursor()

# 删除刚导入的错误数据（id > 12 的旧数据保留）
cursor.execute('DELETE FROM sys_video WHERE id > 12')
conn.commit()
print('已清除旧的新数据')

# 读取 SQL 文件
with open('E:/project/miniprogram-video/scripts/douban_movies.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 VALUES 部分
m = re.search(r'VALUES\s+(.*?);', content, re.DOTALL)
if not m:
    print('未找到 VALUES')
    exit(1)

values_text = m.group(1).strip()

# 逐行解析
lines = values_text.split(',\n')
success = 0

for i, line in enumerate(lines):
    line = line.strip().rstrip(',').rstrip(')')
    if not line or line.startswith('--'):
        continue

    try:
        # 解析 CSV 风格的行: ('title', 1, 'url', ...)
        # 手动按逗号分割，但跳过引号内的逗号
        parts = []
        current = ''
        in_quote = False
        for ch in line.lstrip('('):
            if ch == "'":
                in_quote = not in_quote
                current += ch
            elif ch == ',' and not in_quote:
                parts.append(current.strip())
                current = ''
            else:
                current += ch
        if current.strip():
            parts.append(current.strip())

        if len(parts) < 14:
            print(f'  行{i+1}: 字段不足 ({len(parts)})，跳过')
            continue

        def clean(s):
            s = s.strip()
            if s.startswith("'") and s.endswith("'"):
                s = s[1:-1]
            # 处理转义的单引号
            s = s.replace("''", "'")
            return s

        title = clean(parts[0])
        cat_id = int(parts[1])
        cover_url = clean(parts[2])
        video_url = clean(parts[3])
        description = clean(parts[4])
        director = clean(parts[5])
        actors = clean(parts[6])
        year = int(parts[7]) if parts[7].strip(')') != '0' else 0
        area = clean(parts[8])
        duration = clean(parts[9])
        score = float(parts[10].rstrip(')'))
        tags = clean(parts[11])
        is_recommend = int(parts[12].rstrip(')'))
        play_count = int(parts[13].rstrip(')'))

        sql = """INSERT INTO sys_video
            (title, category_id, cover_url, video_url, description, director, actors, year, area, duration, score, tags, is_recommend, play_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        cursor.execute(sql, (
            title, cat_id, cover_url, video_url, description,
            director, actors, year, area, duration, score,
            tags, is_recommend, play_count
        ))
        conn.commit()
        success += 1
        print(f'  + {title} | {director} | {actors}')

    except Exception as e:
        conn.rollback()
        print(f'  - 行{i+1}: {e}')
        print(f'    数据: {line[:120]}')

print(f'\n== 成功导入 {success} 条')
cursor.execute('SELECT COUNT(*) FROM sys_video')
print(f'数据库总行数: {cursor.fetchone()[0]}')

cursor.execute('SELECT id, title, director, actors, year, area, score FROM sys_video ORDER BY id')
print(f'\n{"ID":4s} {"标题":22s} {"导演":18s} {"主演":24s} {"评分":4s} {"年份":6s}')
print('-' * 80)
for r in cursor.fetchall():
    print(f'{r[0]:4d} {r[1]:22s} {str(r[2] or ""):18s} {str(r[3] or ""):24s} {float(r[6]) if r[6] else 0:4.1f} {r[4] if r[4] else 0:6d}')

conn.close()
