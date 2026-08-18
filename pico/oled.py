import board
import busio
import adafruit_ssd1306

from font5x7 import FONT

WIDTH = 128
HEIGHT = 64

display = None

# 400kHz keeps a full screen refresh down to ~26ms; at the 100kHz default it is
# ~106ms, which is longer than the audio buffer and drops out every redraw.
# Fast mode needs decent pull-ups though, so fall back if the display does not
# answer - a slow display beats no display.
I2C_SPEEDS = (400000, 100000)


def init():
    """
    Bring up the display. If it cannot be found the instrument carries on
    WITHOUT a screen rather than refusing to start - a loose display wire
    should not stop the thing making sound.
    """
    global display

    for frequency in I2C_SPEEDS:
        i2c = None
        try:
            i2c = busio.I2C(scl=board.GP17, sda=board.GP16, frequency=frequency)
            display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)
            clear()
            show()
            print("OLED ready at", frequency, "Hz")
            return
        except Exception as error:
            print("OLED not found at", frequency, "Hz:", error)
            if i2c is not None:
                try:
                    i2c.deinit()
                except Exception:
                    pass

    display = None
    print("OLED unavailable - running without a display")


def ready():
    return display is not None


def clear():
    if display is None:
        return
    display.fill(0)


def show():
    if display is None:
        return
    display.show()


def line(x0, y0, x1, y1):
    if display is None:
        return
    display.line(x0, y0, x1, y1, 1)


def rect(x, y, w, h):
    if display is None:
        return
    display.rect(x, y, w, h, 1)


def fill_rect(x, y, w, h, color=1):
    if display is None:
        return
    display.fill_rect(x, y, w, h, color)


def pixel(x, y, color=1):
    if display is None:
        return
    display.pixel(x, y, color)


def draw_letter(letter, x, y, color=1):
    if display is None:
        return
    if letter not in FONT:
        letter = " "
    bitmap = FONT[letter]
    for row in range(7):
        row_bits = bitmap[row]
        for col in range(5):
            if row_bits & (1 << (4 - col)):
                pixel(x + col, y + row, color)


def text(message, x, y, color=1):
    if display is None:
        return
    for letter in message:
        draw_letter(letter, x, y, color)
        x += 6
