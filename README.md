# MTGO Priority Overlay

Displays a "HOLDING PRIORITY" indicator on your screen while you hold priority in Magic Online. When you hold Ctrl and click to cast a spell or activate an ability during an active match, the overlay appears. When you release Ctrl, it disappears.

No calibration. No configuration. Install once and it runs automatically.

## Requirements

- Windows
- Magic Online running in a window (not full-screen)
- Python 3.8 or later

## Installation

### 1. Install Python

Download Python from [python.org/downloads](https://www.python.org/downloads/) and run the installer. On the first screen, check the box that says **Add Python to PATH** before clicking Install Now.

### 2. Download this project

Click the green **Code** button at the top of this page and select **Download ZIP**. Extract the ZIP to any folder on your computer.

### 3. Run the installer

Open the extracted folder and double-click `install.bat`. The installer sets up everything and adds the overlay to your Windows startup programs. The overlay starts immediately and will run automatically every time you log in.

That is all. There is nothing else to configure.

## How it works

The overlay watches for a specific combination of inputs while Magic Online is in the foreground during a match:

- You hold **Ctrl** (the key MTGO uses to hold priority)
- You **left-click or right-click** to cast a spell or activate an ability

When both happen at the same time, the overlay appears in the lower-left corner of the MTGO game board, just above the phase bar. When you release Ctrl, it disappears.

If you move or resize the MTGO window, or open and close side panels inside MTGO, the overlay repositions itself automatically.

Keyboard shortcuts (Ctrl + any letter key) do not trigger the overlay.

## Uninstall

Double-click `uninstall.bat` in the project folder.

## Troubleshooting

### The overlay never appears

Make sure you are in an active match. When MTGO shows a game in progress, the overlay activates. It does not appear in the lobby, deck editor, or collection viewer.

Make sure MTGO is running in a window, not full-screen.

Hold Ctrl first, then click while still holding it.

### The overlay is in the wrong position

Make sure MTGO is running in a window, not full-screen. If you move or resize the window, the overlay corrects its position within one second.

### The overlay appears when I use a keyboard shortcut

This is handled automatically for letter keys (Ctrl+A through Ctrl+Z). If a specific shortcut still triggers the overlay, open `mtgo_priority.py` in Notepad and add the relevant virtual key code to the `COMBO_VKS` list.

## License

MIT License.
