# from dac import DAC
# from synth import Synth
from buttons import *
from oled import *
import time
import oled
import menu
import joystick

last_move = 0

while True:

    menu.draw()

    now = time.monotonic()

    if joystick.up() and now - last_move > 0.20:
        menu.move_up()
        last_move = now

    elif joystick.down() and now - last_move > 0.20:
        menu.move_down()
        last_move = now

    elif joystick.left() and now - last_move > 0.05:
        menu.volume_down()
        last_move = now

    elif joystick.right() and now - last_move > 0.05:
        menu.volume_up()
        last_move = now

    # SELECT
    if joystick.pressed():

        print("Selected:", menu.current())
        print("Volume:", menu.volume)

        while joystick.pressed():
            pass

        time.sleep(0.1)

    time.sleep(0.02)