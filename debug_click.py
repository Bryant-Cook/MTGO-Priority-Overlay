import time
from pathlib import Path
from pynput import mouse, keyboard

log = Path(r"C:\Users\bryantcook\Desktop\click_debug.txt")
lines = []

def on_click(x, y, button, pressed):
    if pressed:
        lines.append(f"CLICK at ({x},{y}) button={button}")
        log.write_text("\n".join(lines))

def on_press(key):
    lines.append(f"KEY {key}")
    log.write_text("\n".join(lines))
    if key == keyboard.Key.esc:
        return False

with mouse.Listener(on_click=on_click) as ml:
    with keyboard.Listener(on_press=on_press) as kl:
        kl.join()
