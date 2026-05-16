import logging
import sys
import os
from datetime import datetime


_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")


def setup_logger(name: str = "定时休息") -> logging.Logger:
    os.makedirs(_LOG_DIR, exist_ok=True)

    log_file = os.path.join(_LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("=" * 60)
    logger.info(f"日志系统初始化完成，日志文件: {log_file}")
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"系统平台: {sys.platform}")
    logger.info("=" * 60)

    return logger


logger = setup_logger()