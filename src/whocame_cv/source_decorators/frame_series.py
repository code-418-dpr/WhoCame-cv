from collections.abc import Callable, Coroutine
from functools import wraps
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy import ndarray


def frame_series(
    folder_path: Path,
) -> Callable[
    [Callable[[ndarray], Coroutine[Any, Any, None]]],
    Callable[[], Coroutine[Any, Any, None]],
]:
    def decorator(func: Callable[[np.ndarray], Coroutine[Any, Any, None]]) -> Callable[[], Coroutine[Any, Any, None]]:
        @wraps(func)
        async def wrapper() -> None:
            image_files = [f for f in folder_path.iterdir() if f.is_file and f.suffix in (".jpg", ".jpeg", ".png")]

            for num, image_file in enumerate(image_files):
                frame = cv2.imread(image_file)

                if frame is None:
                    break

                await func(frame)

                cv2.imshow("Frame", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            cv2.destroyAllWindows()

        return wrapper

    return decorator
