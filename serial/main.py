# from dac import DAC
# from synth import Synth
from buttons import *
import oled

# dac = DAC()

# synth = Synth(dac)

# synth.note_on(440)  # Play A4 note (440 Hz)

# Menu options
oled.init()

oled.clear()

oled.text("HELLO", 10, 5)

oled.text("> PIANO", 10, 20)
oled.text("  BASS", 10, 32)
oled.text("  SYNTH", 10, 44)

oled.show()

