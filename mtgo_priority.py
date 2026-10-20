#!/usr/bin/env python3
"""
MTGO Priority Overlay
Displays a "HOLDING PRIORITY" overlay while you hold priority in Magic Online.
Double-click launch.command (macOS) or run this file directly to start.
Right-click the overlay at any time to recalibrate or quit.
"""

import sys
import json
import time
import threading
from pathlib import Path
import tkinter as tk

# Auto-install mss if missing
try:
    import mss
except ImportError:
    import subprocess
    print("Installing mss...")
    subprocess.run([sys.executable, "-m", "pip", "install", "mss"], check=True)
    import mss

# ── Configuration ─────────────────────────────────────────────────────────
CONFIG_FILE           = Path.home() / ".mtgo_priority_config.json"
POLL_INTERVAL         = 0.25   # seconds between screen samples
TOLERANCE             = 35     # RGB match threshold (0-255 per channel)
OVERLAY_TEXT          = "HOLDING PRIORITY"
OVERLAY_X             = 250    # pixels from left edge of screen
OVERLAY_BOTTOM_OFFSET = 340    # pixels from bottom of screen


# ── Config ────────────────────────────────────────────────────────────────

def load_config():
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return None


def save_config(data):
    CONFIG_FILE.write_text(json.dumps(data, indent=2))


# ── Pixel sampling ────────────────────────────────────────────────────────

def sample_pixel(x, y):
    with mss.mss() as sct:
        region = {"top": y, "left": x, "width": 2, "height": 2}
        shot = sct.grab(region)
        p = shot.pixel(0, 0)
        return p[0], p[1], p[2]


def color_matches(pixel, target, tolerance):
    return all(abs(pixel[i] - target[i]) <= tolerance for i in range(3))


# ── Calibration window ────────────────────────────────────────────────────

class CalibrationWindow:
    def __init__(self, on_complete):
        self.on_complete = on_complete
        self.root = tk.Tk()
        self.root.title("MTGO Priority Overlay")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#1e1e1e")
        self._build()
        self.root.mainloop()

    def _build(self):
        pad = {"padx": 24, "pady": 6, "bg": "#1e1e1e"}

        tk.Label(
            self.root, text="MTGO Priority Overlay",
            font=("Helvetica", 16, "bold"), fg="white", **pad
        ).pack(pady=(20, 2))

        tk.Label(
            self.root, text="Calibration required",
            font=("Helvetica", 11), fg="#888888", **pad
        ).pack(pady=(0, 12))

        tk.Label(
            self.root,
            text=(
                "1.  Open MTGO and start a game.\n"
                "2.  Hold priority so the OK button is visible.\n"
                "3.  Click Start, then move your mouse\n"
                "     over the OK button.\n"
                "4.  You have 5 seconds."
            ),
            font=("Helvetica", 11), fg="#cccccc",
            justify="left", **pad
        ).pack(pady=(0, 12))

        self.status = tk.Label(
            self.root, text="",
            font=("Helvetica", 13, "bold"), fg="#ffcc00", **pad
        )
        self.status.pack(pady=(0, 8))

        self.btn = tk.Button(
            self.root, text="Start Calibration",
            font=("Helvetica", 12, "bold"),
            bg="#2e6be6", fg="white",
            activebackground="#1a4fc4", activeforeground="white",
            relief="flat", padx=18, pady=10,
            command=self._start
        )
        self.btn.pack(pady=(0, 20))

    def _start(self):
        self.btn.config(state="disabled")
        threading.Thread(target=self._countdown, daemon=True).start()

    def _countdown(self):
        for i in range(5, 0, -1):
            self.status.config(text=f"Move mouse to indicator... {i}")
            time.sleep(1)

        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        r, g, b = sample_pixel(x, y)

        save_config({"x": x, "y": y, "color": {"r": r, "g": g, "b": b}})

        self.status.config(text=f"Saved!  RGB({r}, {g}, {b})")
        self.btn.config(text="Start Overlay", state="normal", bg="#27ae60",
                        command=self._finish)

    def _finish(self):
        self.root.destroy()
        self.on_complete()


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

        sh = self.root.winfo_screenheight()
        self.root.geometry(f"180x40+{OVERLAY_X}+{sh - OVERLAY_BOTTOM_OFFSET}")
        self.root.configure(bg="#111111")

        self.label = tk.Label(
            self.root, text=OVERLAY_TEXT,
            font=("Helvetica", 14, "bold"),
            fg="white", bg="#111111",
        )
        self.label.pack(expand=True, fill="both")

        # Right-click context menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Recalibrate", command=self._recalibrate)
        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=self.root.destroy)
        self.root.bind("<Button-3>", self._show_menu)
        self.label.bind("<Button-3>", self._show_menu)

        self.root.withdraw()
        self._visible = False

    def _show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)

    def _recalibrate(self):
        self.root.destroy()
        CalibrationWindow(on_complete=lambda: Overlay().run())

    def show(self):
        if not self._visible:
            self._visible = True
            self.root.after(0, self.root.deiconify)

    def hide(self):
        if self._visible:
            self._visible = False
            self.root.after(0, self.root.withdraw)

    def run(self):
        cfg = load_config()
        x      = cfg["x"]
        y      = cfg["y"]
        target = (cfg["color"]["r"], cfg["color"]["g"], cfg["color"]["b"])

        def poll():
            while True:
                try:
                    pixel = sample_pixel(x, y)
                    if color_matches(pixel, target, TOLERANCE):
                        self.show()
                    else:
                        self.hide()
                except Exception:
                    pass
                time.sleep(POLL_INTERVAL)

        threading.Thread(target=poll, daemon=True).start()
        self.root.mainloop()


# ── Entry point ───────────────────────────────────────────────────────────

def main():
    if load_config() is None:
        CalibrationWindow(on_complete=lambda: Overlay().run())
    else:
        Overlay().run()


if __name__ == "__main__":
    main()
