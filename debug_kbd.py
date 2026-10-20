import time
import ctypes
from pathlib import Path

log = Path(r"C:\Users\bryantcook\Desktop\kbd_debug.txt")

user32   = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK_CONTROL = 0x11
VK_LCONTROL = 0xA2
VK_RCONTROL = 0xA3

lines = ["Started. Hold Ctrl and click in MTGO..."]
log.write_text("\n".join(lines))

last_ctrl = False
for _ in range(200):  # 20 seconds
    ctrl = bool(user32.GetAsyncKeyState(VK_CONTROL) & 0x8000)

    # foreground window
    hwnd = user32.GetForegroundWindow()
    pid  = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    handle = kernel32.OpenProcess(0x1000, False, pid.value)
    exe_buf  = ctypes.create_unicode_buffer(512)
    exe_size = ctypes.c_ulong(512)
    if handle:
        kernel32.QueryFullProcessImageNameW(handle, 0, exe_buf, ctypes.byref(exe_size))
        kernel32.CloseHandle(handle)
    length    = user32.GetWindowTextLengthW(hwnd)
    title_buf = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title_buf, length + 1)

    if ctrl != last_ctrl:
        lines.append(f"Ctrl={'DOWN' if ctrl else 'UP'}  exe={exe_buf.value}  title={title_buf.value}")
        log.write_text("\n".join(lines))
        last_ctrl = ctrl

    time.sleep(0.1)

lines.append("Done.")
log.write_text("\n".join(lines))
