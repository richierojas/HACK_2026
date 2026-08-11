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

u16 = 65535
X_CENTER = u16//2
Y_CENTER = u16//2
MIN_X = 0               #fully left
MAX_X = u16             #fully right
MIN_Y = 0               #fully UP
MAX_Y = u16             #fully DOWN


def x():
    return vx.value


def y():
    return vy.value

# Returns a number from [-1, 1]. If joystick is 50% up, returns 0.5, if joystick is 50% down, returns -0.5
def fraction_y():
    amount_up = (Y_CENTER - vy.value)
    return amount_up / Y_CENTER

# Returns a number from [-1, 1]. If joystick is 50% right, returns 0.5, if joystick is 50% left, returns -0.5
def fraction_x():
    amount_right = (vx.value - X_CENTER)
    return amount_right / X_CENTER

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