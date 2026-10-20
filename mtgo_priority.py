#!/usr/bin/env python3
"""
MTGO Priority Overlay
Shows a "HOLDING PRIORITY" overlay when you hold Ctrl and click to cast a
spell or activate an ability in an active MTGO match.
Anchors itself to the bottom-left corner of the MTGO game board and
repositions whenever the window moves or is resized.
Right-click the overlay to quit.
"""

import sys
import ctypes
import time
import threading
import subprocess
import tkinter as tk

try:
    import mss
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "mss"], check=True)
    import mss

OVERLAY_TEXT          = "HOLDING PRIORITY"
OVERLAY_W             = 220
OVERLAY_H             = 28
OVERLAY_PAD_X         = 20    # gap between game board left edge and overlay
GAME_BOARD_Y_FRAC     = 0.73  # phase bar is ~73% down the MTGO window height
# Brightness threshold for detecting end of dark side panel vs grey game board
PANEL_BRIGHTNESS_THRESHOLD = 65
POLL_MS               = 50

user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_CONTROL = 0x11
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
COMBO_VKS  = list(range(0x41, 0x5B))  # A–Z

_WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_size_t, ctypes.c_size_t)


# ── Window helpers ────────────────────────────────────────────────────────

class _RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def _get_mtgo_rect():
    """Return (left, top, right, bottom) of the MTGO window, or None."""
    found = [None]

    def _cb(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = kernel32.OpenProcess(0x1000, False, pid.value)
        if not h:
            return True
        buf  = ctypes.create_unicode_buffer(512)
        size = ctypes.c_ulong(512)
        kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size))
        kernel32.CloseHandle(h)
        if "mtgo" in buf.value.lower():
            rect = _RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            if rect.right - rect.left > 400:
                found[0] = (rect.left, rect.top, rect.right, rect.bottom)
                return False
        return True

    cb = _WNDENUMPROC(_cb)
    user32.EnumWindows(cb, 0)
    return found[0]


def _find_game_board_left(rect):
    """Scan a horizontal row to find where the game board grey background starts.

    The side panel contains bright card text (near-white) and card art. Requiring
    20 consecutive medium-grey pixels (60-145 brightness, low colour saturation)
    skips over isolated text characters and finds the solid game board background.
    """
    left, top, right, bottom = rect
    win_h = bottom - top
    scan_y = top + int(win_h * 0.50)
    scan_x_start = left + 30
    scan_x_end   = min(left + 500, right - 50)
    try:
        with mss.mss() as sct:
            region = {
                "top":    scan_y,
                "left":   scan_x_start,
                "width":  scan_x_end - scan_x_start,
                "height": 1,
            }
            shot = sct.grab(region)
        consecutive = 0
        for i in range(shot.width):
            r, g, b = shot.pixel(i, 0)[:3]
            brightness = (r + g + b) / 3
            # Medium grey: not dark panel, not bright text/art, roughly neutral hue
            is_board_grey = (
                60 < brightness < 145
                and abs(r - g) < 25
                and abs(g - b) < 25
            )
            if is_board_grey:
                consecutive += 1
                if consecutive >= 20:
                    return scan_x_start + i - 19
            else:
                consecutive = 0
    except Exception:
        pass
    # Fallback: 10% from window left edge
    return left + int((right - left) * 0.10)


def _overlay_pos():
    """Compute (x, y) for the overlay based on the current MTGO window rect."""
    rect = _get_mtgo_rect()
    if rect:
        left, top, right, bottom = rect
        win_h     = bottom - top
        game_left = _find_game_board_left(rect)
        x = game_left + OVERLAY_PAD_X
        phase_y = top + int(win_h * GAME_BOARD_Y_FRAC)
        y = phase_y - OVERLAY_H - 30
        return x, y
    # Fallback: centre-left of screen
    sw = user32.GetSystemMetrics(0)
    sh = user32.GetSystemMetrics(1)
    return sw // 4, sh - 200 - OVERLAY_H


def _key_down(vk):
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


def _any_combo_key():
    return any(_key_down(vk) for vk in COMBO_VKS)


def _foreground_exe_and_title():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return "", ""
    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    h = kernel32.OpenProcess(0x1000, False, pid.value)
    exe_buf  = ctypes.create_unicode_buffer(512)
    exe_size = ctypes.c_ulong(512)
    if h:
        kernel32.QueryFullProcessImageNameW(h, 0, exe_buf, ctypes.byref(exe_size))
        kernel32.CloseHandle(h)
    n   = user32.GetWindowTextLengthW(hwnd)
    ttl = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, ttl, n + 1)
    return exe_buf.value.lower(), ttl.value


def _in_mtgo_match():
    exe, title = _foreground_exe_and_title()
    return "mtgo" in exe and "vs." in title.lower()


# ── Overlay ───────────────────────────────────────────────────────────────

class Overlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        try:
            self.root.attributes("-alpha", 0.85)
        except tk.TclError:
            pass
        try:
            self.root.attributes("-toolwindow", True)
        except tk.TclError:
            pass

        x, y = _overlay_pos()
        self.root.geometry(f"{OVERLAY_W}x{OVERLAY_H}+{x}+{y}")
        self.root.configure(bg="#111111")

        frame = tk.Frame(self.root, bg="#111111")
        frame.pack(expand=True, fill="both", padx=10)
        tk.Label(frame, text="◆", font=("Helvetica", 9),
                 fg="#ffaa00", bg="#111111").pack(side="left", padx=(0, 5))
        tk.Label(frame, text=OVERLAY_TEXT, font=("Helvetica", 11, "bold"),
                 fg="white", bg="#111111").pack(side="left")

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Quit", command=self._quit)
        for widget in (self.root, frame):
            widget.bind("<Button-3>", self._show_menu)

        self.root.withdraw()
        self._visible  = False
        self._running  = True
        self._last_pos = (x, y)

    def _show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def _quit(self):
        self._running = False
        self.root.destroy()

    def show(self):
        if not self._visible:
            self._visible = True
            self.root.after(0, self.root.deiconify)

    def hide(self):
        if self._visible:
            self._visible = False
            self.root.after(0, self.root.withdraw)

    def _reposition(self):
        x, y = _overlay_pos()
        if (x, y) != self._last_pos:
            self._last_pos = (x, y)
            geo = f"{OVERLAY_W}x{OVERLAY_H}+{x}+{y}"
            self.root.after(0, lambda g=geo: self.root.geometry(g))

    def run(self):
        threading.Thread(target=self._poll, daemon=True).start()
        self.root.mainloop()
        self._running = False

    def _poll(self):
        prev_ctrl = False
        prev_lbtn = False
        prev_rbtn = False
        had_combo = False

        mtgo_cache      = False
        mtgo_cache_time = 0.0
        pos_check_time  = 0.0

        while self._running:
            now  = time.monotonic()
            ctrl = _key_down(VK_CONTROL)
            lbtn = _key_down(VK_LBUTTON)
            rbtn = _key_down(VK_RBUTTON)

            # Refresh MTGO match status every 500ms
            if now - mtgo_cache_time > 0.5:
                mtgo_cache      = _in_mtgo_match()
                mtgo_cache_time = now

            # Reposition overlay every second in case window moved
            if now - pos_check_time > 1.0:
                self._reposition()
                pos_check_time = now

            # Ctrl released
            if prev_ctrl and not ctrl:
                had_combo = False
                self.hide()

            # Another key while Ctrl held = keyboard shortcut, not a cast
            if ctrl and _any_combo_key():
                had_combo = True
                self.hide()

            # Left or right click while Ctrl held = casting / activating
            click_started = (lbtn and not prev_lbtn) or (rbtn and not prev_rbtn)
            if click_started and ctrl and not had_combo and mtgo_cache:
                self.show()

            prev_ctrl = ctrl
            prev_lbtn = lbtn
            prev_rbtn = rbtn
            time.sleep(POLL_MS / 1000)


def main():
    Overlay().run()


if __name__ == "__main__":
    main()
