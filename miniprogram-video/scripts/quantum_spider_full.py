"""
量子资源 API — 全量数据爬虫（改进版）
====================================
API: https://cj.lziapi.com/api.php/provide/vod/at/json/
网站: https://lzizy8.com

改进说明：
  1. ✅ 正确提取 lzm3u8 源（index.m3u8 HLS 流），保证可播放
  2. ✅ 过滤标题含"解说""预告""花絮""片段""幕后""试看"的视频
  3. ✅ 跳过 type_id=35（电影解说）等无用分类
  4. ✅ 全量爬取（不限 100 条/类）
  5. ✅ 断点续传（已完成分类跳过）
  6. ✅ 批量插入数据库（大幅提速）
  7. ✅ 合理请求间隔，避免被封
"""

import requests
import pymysql
import time
import re
import os
import json
import socket
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===================== 配置 =====================

API_BASE = 'https://cj.lziapi.com/api.php/provide/vod/at/json/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 创建带重试机制的 Session
SESSION = requests.Session()
RETRY_STRATEGY = Retry(
    total=5,
    backoff_factor=2,      # 重试等待: 2, 4, 8, 16, 32 秒
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=RETRY_STRATEGY, pool_connections=10, pool_maxsize=20)
SESSION.mount('https://', adapter)
SESSION.mount('http://', adapter)

# 预解析 DNS，避免间歇性 DNS 失败
def resolve_host(hostname, timeout=5):
    """解析域名到 IP，带超时"""
    try:
        return socket.getaddrinfo(hostname, 443, socket.AF_INET)[0][4][0]
    except Exception:
        return None

API_HOST = 'cj.lziapi.com'
API_IP = resolve_host(API_HOST)
if API_IP:
    print(f'[DNS] {API_HOST} → {API_IP}')
else:
    print(f'[DNS] ⚠️ 无法解析 {API_HOST}，将使用标准请求')

DB_CONFIG = {
    'host': 'localhost', 'user': 'root', 'password': '123456',
    'database': 'video_platform', 'charset': 'utf8mb4',
}

REQUEST_DELAY = 0.3       # 每次API请求间隔（秒）
BATCH_SIZE = 50           # 每批提交多少条到数据库

CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), 'quantum_checkpoint.txt')
ERROR_LOG_FILE = os.path.join(os.path.dirname(__file__), 'quantum_errors.jsonl')

# ===== 过滤关键词（标题包含这些词则跳过） =====
FILTER_KEYWORDS = [
    '解说', '预告', '花絮', '片段', '幕后', '试看', '赏析',
    '速看', '混剪', '盘点', '汇总', '合集', 'cut', 'CUT',
    '预告片', '片花', '宣传片', '特辑', '花young',
]

# ===== 分类映射 =====
# 我们数据库的分类：1=电影, 2=电视剧, 3=动漫, 4=综艺, 5=纪录片
CATEGORY_MAP = {
    # 电影类
    1: 1,   # 电影片（通用）
    6: 1,   # 剧情片
    7: 1,   # 喜剧片
    8: 1,   # 爱情片
    9: 1,   # 科幻片
    10: 1,  # 恐怖片
    11: 1,  # 动作片
    12: 1,  # 战争片
    34: 1,  # 动画片（电影类动画）
    # 电视剧类
    2: 2,   # 连续剧（通用）
    13: 2,  # 国产剧
    14: 2,  # 港剧
    15: 2,  # 日剧
    16: 2,  # 欧美剧
    21: 2,  # 台剧
    22: 2,  # 日本剧
    23: 2,  # 韩剧
    24: 2,  # 泰剧
    # 综艺类
    25: 4,  # 大陆综艺
    26: 4,  # 港台综艺
    27: 4,  # 日韩综艺
    28: 4,  # 欧美综艺
    # 动漫类
    3: 3,   # 动画片（通用）
    4: 3,   # 动漫片（通用）
    29: 3,  # 国产动漫
    30: 3,  # 日韩动漫
    31: 3,  # 欧美动漫
    32: 3,  # 港台动漫
    33: 3,  # 海外动漫
    # 纪录片
    20: 5,  # 纪录片
    # ===== 跳过的分类 =====
    # 35: 电影解说（23,284条）— 标题含"解说"会被过滤，但直接跳过更高效
    # 36: 短剧（3条）
    # 37-39: 其他非标准分类
}

# ===== 分类名称（仅用于日志显示） =====
TYPE_NAMES = {
    1: '电影片', 2: '连续剧', 3: '动画片', 4: '动漫片',
    6: '剧情片', 7: '喜剧片', 8: '爱情片', 9: '科幻片',
    10: '恐怖片', 11: '动作片', 12: '战争片',
    13: '国产剧', 14: '港剧', 15: '日剧', 16: '欧美剧',
    20: '纪录片', 21: '台剧', 22: '日剧', 23: '韩剧', 24: '泰剧',
    25: '大陆综艺', 26: '港台综艺', 27: '日韩综艺', 28: '欧美综艺',
    29: '国产动漫', 30: '日韩动漫', 31: '欧美动漫', 32: '港台动漫',
    33: '海外动漫', 34: '动画片',
    35: '【跳过】电影解说', 36: '【跳过】短剧',
}


# ===================== 自适应并发控制器 =====================

class AdaptiveConcurrency:
    """
    自适应并发控制器
    - 初始并发 5 线程
    - 连续成功 ↗ 可尝试增加并发（上限 8）
    - 错误率高于 30% ↘ 降低并发
    - 错误率持续高 ↗ 回退到单线程
    """

    def __init__(self, initial=5, min_workers=1, max_workers=8):
        self.current = initial
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.success_count = 0
        self.error_count = 0
        self.consecutive_errors = 0
        self.lock = threading.Lock()
        self._ratelimited = False  # 是否已触发限流模式

    def record_success(self):
        with self.lock:
            self.success_count += 1
            self.consecutive_errors = 0
            # 每连续成功 50 条，尝试增加一个并发（不超过上限）
            if self.success_count % 50 == 0 and self.current < self.max_workers and not self._ratelimited:
                self.current += 1
                log_message(f'  ⚡ 并发提升至 {self.current} 线程')

    def record_error(self):
        with self.lock:
            self.error_count += 1
            self.consecutive_errors += 1
            total = self.success_count + self.error_count
            if total > 20:
                error_rate = self.error_count / total
                # 错误率 > 30% 或 连续错误 > 5
                if error_rate > 0.3 or self.consecutive_errors > 5:
                    old = self.current
                    self.current = max(self.min_workers, self.current - 1)
                    if self.current != old:
                        log_message(f'  ⚠️ 检测到限流/错误率{error_rate:.0%}，并发降为 {self.current} 线程')
                    # 如果已经降到 1 了还出错，标记限流模式
                    if self.current == 1 and self.consecutive_errors > 10:
                        self._ratelimited = True
                        log_message('  🐢 持续高错误，进入单线程安全模式')

    @property
    def workers(self):
        return self.current

    @property
    def is_ratelimited(self):
        return self._ratelimited


def log_message(msg):
    """线程安全的打印"""
    now = datetime.now().strftime('%H:%M:%S')
    print(f'[{now}] {msg}')


# ===================== 工具函数 =====================

def should_skip_by_title(title):
    """检查标题是否包含过滤关键词"""
    if not title:
        return False
    for kw in FILTER_KEYWORDS:
        if kw in title:
            return True
    return False


def clean_html(text):
    """清理HTML标签"""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'")
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_lzm3u8_episodes(play_url, vod_play_from=''):
    """
    提取 lzm3u8 源的分集列表

    vod_play_url 格式：
        源1_ep1$url#源1_ep2$url#...$$$源2_ep1$url#源2_ep2$url#...
    vod_play_from 格式：
        liangzi,lzm3u8  (列表接口) 或 liangzi$$$lzm3u8 (详情接口)

    返回: [(episode_number, title, url), ...] 或 []（无有效数据）
    """
    if not play_url:
        return []

    # 确定 lzm3u8 源的索引位置
    if vod_play_from:
        # 按 $$$ 或 , 分割源名称
        source_names = re.split(r'[,$]{3,}|,', vod_play_from)
        source_names = [s.strip().lower() for s in source_names if s.strip()]
    else:
        source_names = []

    # 按 $$$ 分割不同的播放源
    sources = play_url.split('$$$')

    # 确定要取哪个源（优先 lzm3u8）
    target_source_idx = -1
    for i, name in enumerate(source_names):
        if 'lzm3u8' in name:
            target_source_idx = i
            break

    # 如果没找到 lzm3u8，或者索引超出sources范围，尝试找m3u8格式的源
    if target_source_idx < 0 or target_source_idx >= len(sources):
        # 遍历查找包含 .m3u8 的源
        for i, src in enumerate(sources):
            if '.m3u8' in src:
                target_source_idx = i
                break

    # 仍然没找到，就用第一个非空的源
    if target_source_idx < 0:
        for i, src in enumerate(sources):
            if src.strip():
                target_source_idx = i
                break

    if target_source_idx < 0 or target_source_idx >= len(sources):
        return []

    # 解析目标源的分集
    target_source = sources[target_source_idx].strip()
    return _parse_episodes_from_source(target_source)


def _parse_episodes_from_source(source_text):
    """
    解析单一源的剧集
    格式: 第01集$url#第02集$url#...
    """
    episodes = []
    if not source_text:
        return episodes

    parts = source_text.split('#')
    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        if '$' in part:
            title, url = part.split('$', 1)
            url = url.strip()
            if url and url.startswith('http'):
                # 提取集数
                ep_num = i + 1
                match = re.search(r'第(\d+)集', title)
                if match:
                    ep_num = int(match.group(1))
                else:
                    match = re.search(r'(\d+)', title)
                    if match:
                        ep_num = int(match.group(1))

                episodes.append((ep_num, title.strip(), url))

    if not episodes and source_text:
        # 可能是单集（电影格式：标题$url）
        if '$' in source_text:
            title, url = source_text.split('$', 1)
            url = url.strip()
            if url.startswith('http'):
                episodes.append((1, title.strip(), url))

    return episodes


def fetch_page(type_id, page, page_size=20):
    """获取一页列表数据"""
    url = f'{API_BASE}?ac=list&t={type_id}&pg={page}&pagesize={page_size}'
    for attempt in range(3):
        try:
            r = SESSION.get(url, headers=HEADERS, timeout=30)
            return r.json()
        except Exception as e:
            if attempt < 2:
                wait = (attempt + 1) * 3
                print(f'    [重试 {attempt+1}/3] 等待{wait}s后重试: {e}')
                time.sleep(wait)
            else:
                print(f'    [请求失败] {e}')
    return None


def fetch_detail(vod_id):
    """获取视频详情（带指数退避重试）"""
    url = f'{API_BASE}?ac=detail&ids={vod_id}'
    for attempt in range(5):
        try:
            r = SESSION.get(url, headers=HEADERS, timeout=30)
            data = r.json()
            if data.get('list'):
                return data['list'][0]
            return None
        except requests.exceptions.ConnectionError as e:
            if attempt < 4:
                wait = (attempt + 1) * 5  # 5, 10, 15, 20秒
                print(f'    [连接错误 重试{attempt+1}/5] {wait}s后重试...', end=' ')
                # 有时 DNS 恢复需要时间，重新解析
                ip = resolve_host(API_HOST)
                print(f'(DNS: {ip or "不通"})')
                time.sleep(wait)
            else:
                print(f'    [详情请求失败] {e}')
        except Exception as e:
            if attempt < 2:
                wait = (attempt + 1) * 3
                print(f'    [错误 重试{attempt+1}/3] {wait}s后重试: {e}')
                time.sleep(wait)
            else:
                print(f'    [详情请求失败] {e}')
    return None


def read_checkpoint():
    """读取断点文件，返回已完成的type_id列表"""
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())


def write_checkpoint(type_id):
    """追加写入断点"""
    with open(CHECKPOINT_FILE, 'a') as f:
        f.write(f'{type_id}\n')


def log_error(vod_id, title, type_id, reason):
    """记录错误到日志文件"""
    with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps({
            'vod_id': vod_id, 'title': title,
            'type_id': type_id, 'reason': reason,
            'time': datetime.now().isoformat()
        }, ensure_ascii=False) + '\n')


# ===================== 主逻辑 =====================

def main():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    completed_types = read_checkpoint()
    total_inserted = 0
    total_episodes = 0
    total_skipped = 0
    total_errors = 0

    print(f'断点文件: {CHECKPOINT_FILE}')
    print(f'已完成的分类: {sorted(completed_types) if completed_types else "无"}')
    print(f'过滤关键词: {FILTER_KEYWORDS}')
    print(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'=' * 60)

    for type_id, our_cat_id in sorted(CATEGORY_MAP.items()):
        type_name = TYPE_NAMES.get(type_id, f'未知({type_id})')

        # 跳过断点中已完成的分类
        if str(type_id) in completed_types:
            print(f'⏭️  [{type_id}] {type_name} — 已完成，跳过（断点续传）')
            continue

        cat_names = {1: '电影', 2: '电视剧', 3: '动漫', 4: '综艺', 5: '纪录片'}
        print(f'\n{"=" * 60}')
        print(f'▶  [{type_id}] {type_name} → {cat_names.get(our_cat_id, "未知")}(category_id={our_cat_id})')
        print(f'{"=" * 60}')

        # 获取第一页，了解总量
        first_page = fetch_page(type_id, 1)
        if not first_page:
            print('  ❌ API无响应，跳过此分类')
            continue

        total = first_page.get('total', 0)
        pagecount = first_page.get('pagecount', 1)

        if total == 0:
            print('  ℹ️  空分类，跳过')
            write_checkpoint(type_id)
            continue

        page_size = 20
        print(f'  总量: {total} 条, 总页数: {pagecount}')

        # ===== 第一遍：收集所有vod_id和基本信息 =====
        all_items = []
        items_seen = set()  # 去重

        for pg in range(1, pagecount + 1):
            if pg == 1:
                page_data = first_page
            else:
                time.sleep(REQUEST_DELAY)
                page_data = fetch_page(type_id, pg)

            if not page_data or not page_data.get('list'):
                if pg > 1:
                    print(f'    ⚠️  第{pg}页获取失败，跳过')
                continue

            for item in page_data.get('list', []):
                vod_id = item.get('vod_id')
                if vod_id and vod_id not in items_seen:
                    items_seen.add(vod_id)
                    all_items.append(item)

            if pg % 20 == 0 or pg == pagecount:
                print(f'  列表进度: {pg}/{pagecount} 页, 已收集 {len(all_items)} 条', end='\r')

        print(f'\n  共收集 {len(all_items)} 条（去重后）')

        # ===== 第二遍：并发获取详情并导入 =====
        cat_inserted = 0
        cat_episodes = 0
        cat_skipped = 0
        cat_errors = 0
        batch_buffer = []  # 批量缓存
        concurrency = AdaptiveConcurrency(initial=5)
        stats_lock = threading.Lock()

        def flush_batch():
            """将缓存中的数据批量写入数据库"""
            nonlocal cat_inserted, cat_episodes, batch_buffer
            if not batch_buffer:
                return

            for record in batch_buffer:
                try:
                    # 插入 sys_video
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    sql = """INSERT INTO sys_video
                        (title, category_id, cover_url, video_url, description, director, actors,
                         year, area, duration, score, tags, play_count, status, is_recommend, create_time, update_time)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 1, 0, %s, %s)"""

                    cursor.execute(sql, (
                        record['title'], our_cat_id, record['pic'], record['video_url'],
                        record['description'], record['director'], record['actors'],
                        record['year'], record['area'], record['duration'],
                        record['score'], record['tags'], now, now
                    ))
                    new_id = cursor.lastrowid

                    # 插入剧集
                    if record['episodes']:
                        ep_sql = """INSERT INTO sys_video_episode
                            (video_id, episode_number, episode_title, video_url, duration, create_time)
                            VALUES (%s, %s, %s, %s, %s, %s)"""
                        ep_data = [
                            (new_id, ep[0], ep[1], ep[2], '', now)
                            for ep in record['episodes']
                        ]
                        cursor.executemany(ep_sql, ep_data)
                        cat_episodes += len(record['episodes'])

                    cat_inserted += 1

                except Exception as e:
                    conn.rollback()
                    log_error(record.get('vod_id', '?'), record['title'], type_id, f'数据库错误: {e}')

            conn.commit()
            batch_buffer = []

        def process_item(item_data):
            """处理单个视频项（在子线程中运行）"""
            vod_id = item_data['vod_id']
            vod_name = item_data.get('vod_name', '')
            vod_play_from = item_data.get('vod_play_from', '')

            # 标题过滤
            if should_skip_by_title(vod_name):
                return {'action': 'skip', 'reason': '标题过滤'}

            # 获取详情
            detail = fetch_detail(vod_id)
            if not detail:
                return {'action': 'skip', 'reason': '详情获取失败', 'vod_id': vod_id, 'vod_name': vod_name}

            # 提取字段
            title = detail.get('vod_name', vod_name)

            # 再次检查标题
            if should_skip_by_title(title):
                return {'action': 'skip', 'reason': '标题过滤(详情)'}

            pic = detail.get('vod_pic', '')
            director = detail.get('vod_director', '')
            actor = detail.get('vod_actor', '')
            area = detail.get('vod_area', '')
            year_str = detail.get('vod_year', '')
            score_str = detail.get('vod_score', '0')
            vod_class = detail.get('vod_class', '')
            vod_content = detail.get('vod_content', '')
            vod_remarks = detail.get('vod_remarks', '')
            play_url = detail.get('vod_play_url', '')

            description = clean_html(vod_content)

            year = 0
            if year_str:
                match = re.search(r'(\d{4})', str(year_str))
                if match:
                    year = int(match.group(1))

            try:
                score = float(score_str) if score_str else 0.0
            except ValueError:
                score = 0.0

            episodes = parse_lzm3u8_episodes(play_url, vod_play_from)
            ep_count = len(episodes)

            is_multi_episode = ep_count > 1
            video_url = ''
            if not is_multi_episode and episodes:
                video_url = episodes[0][2]

            duration = vod_remarks if vod_remarks else ''
            if not duration and not is_multi_episode:
                duration = 'HD'

            return {
                'action': 'record',
                'record': {
                    'vod_id': vod_id,
                    'title': title,
                    'pic': pic,
                    'video_url': video_url,
                    'description': description,
                    'director': director,
                    'actors': actor,
                    'year': year,
                    'area': area,
                    'duration': duration,
                    'score': score,
                    'tags': vod_class,
                    'episodes': episodes,
                }
            }

        # 并发处理：使用 ThreadPoolExecutor
        total_items = len(all_items)
        processed = 0
        with ThreadPoolExecutor(max_workers=concurrency.workers) as executor:

            def submit_batch(start_idx, batch_size):
                """提交一批任务"""
                batch = all_items[start_idx:start_idx + batch_size]
                futures = {}
                for i, item in enumerate(batch):
                    future = executor.submit(process_item, item)
                    futures[future] = start_idx + i
                return futures

            # 初始提交一批（并发数 * 20，保持流水线饱满）
            window_size = concurrency.workers * 20
            pending_futures = submit_batch(0, window_size)
            next_idx = min(window_size, total_items)
            submitted_count = next_idx

            while pending_futures:
                # 等待任意一个完成
                done = set()
                for future in as_completed(pending_futures.keys()):
                    done.add(future)
                    idx = pending_futures[future]
                    processed += 1

                    try:
                        result = future.result()
                    except Exception as e:
                        with stats_lock:
                            concurrency.record_error()
                            cat_errors += 1
                        log_message(f'  ❌ [{processed}/{total_items}] 处理异常: {e}')
                        continue

                    if result['action'] == 'skip':
                        if result.get('reason') == '详情获取失败':
                            with stats_lock:
                                concurrency.record_error()
                                cat_errors += 1
                            if cat_errors <= 5:
                                log_message(f'  ❌ [{processed}/{total_items}] ID={result.get("vod_id")} {result.get("vod_name")} — 详情获取失败')
                        else:
                            with stats_lock:
                                cat_skipped += 1
                        continue

                    # 成功获取到记录
                    with stats_lock:
                        concurrency.record_success()
                    batch_buffer.append(result['record'])

                    # 满一批就写入
                    if len(batch_buffer) >= BATCH_SIZE:
                        flush_batch()
                        log_message(f'  ✅ [{processed}/{total_items}] 已导入 {cat_inserted} 部, {cat_episodes} 集 (跳过{cat_skipped}) | 并发{concurrency.workers}')

                    break  # 一次只处理一个完成的任务，然后重新检查并发设置

                # 移除已完成的任务
                for f in done:
                    del pending_futures[f]

                # 检查是否需要调整并发
                if concurrency.is_ratelimited and concurrency.workers == 1:
                    # 限流模式：不再使用并发，回退到单线程处理剩余任务
                    remaining = total_items - processed
                    log_message(f'  🐢 回退到单线程模式处理剩余 {remaining} 条...')
                    # 取消所有未完成的任务
                    for f in pending_futures:
                        f.cancel()
                    pending_futures.clear()
                    executor.shutdown(wait=False)

                    # 用单线程处理剩余的
                    for idx in range(processed, total_items):
                        item = all_items[idx]
                        result = process_item(item)
                        if result['action'] == 'skip':
                            if result.get('reason') == '详情获取失败':
                                cat_errors += 1
                            else:
                                cat_skipped += 1
                            continue

                        batch_buffer.append(result['record'])
                        if len(batch_buffer) >= BATCH_SIZE:
                            flush_batch()
                            log_message(f'  ✅ [{idx+1}/{total_items}] 已导入 {cat_inserted} 部, {cat_episodes} 集 (跳过{cat_skipped}) (单线程)')

                    break  # 退出 while 循环

                # 提交新任务来填补空缺
                while len(pending_futures) < window_size and next_idx < total_items:
                    item = all_items[next_idx]
                    future = executor.submit(process_item, item)
                    pending_futures[future] = next_idx
                    next_idx += 1
                    submitted_count += 1

                # 如果所有任务都提交了且无待处理的，退出
                if not pending_futures:
                    break

                # 自适应调整窗口大小
                new_window = concurrency.workers * 20
                if new_window != window_size:
                    window_size = new_window

        # 写入剩余批次
        flush_batch()

        total_inserted += cat_inserted
        total_episodes += cat_episodes
        total_skipped += cat_skipped
        total_errors += cat_errors

        print(f'\n  📊 [{type_name}] 完成: 导入 {cat_inserted} 部, {cat_episodes} 集, 跳过 {cat_skipped} 条, 错误 {cat_errors} 条')

        # 写入断点
        write_checkpoint(type_id)
        completed_types.add(str(type_id))

    # ===== 最终统计 =====
    print(f'\n\n{"=" * 60}')
    print(f'🏁 爬取完成!')
    print(f'{"=" * 60}')
    print(f'⏱  结束时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'✅ 总计导入: {total_inserted} 部视频')
    print(f'📺 总计集数: {total_episodes} 集')
    print(f'⏭️  总计跳过(过滤): {total_skipped} 条')
    print(f'❌ 总计错误: {total_errors} 条')

    # 数据库统计
    try:
        cursor.execute("""
            SELECT c.name, COUNT(*)
            FROM sys_video v JOIN sys_category c ON v.category_id = c.id
            GROUP BY c.id ORDER BY c.id
        """)
        print(f'\n📊 各分类数量:')
        for cat_name, cnt in cursor.fetchall():
            print(f'  {cat_name}: {cnt} 部')

        cursor.execute("SELECT COUNT(DISTINCT e.video_id) FROM sys_video_episode e")
        with_eps = cursor.fetchone()[0]
        print(f'  (其中有多集数据的视频: {with_eps} 部)')

        cursor.execute("SELECT COUNT(*) FROM sys_video WHERE video_url != ''")
        single_url = cursor.fetchone()[0]
        print(f'  单视频(无分集): {single_url} 部')
    except Exception as e:
        print(f'  统计查询失败: {e}')

    conn.close()
    print(f'\n📝 详细错误日志: {ERROR_LOG_FILE}')
    print(f'📝 断点文件: {CHECKPOINT_FILE}')


if __name__ == '__main__':
    main()
