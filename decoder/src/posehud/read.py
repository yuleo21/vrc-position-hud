import time
from collections.abc import Iterator

from .capture import WindowsVRChatCapture
from .decode import decode_pose
from .pose import Pose

_IDLE_POLL_INTERVAL_S = 0.005


def poses(window_title: str = "VRChat") -> Iterator[Pose]:
    capture = WindowsVRChatCapture(window_title)
    last_time_ms: int | None = None
    try:
        while True:
            pose = decode_pose(capture.grab())
            if pose is None or pose.time_ms == last_time_ms:
                time.sleep(_IDLE_POLL_INTERVAL_S)
                continue
            last_time_ms = pose.time_ms
            yield pose
    finally:
        capture.close()
