import math
from dataclasses import dataclass
from typing import NamedTuple


class Vec3(NamedTuple):
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Pose:
    """6DoF姿勢(Unity座標系: Y-up, 左手系, 単位メートル)"""

    time_ms: int  # _VRChatTimeNetworkMs
    position: Vec3
    forward: Vec3
    up: Vec3

    @property
    def yaw_deg(self) -> float:
        """+Z 基準の yaw。atan2(fwd.x, fwd.z)。"""
        return math.degrees(math.atan2(self.forward.x, self.forward.z))

    @property
    def pitch_deg(self) -> float:
        """上向きが正の pitch。asin(fwd.y)。"""
        return math.degrees(math.asin(max(-1.0, min(1.0, self.forward.y))))

    @property
    def roll_deg(self) -> float:
        """right = cross(up, fwd) の y 成分と up.y から求める。atan2(right.y, up.y)。"""
        fwd = self.forward
        up = self.up
        right_y = up.z * fwd.x - up.x * fwd.z
        return math.degrees(math.atan2(right_y, up.y))
