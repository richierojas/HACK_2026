import time
import json
import board
from digitalio import DigitalInOut, Direction, Pull

button_pins = [
    ("Button 1", board.GP10),
    ("Button 2", board.GP11),
    ("Button 3", board.GP12),
    ("Button 4", board.GP13),
    ("Button 5", board.GP21),
    ("Button 6", board.GP20),
    ("Button 7", board.GP19),
    ("Button 8", board.GP18),
]

buttons = []

for name, pin in button_pins:
    btn = DigitalInOut(pin)
    btn.direction = Direction.INPUT
    btn.pull = Pull.UP

    buttons.append({
        "name": name,
        "button-number": int(name.split()[1]), #get number from name "Button <number>"
        "pin": btn,
        "last": False,
        "start": 0
    })


def update():

    events = []

    now = time.monotonic()

    for button in buttons:

        pressed = not button["pin"].value

        # Just pressed
        if pressed and not button["last"]:
            button["start"] = now
            events.append(json.dumps({"type": "button-pressed", "value": {"button": button["button-number"]}}))

        # Just released
        elif not pressed and button["last"]:
            duration = now - button["start"]
            events.append(json.dumps({"type": "button-released", "value": {"button": button["button-number"], "duration": duration}}))

        button["last"] = pressed

    return events
