# HACK_2026
A embedded system project that focuses on designing and prototyping a custom musical instrument that requires using a Raspberry Pico, Keypad, Oled Display. Digital Audio Converter, Joystick ,Slide Potentiometer, and Buttons with custom 3d printed case


## Setting up the Pico

The firmware in `pico/` runs on CircuitPython. Copy the **contents** of `pico/`
(not the folder itself) to the root of the CIRCUITPY drive — `code.py` must sit
at the top level, since that's what CircuitPython runs on boot.

### Required libraries

The `lib/` folder is **not** in this repo — you have to install it on each board.
Without it the Pico fails on the first import and nothing runs: no audio, no
display, no serial output to the website.

The easiest way is [circup](https://github.com/adafruit/circup), which resolves
dependencies for you:

```bash
pip install circup
circup install adafruit_ssd1306 asyncio
```

To do it by hand instead, download the [CircuitPython Library Bundle](https://circuitpython.org/libraries)
matching your CircuitPython version and copy these into `CIRCUITPY/lib/`:

| Library | Needed by | Why |
|---|---|---|
| `adafruit_ssd1306` | `oled.py` | OLED display driver |
| `adafruit_framebuf` | `adafruit_ssd1306` | pixel buffer it draws into |
| `adafruit_bus_device` | `adafruit_ssd1306` | I2C transport |
| `asyncio` | `code.py`, `sound/synth.py` | main loop + recording playback |
| `adafruit_ticks` | `asyncio` | timing backend |

Everything else the firmware imports — `board`, `digitalio`, `analogio`,
`busio`, `keypad`, `synthio`, `audiobusio`, `audiomixer`, `json`, `time` — is
built into CircuitPython and needs no installation.

> **Note:** `asyncio` is not part of the CircuitPython core, even though it
> looks like a standard module. It must be installed like any other library.
