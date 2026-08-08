import buttons 
import oled 
import time
import menu
import joystick
import slider
import json

last_move = 0
last_volume = -1

oled.init()

while True:

    # Update volume from slider
    current_volume = slider.percent()

    if current_volume != last_volume:
        menu.volume = current_volume

        print(json.dumps({
            "type": "volume",
            "value": current_volume,
        }))

        last_volume = current_volume
    # Draw the menu 
    menu.draw()
    now = time.monotonic()

    # Navigate menu
    if joystick.up() and now - last_move > 0.20:
        menu.move_up()
        print(json.dumps({
            "type": "menu",
            "value": menu.current(),
        }))
        last_move = now

    elif joystick.down() and now - last_move > 0.20:
        menu.move_down()
        print(json.dumps({
            "type": "menu",
            "value": menu.current(),
        }))
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

        print(json.dumps({
            "type": "select",
            "value": menu.current(),
        }))
        while joystick.pressed():
            pass

        time.sleep(0.1)
    #Read button events
    events = buttons.update()

    for event in events:

        if event[0] == "pressed":

            print(json.dumps({
                "type": "button",
                "value": event[1],
            }))

        elif event[0] == "released":

            print(json.dumps({
                "type": "button_released",
                "value": event[1],
                "held": event[2],
            }))



    

    time.sleep(0.02)
