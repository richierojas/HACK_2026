import buttons 
import oled 
import time
import oled
import menu
import joystick
import slider

last_move = 0

oled.init()

while True:

    # Update volume from slider
    menu.volume = slider.percent()

    # Draw menu
    menu.draw()

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
        print("Volume:", menu.volume)

        while joystick.pressed():
            pass

        time.sleep(0.1)
        
    events = buttons.update()

    for event in events:

        if event[0] == "pressed":
            print("PLAY", event[1])

        elif event[0] == "released":
            print("STOP", event[1], "Held:", round(event[2], 2))



    

    time.sleep(0.02)
