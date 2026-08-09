import buttons
import oled
import board
import time
import oled
import menu
import joystick
import slider
import matrix_keypad

import synthio
import asyncio
import audiobusio
import audiomixer

from sound.synth import Synth_Wrapper
from sound.scale import Scale
from sound.synth_presets import Synth_Presets

last_move = 0

scale = Scale('C', 4, Scale.MAJOR)
sample_rate = 22050
synth_wrapper = Synth_Wrapper(scale)
audio = audiobusio.I2SOut(
    bit_clock=board.GP1,
    word_select=board.GP2,
    data=board.GP0,
)

num_voices = 2

mixer = audiomixer.Mixer(
    voice_count=1,
    sample_rate=sample_rate,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True)

preset = Synth_Presets()
synth = synthio.Synthesizer(sample_rate=sample_rate)
note = synthio.Note(frequency=synthio.midi_to_hz(scale.get_midi_note(1)), envelope=preset.envelope, waveform=preset.waveform)

mixer.voice[0].play(synth)
mixer.voice[0].level = 0.8

while True:

    now = time.monotonic()

    # Navigate menu
    if joystick.up() and now - last_move > 0.20:
        menu.move_up()
        last_move = now

    elif joystick.down() and now - last_move > 0.20:
        menu.move_down()
        last_move = now

    # Select instrument
    if joystick.pressed():

        print("Selected:", menu.current())
        print("Volume:", menu.volume.value)

        while joystick.pressed():
            pass

        time.sleep(0.1)

    events = buttons.update()

    for event in events:

        if event[0] == "pressed":
            print("PLAY", event[1])
            synth.press(note)

            # synth.note_on(...)

        elif event[0] == "released":
            print("STOP", event[1], "Held:", round(event[2], 2))

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
