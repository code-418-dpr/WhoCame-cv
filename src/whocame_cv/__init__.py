import os

from logger import get_logger

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
logger = get_logger(__name__)
logger.info("Importing modules")

import asyncio
import contextlib

from whocame_cv.test import main


def main_sync() -> None:
    with contextlib.suppress(KeyboardInterrupt):
        logger.info("Running the main cycle")
        asyncio.run(main())
