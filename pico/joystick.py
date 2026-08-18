import board
import analogio
import digitalio

# Analog axes. Note these are the ELECTRICAL axes of the joystick module, which
# are NOT the directions you push - see the rotation note below.
vx = analogio.AnalogIn(board.GP27)
vy = analogio.AnalogIn(board.GP26)

# Pushbutton
sw = digitalio.DigitalInOut(board.GP22)
sw.direction = digitalio.Direction.INPUT
sw.pull = digitalio.Pull.UP

u16 = 65535
X_CENTER = u16//2
Y_CENTER = u16//2

# The joystick is mounted rotated 90 degrees in the case, so pushing it does not
# move the axis you would expect:
#     push UP    -> X axis (GP27) goes LOW
#     push DOWN  -> X axis (GP27) goes HIGH
#     push RIGHT -> Y axis (GP26) goes LOW
#     push LEFT  -> Y axis (GP26) goes HIGH
# Everything below reports the PHYSICAL direction, so nothing that calls this
# module has to know about the rotation. If the case is ever rebuilt with the
# joystick straight, swap vx and vy in these four functions and nowhere else.

# How far off centre counts as a deliberate push. Set from a calibration sweep -
# if a direction never triggers, or triggers while centred, these are wrong.
DEFLECTED_LOW = 12000
DEFLECTED_HIGH = 53000


def x():
    return vx.value


def y():
    return vy.value


# Returns a number from [-1, 1]. +1 is fully up, -1 is fully down.
def fraction_y():
    return (X_CENTER - vx.value) / X_CENTER


# Returns a number from [-1, 1]. +1 is fully right, -1 is fully left.
def fraction_x():
    return (Y_CENTER - vy.value) / Y_CENTER


def up():
    return vx.value < DEFLECTED_LOW


def down():
    return vx.value > DEFLECTED_HIGH


def right():
    return vy.value < DEFLECTED_LOW


def left():
    return vy.value > DEFLECTED_HIGH


def pressed():
    return not sw.value
