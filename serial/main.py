from machine import Pin
from utime import sleep_ms
import sys, select

#Connect LEDs:
#   Connect to GPIO pins from left to right corresponding to array
LED_GPIO_PINS = 0

#Connect Switch:
#   'On' side to 3.3V
#    Middle to GPIO pin
#   'Off' side to GRND
SWITCH_PIN = 3
     
led = Pin(LED_GPIO_PINS, Pin.OUT)
switch = Pin(SWITCH_PIN, Pin.IN, Pin.PULL_DOWN)

server_poll = select.poll()
server_poll.register(sys.stdin, select.POLLIN)

server_light_state = True

def pin_changed(pin):
    print('{"type": "switch", "value": %d}' % pin.value())

#Send message whenever switch changes value, default trigger is when value changes
switch.irq(handler=pin_changed)

while True:
    sleep_ms(100)
    if server_poll.poll(0):
        #assume poll contains a on or off message
        server_message = sys.stdin.readline().strip()
        if(server_message == "on"):
            server_light_state = True
        elif(server_message == "off"):
            server_light_state = False
    
    if switch.value() == 1 and server_light_state:
        led.on()
    else:
        led.off()

    




