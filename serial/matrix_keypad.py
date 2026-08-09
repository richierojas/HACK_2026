import time
import board
import keypad

row_pins = (
    board.GP9,
    board.GP8,
    board.GP7,
    board.GP6
)

column_pins = (
    board.GP5,
    board.GP4,
    board.GP3
)

matrix = keypad.KeyMatrix(
    row_pins=row_pins,
    column_pins=column_pins
)

KEYS = "123456789*0#"

press_start = {}


def update():
    events = []

    while True:
        event = matrix.events.get()

        if event is None:
            break

        key = KEYS[event.key_number]

        if event.pressed:
            press_start[key] = time.monotonic()
            events.append(("pressed", key))

        else:
            start = press_start.pop(key, time.monotonic())
            duration = time.monotonic() - start

            events.append(
                ("released", key, duration)
            )

    return events
