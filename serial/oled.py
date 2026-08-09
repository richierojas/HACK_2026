import board
import busio
import adafruit_ssd1306

from font5x7 import FONT

WIDTH = 128
HEIGHT = 64

display = None


def init():
    global display

    i2c = busio.I2C(
        scl=board.GP17,
        sda=board.GP16
    )

    display = adafruit_ssd1306.SSD1306_I2C(
        WIDTH,
        HEIGHT,
        i2c,
        addr=0x3C
    )

    clear()
    show()


def clear():
    display.fill(0)


def show():
    display.show()


def line(x0, y0, x1, y1):
    display.line(x0, y0, x1, y1, 1)


def rect(x, y, w, h):
    display.rect(x, y, w, h, 1)


def fill_rect(x, y, w, h, color=1):
    display.fill_rect(x, y, w, h, color)

def pixel(x, y, color=1):
    display.pixel(x, y, color)

def draw_letter(letter, x, y, color=1):
    if letter not in FONT:
        letter = " "
    bitmap = FONT[letter]
    for row in range(7):
        row_bits = bitmap[row]
        for col in range(5):
            if row_bits & (1 << (4 - col)):
                pixel(x + col, y + row, color)

def text(message, x, y, color=1):
    for letter in message:
        draw_letter(letter, x, y, color)
        x += 6