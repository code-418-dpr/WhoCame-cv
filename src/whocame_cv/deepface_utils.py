import typing

import numpy as np
from deepface import DeepFace


def deepface_represent(
    img: str | np.ndarray,
    max_faces: int | None = None,
    model_name: str = "Facenet512",
    detector_backend: str = "retinaface",
    align: bool = True,
) -> list[dict[str, typing.Any]] | None:
    try:
        representations = DeepFace.represent(
            img,
            model_name=model_name,
            detector_backend=detector_backend,
            max_faces=max_faces,
            align=align,
        )
    except ValueError:
        return None
    else:
        return representations


def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> np.floating:
    return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))


def compare_embeddings(
    embedding1: np.ndarray,
    embedding2: np.ndarray,
    threshold: float = 0.5,
) -> tuple[bool, np.floating]:
    value = cosine_similarity(embedding1, embedding2)
    verdict = value > threshold
    return verdict, value


def image_np_embeddings(image_np: np.ndarray, max_faces: int | None = None) -> tuple[np.ndarray, ...] | None:
    representations = deepface_represent(image_np, max_faces)
    return (
        tuple(representation["embedding"] for representation in representations)
        if representations is not None
        else None
    )
