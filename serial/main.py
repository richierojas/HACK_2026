import buttons
import oled
import time
import oled
import menu
import joystick
import slider
import matrix_keypad
import json

last_move = 0
last_volume = None
last_instrument = None

oled.init()

while True:

    # Update volume from slider
    current_volume = slider.percent()

    if last_volume is None or abs(current_volume - last_volume) >= 2:
        print(json.dumps({"type": "volume", "value": current_volume}))
        last_volume = current_volume

    menu.volume = current_volume
    menu.draw()
    # Draw menu

    now = time.monotonic()

    # Navigate menu
    if joystick.up() and now - last_move > 0.20:
        menu.move_up()
        last_move = now

    elif joystick.down() and now - last_move > 0.20:
        menu.move_down()
        last_move = now

# Use for volume control with joystick

    #elif joystick.left() and now - last_move > 0.05:
       # menu.volume_down()
        #last_move = now

    #elif joystick.right() and now - last_move > 0.05:
       # menu.volume_up()
        #last_move = now

    # Select instrument
    if joystick.pressed():

        print("Selected:", menu.current())
        print("Volume:", menu.volume.value)

        while joystick.pressed():
            pass

        time.sleep(0.1)

    events = buttons.update()

    for event in events:
        print(event)

    current_instrument = menu.current()

    if last_instrument is None or current_instrument != last_instrument:
        print(json.dumps({"type": "instrument", "value": current_instrument}))
        last_instrument = current_instrument

    events = matrix_keypad.update()

    for event in events:
        if event[0] == "pressed":
            print("PRESSED:", event[1])

        elif event[0] == "released":
            print(
                "RELEASED:",
                event[1],
                "HELD:",
                round(event[2], 2),
                "seconds"
            )

    time.sleep(0.02)