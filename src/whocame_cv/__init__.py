import logging
import os

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

logging.basicConfig(
    encoding="utf-8",
    level="INFO",
    filemode="w",
    format="%(name)s [%(asctime)s] %(levelname)s %(message)s",
)
logging.info("Подключение модулей")

import asyncio
import contextlib

from whocame_cv.test import main

logger = logging.getLogger(__name__)


def main_sync() -> None:
    with contextlib.suppress(KeyboardInterrupt):
        logger.info("Запуск основного цикла")
        asyncio.run(main())
