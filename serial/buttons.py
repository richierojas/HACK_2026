import time
import board
from digitalio import DigitalInOut, Direction, Pull

# list of tuples to hold the name of buttons and GPIO pin its connected to
button_pins = [
    ("Button 1", "GP10", board.GP10),
    ("Button 2", "GP11", board.GP11),
    ("Button 3", "GP12", board.GP12),
    ("Button 4", "GP13", board.GP13),
    ("Button 5", "GP21", board.GP21),
    ("Button 6", "GP20", board.GP20),
    ("Button 7", "GP19", board.GP19),
    ("Button 8", "GP18", board.GP18),
]

print("Buttons module loaded")

# list to hold buttons
buttons = []

# loop though each element of button_pins to create it and add it to buttons list
for name, gpio_pin, pin in button_pins:
    btn = DigitalInOut(pin)
    btn.direction = Direction.INPUT
    btn.pull = Pull.UP
    buttons.append((name, gpio_pin, btn))


while True:
    # loop though each button in the list
    for name, gpio_pin, btn in (buttons):
        # btn.value returns volatage, 3.3v=True, 0v=False
        # if not False = True mean btn pressed
        if not btn.value:
            print(f"{name}  pressed on pin {gpio_pin}")

    time.sleep(0.05)
