import board
import analogio

pot = analogio.AnalogIn(board.GP28)

MIN = 500      
MAX = 63000

def raw():
    total = 0

    for _ in range(8):
        total += pot.value

    return total // 8


def percent():

    value = raw()

    if value < MIN:
        value = MIN

    if value > MAX:
        value = MAX

    return int((value - MIN) * 100 / (MAX - MIN))