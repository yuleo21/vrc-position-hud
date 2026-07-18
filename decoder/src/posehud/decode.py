import enum
from dataclasses import dataclass

import numpy as np

from .pose import Pose, Vec3
from .spec import (
    BLOCK,
    COLS,
    IDX_CHECKSUM,
    IDX_FWD,
    IDX_MAGIC,
    IDX_POS,
    IDX_TIME,
    IDX_UP,
    MAGIC,
    OFFSET_X,
    OFFSET_Y,
    ROWS,
    THRESHOLD,
)


class DecodeStatus(enum.Enum):
    OK = "ok"
    MAGIC_MISMATCH = "magic_mismatch"
    CHECKSUM_MISMATCH = "checksum_mismatch"


@dataclass(frozen=True)
class DecodeResult:
    status: DecodeStatus
    words: np.ndarray
    pose: Pose | None = None

    @property
    def ok(self) -> bool:
        return self.status is DecodeStatus.OK


_half = BLOCK // 2
_CX = OFFSET_X + np.arange(COLS) * BLOCK + _half  # (cols,)
_CY = OFFSET_Y + np.arange(ROWS) * BLOCK + _half  # (rows,)
_WEIGHTS = np.uint64(1) << np.arange(COLS - 1, -1, -1, dtype=np.uint64)


def sample_bits(frame: np.ndarray) -> np.ndarray:
    if frame.ndim != 3:
        raise ValueError(f"frame must be HxWxC, got shape {frame.shape}")
    need_h = int(_CY[-1]) + 1
    need_w = int(_CX[-1]) + 1
    if frame.shape[0] < need_h or frame.shape[1] < need_w:
        raise ValueError(
            f"frame {frame.shape[:2]} too small for grid (need >= {need_h}x{need_w})"
        )
    samples = frame[np.ix_(_CY, _CX)][:, :, :3].astype(np.uint16)
    rgb_sum = samples.sum(axis=2)  # (rows, cols)
    return rgb_sum > THRESHOLD


def pack_words(bits: np.ndarray) -> np.ndarray:
    words = bits.astype(np.uint64) @ _WEIGHTS  # (rows,)
    return words.astype(np.uint32)


def decode_words(frame: np.ndarray) -> np.ndarray:
    return pack_words(sample_bits(frame))


def validate_words(words: np.ndarray) -> DecodeStatus:
    if int(words[IDX_MAGIC]) != MAGIC:
        return DecodeStatus.MAGIC_MISMATCH
    xor = np.bitwise_xor.reduce(words[:IDX_CHECKSUM].astype(np.uint32))
    if np.uint32(xor) != words[IDX_CHECKSUM]:
        return DecodeStatus.CHECKSUM_MISMATCH
    return DecodeStatus.OK


def _words_to_vec3(words: np.ndarray, idx: slice) -> Vec3:
    floats = words[idx].astype(np.uint32).view(np.float32)
    return Vec3(float(floats[0]), float(floats[1]), float(floats[2]))


def words_to_pose(words: np.ndarray) -> Pose:
    return Pose(
        time_ms=int(words[IDX_TIME]),
        position=_words_to_vec3(words, IDX_POS),
        forward=_words_to_vec3(words, IDX_FWD),
        up=_words_to_vec3(words, IDX_UP),
    )


def decode_frame(frame: np.ndarray) -> DecodeResult:
    words = decode_words(frame)
    status = validate_words(words)
    pose = words_to_pose(words) if status is DecodeStatus.OK else None
    return DecodeResult(status=status, words=words, pose=pose)


def decode_pose(frame: np.ndarray) -> Pose | None:
    return decode_frame(frame).pose


__all__ = [
    "DecodeResult",
    "DecodeStatus",
    "decode_frame",
    "decode_pose",
    "decode_words",
    "pack_words",
    "sample_bits",
    "validate_words",
    "words_to_pose",
]
