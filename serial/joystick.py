import board
import analogio
import digitalio

# Analog axes
vx = analogio.AnalogIn(board.GP27)
vy = analogio.AnalogIn(board.GP26)

# Pushbutton
sw = digitalio.DigitalInOut(board.GP22)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP


def x():
    return vx.value


def y():
    return vy.value


def up():
    return vy.value < 12000


def down():
    return vy.value > 53000


def left():
    return vx.value < 12000


def right():
    return vx.value > 53000


def pressed():
    return not sw.value