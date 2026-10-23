import pymysql
from config.setting import Config
from common.logger import logger

class DBUtil:
    def __init__(self):
        try:
            self.conn = pymysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                # 1. 这里改成了 password
                password=Config.DB_PWD, 
                database=Config.DB_NAME,
                charset='utf8mb4',
                # 字典游标，返回 {'id': 1, 'username': 'xxx'} 这种格式
                cursorclass=pymysql.cursors.DictCursor ,
                autocommit=True 
            )
            logger.info("数据库连接成功！")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def query_one(self, sql):
        """查询单条数据，返回字典（查不到返回 None）"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchone()

    def query_all(self, sql):
        """查询多条数据，返回字典列表（查不到返回空列表 []）"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def close(self):
        """关闭数据库连接"""
        self.conn.close()
        logger.info("数据库连接已关闭！")