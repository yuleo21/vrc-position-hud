import sys

import numpy as np

from .spec import CAPTURE_H, CAPTURE_W


class WindowNotFoundError(RuntimeError):
    pass


def _enable_dpi_awareness() -> None:
    import ctypes

    # Per-Monitor v2 (-4) → Per-Monitor (2) → System の順に試す
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
        return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


def find_window_rect(title: str = "VRChat") -> tuple[int, int, int, int] | None:
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    hwnd = user32.FindWindowW(None, title)
    if not hwnd:
        hwnd = _find_window_substring(title)
    if not hwnd:
        return None

    rect = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
        return None
    width, height = rect.right - rect.left, rect.bottom - rect.top
    if width <= 0 or height <= 0:
        return None  # 最小化中など

    pt = wintypes.POINT(0, 0)
    if not user32.ClientToScreen(hwnd, ctypes.byref(pt)):
        return None
    return pt.x, pt.y, width, height


def _find_window_substring(needle: str):
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    needle_low = needle.lower()
    found = []

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def _cb(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if needle_low in buf.value.lower():
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(WNDENUMPROC(_cb), 0)
    return found[0] if found else None


class WindowsVRChatCapture:
    def __init__(self, window_title: str = "VRChat"):
        if sys.platform != "win32":
            raise RuntimeError("WindowsVRChatCapture is Windows-only")
        import mss  # 遅延 import

        _enable_dpi_awareness()
        self.window_title = window_title
        self._sct = mss.mss()
        self._rect: tuple[int, int, int, int] | None = None

    def _resolve_rect(self) -> tuple[int, int, int, int] | None:
        self._rect = find_window_rect(self.window_title)
        return self._rect

    def grab(self) -> np.ndarray:
        rect = self._rect or self._resolve_rect()
        if rect is None:
            raise WindowNotFoundError(f'window "{self.window_title}" not found')
        left, top, cw, ch = rect
        region = {
            "left": left,
            "top": top,
            "width": min(CAPTURE_W, cw),
            "height": min(CAPTURE_H, ch),
        }
        try:
            shot = self._sct.grab(region)
        except Exception:
            self._rect = None
            raise
        return np.asarray(shot)[:, :, :3]

    def refresh_window(self) -> None:
        self._resolve_rect()

    def close(self) -> None:
        try:
            self._sct.close()
        except Exception:
            pass
