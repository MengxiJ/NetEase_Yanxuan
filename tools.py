import logging
import os
import time
from datetime import datetime
from logging import handlers

from config import BASE_DIR


class GetLog:
    """日志管理器（参照原子化框架日志规范：按天滚动 + 控制台输出）"""

    _log = None

    @classmethod
    def get_log(cls):
        if cls._log is None:
            cls._log = logging.getLogger()
            cls._log.setLevel(logging.INFO)

            # 避免重复添加 handler
            if not cls._log.handlers:
                log_dir = os.path.join(BASE_DIR, "log")
                os.makedirs(log_dir, exist_ok=True)
                filename = os.path.join(
                    log_dir,
                    "app-{}.log".format(time.strftime("%Y%m%d")),
                )

                # 文件处理器（按天滚动）
                tf = handlers.TimedRotatingFileHandler(
                    filename=filename,
                    when="midnight",
                    interval=1,
                    backupCount=7,
                    encoding="utf-8",
                )
                fmt = logging.Formatter(
                    "%(asctime)s %(levelname)s [%(filename)s(%(funcName)s:%(lineno)d)] - %(message)s"
                )
                tf.setFormatter(fmt)
                cls._log.addHandler(tf)

                # 控制台处理器
                sh = logging.StreamHandler()
                sh.setFormatter(fmt)
                cls._log.addHandler(sh)

        return cls._log


def get_timestamp_str():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
