from pathlib import Path

import aiofiles
from piccolo.table import create_db_tables
from tqdm.asyncio import tqdm

from db.tables import UnknownVisitors, Visitors
from logger import get_logger

FACES_DIR = Path(__file__).parent / "faces"
logger = get_logger(__name__)


async def seed() -> None:
    logger.info("Creating tables")
    await create_db_tables(Visitors, UnknownVisitors, if_not_exists=True)
    await UnknownVisitors.delete(force=True)
    await Visitors.delete(force=True)

    logger.info("Iterating %s", FACES_DIR)
    visitors_to_insert = []
    async for person_dir in tqdm(tuple(FACES_DIR.iterdir())):
        person_dir: Path
        if person_dir.is_dir():
            pics = []
            for face_img in person_dir.iterdir():
                face_img: Path
                if face_img.is_file() and face_img.suffix in (".jpg", ".png"):
                    async with aiofiles.open(face_img, "rb") as f:
                        pics.append(await f.read())
                if len(pics) == 3:  # noqa: PLR2004
                    break

            if 1 <= len(pics) <= 3:  # noqa: PLR2004
                visitors_to_insert.append(
                    Visitors(
                        full_name=person_dir.name,
                        frontal_pic=pics[0],
                        left_pic=pics[1] if len(pics) > 1 else None,
                        right_pic=pics[2] if len(pics) > 2 else None,  # noqa: PLR2004
                    ),
                )

    logger.info("Inserting %s visitors", len(visitors_to_insert))
    await Visitors.insert(*visitors_to_insert)
