from collections.abc import Callable, Coroutine
from typing import Any

import cv2
import numpy as np


def front_camera(
    func: Callable[[np.ndarray], Coroutine[Any, Any, None]],
) -> Callable[[], Coroutine[Any, Any, None]]:
    async def wrapper() -> None:
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            await func(frame)

            cv2.imshow("Frame", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    return wrapper
