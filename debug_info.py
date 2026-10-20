import ctypes
import tkinter as tk
from pathlib import Path

out = []

# Screen size
root = tk.Tk()
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
root.destroy()
out.append(f"Screen: {w}x{h}")

# Overlay position would be
overlay_x = 250
overlay_y = h - 340
out.append(f"Overlay position: x={overlay_x}, y={overlay_y}")

# All window titles
import subprocess
result = subprocess.run(
    ["powershell", "-Command",
     "Get-Process | Where-Object { $_.MainWindowTitle -ne '' } | ForEach-Object { $_.MainWindowTitle }"],
    capture_output=True, text=True
)
out.append("Window titles:")
out.append(result.stdout.strip() or "(none found)")

Path(r"C:\Users\bryantcook\Desktop\mtgo_debug.txt").write_text("\n".join(out))
