import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(name="AutoTest"):
    log_dir=os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file=os.path.join(log_dir,"test.log")
    logger=logging.getLogger(name)
    if not logger.handlers:
        # 3. 定义日志格式（时间 - 文件名:行号 - 级别 - 信息）
        formatter = logging.Formatter(
            '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
        )

        # 4. 创建控制台输出 (你本地终端看的内容)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 5. 创建文件输出（保存到硬盘的 logs/test.log，按大小自动分割，最多存3个备份）
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# 导出一个全局唯一的 logger 实例，哪里需要哪里 import
logger = get_logger()