import sys
import traceback
from core.logger import logger
from app import App


def main():
    try:
        logger.info("应用启动")
        app = App(sys.argv)
        logger.info("进入主事件循环")
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"应用崩溃: {str(e)}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()