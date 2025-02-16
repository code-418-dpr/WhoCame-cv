from pathlib import Path

import aiofiles

from db.tables import Visitors

FACES_DIR = Path(__file__).parent / "faces"


async def seed() -> None:
    visitors_to_insert = []

    for person_dir in FACES_DIR.iterdir():
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

    await Visitors.insert(*visitors_to_insert)
