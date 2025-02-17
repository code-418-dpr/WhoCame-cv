import asyncio
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from db.tables import UnknownVisitors, Visitors
from logger import get_logger
from whocame_cv.deepface_utils import compare_embeddings, deepface_represent, image_np_embeddings
from whocame_cv.source_decorators import frame_series

logger = get_logger(__name__)


def single_image_embedding(image: bytes) -> np.ndarray:
    image_np = np.frombuffer(image, dtype=np.uint8)
    image_np = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    return image_np_embeddings(image_np, max_faces=1)[0]


async def get_visitors_embeddings() -> dict[str, tuple[np.ndarray, ...]]:
    raw_visitors = await Visitors.select()
    visitors = {}

    for raw_visitor in raw_visitors:
        frontal_pic: bytes = raw_visitor["frontal_pic"]
        left_pic: bytes | None = raw_visitor.get("left_pic")
        right_pic: bytes | None = raw_visitor.get("right_pic")

        frontal_embedding = single_image_embedding(frontal_pic)
        left_embedding = right_embedding = None
        if left_pic is not None:
            left_embedding = single_image_embedding(left_pic)
        if right_pic is not None:
            right_embedding = single_image_embedding(right_pic)

        visitor_id = raw_visitor["id"]
        visitor_pics = [frontal_embedding, left_embedding, right_embedding]
        visitors[visitor_id] = tuple(filter(None, visitor_pics))

    return visitors


async def save_unknown_face(
    frame: np.ndarray,
    facial_area: dict[str, Any],
    nearest_distance: float,
) -> None:
    x, y, w, h = facial_area["x"], facial_area["y"], facial_area["w"], facial_area["h"]
    face_img = frame[y : y + h, x : x + w]
    _, img_bytes = cv2.imencode(".jpg", face_img)
    face_bytes = img_bytes.tobytes()
    await UnknownVisitors(pic=face_bytes, nearest_distance=nearest_distance).save()


logger.info("Creating image vectors")
visitors = asyncio.run(get_visitors_embeddings())
recognized_visitors, unrecognized_visitors = {}, {}

total = found = 0


@frame_series(Path(__file__).parent / "videos" / "1")
async def main(frame: np.ndarray) -> None:
    global total, found  # noqa: PLW0603
    faces = deepface_represent(frame)
    if faces is None:
        return

    logger.info("Found %s faces", len(faces))
    for face in faces:
        embedding: np.ndarray = face["embedding"]
        db_id = None
        verdict, max_value = False, 0.0
        for db_id, db_embedding_list in {**unrecognized_visitors, **recognized_visitors, **visitors}.items():  # noqa: B007
            db_embedding = db_embedding_list[0]
            verdict, value = compare_embeddings(db_embedding, embedding)
            max_value = max(max_value, value)
            if not verdict and len(db_embedding_list) > 1:
                db_embedding = db_embedding_list[1]
                verdict, value = compare_embeddings(db_embedding, embedding)
                max_value = max(max_value, value)
                if not verdict and len(db_embedding_list) > 2:  # noqa: PLR2004
                    db_embedding = db_embedding_list[2]
                    verdict, value = compare_embeddings(db_embedding, embedding)
                    max_value = max(max_value, value)
            if verdict:
                break

        total += 1
        if verdict:
            if db_id not in recognized_visitors and db_id not in unrecognized_visitors:
                found += 1
                logger.info("%s / %s Recognized %s (%s)\n", found, total, db_id, max_value)
                recognized_visitors[db_id] = [embedding]
                visitors.pop(db_id)
        else:
            logger.info("%s / %s Unrecognized one of the faces (%s)\n", found, total, max_value)
            unrecognized_visitors[str(embedding)] = [embedding]
            await save_unknown_face(frame, face["facial_area"], max_value)
