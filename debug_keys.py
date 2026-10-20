import ctypes, time
from pathlib import Path

user32  = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
log     = Path(r"C:\Users\bryantcook\Desktop\key_debug.txt")

def fg_info():
    hwnd = user32.GetForegroundWindow()
    pid  = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    h = kernel32.OpenProcess(0x1000, False, pid.value)
    exe = ctypes.create_unicode_buffer(512)
    sz  = ctypes.c_ulong(512)
    if h:
        kernel32.QueryFullProcessImageNameW(h, 0, exe, ctypes.byref(sz))
        kernel32.CloseHandle(h)
    n   = user32.GetWindowTextLengthW(hwnd)
    ttl = ctypes.create_unicode_buffer(n + 1)
    user32.GetWindowTextW(hwnd, ttl, n + 1)
    return exe.value, ttl.value

lines = ["Scanning keys — press your CTRL key now, hold it for a second, then release. Repeat a few times."]
log.write_text("\n".join(lines))

prev = set()
for _ in range(300):   # 15 seconds
    pressed = set()
    for vk in range(0x01, 0xFF):
        if user32.GetAsyncKeyState(vk) & 0x8000:
            pressed.add(vk)

    appeared  = pressed - prev
    released  = prev - pressed

    if appeared:
        exe, title = fg_info()
        for vk in appeared:
            lines.append(f"DOWN  vk=0x{vk:02X} ({vk:3d})  fg_exe={exe}  fg_title={title[:60]}")
    if released:
        for vk in released:
            lines.append(f"UP    vk=0x{vk:02X} ({vk:3d})")

    if appeared or released:
        log.write_text("\n".join(lines))

    prev = pressed
    time.sleep(0.05)

lines.append("Done.")
log.write_text("\n".join(lines))
