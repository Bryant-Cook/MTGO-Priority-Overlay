# MTGO Priority Overlay

Displays a "HOLDING PRIORITY" overlay on your screen while you hold priority in Magic Online. The overlay appears automatically and disappears after you pass.

## Requirements

- Windows (any version)
- Magic Online running in a window, not full-screen

## Installation

**1. Install Python.**

Download Python from [python.org/downloads](https://www.python.org/downloads/) and run the installer. On the first screen, check the box that says **Add Python to PATH** before clicking Install Now.

**2. Download this project.**

Click the green Code button at the top of this page and select Download ZIP. Extract the ZIP to any folder on your computer.

**3. Run the installer.**

Open the extracted folder and double-click `install.bat`. The installer sets up everything and adds the overlay to your Windows startup programs. The overlay will now run automatically every time you start your computer.

**4. Calibrate (first run only).**

The first time the overlay starts, a setup window appears. Follow the steps on screen. Get into a game of MTGO and hold priority. Make sure the OK button is visible. Click Start, then move your mouse over the OK button. You have 5 seconds.

After calibration, the overlay is fully automatic. You never need to do this again unless you move or resize the MTGO window.

## How it works

The overlay watches a single pixel on your screen. During calibration, you point to the MTGO priority indicator and the overlay learns its color. After that, it samples that pixel 4 times per second. The overlay appears while the pixel matches the calibrated color and disappears after it changes.

## Recalibrate

If you move or resize the MTGO window, right-click the overlay and select Recalibrate.

## Uninstall

Double-click `uninstall.bat` in the project folder. This removes the overlay from your startup programs.

## Troubleshooting

### The overlay never appears

Make sure MTGO is running in a window, not full-screen. Run calibration again by right-clicking the overlay and selecting Recalibrate. Make sure the priority indicator is visible on screen while you calibrate.

### The overlay appears outside my priority window

Right-click the overlay, select Recalibrate, and aim at a more specific part of the priority indicator.

### The overlay flickers

Open `mtgo_priority.py` in Notepad and change `TOLERANCE = 35` to a higher number, such as `TOLERANCE = 50`. Save the file and restart the overlay.

## License

MIT License.
