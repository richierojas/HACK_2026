import buttons
import oled
import board
import time
import oled
import menu
import joystick
import slider
import matrix_keypad
import json

import synthio
import asyncio
import audiobusio
import audiomixer

from sound.synth import Synth_Wrapper
from sound.scale import Scale
from sound.synth_presets import Synth_Presets

scale = Scale('C', 3, Scale.MINOR)
sample_rate = 22050
synth_wrapper = Synth_Wrapper(scale)
audio = audiobusio.I2SOut(
    bit_clock=board.GP1,
    word_select=board.GP2,
    data=board.GP0,
)

num_voices = 2

mixer = audiomixer.Mixer(
    voice_count=2,
    sample_rate=sample_rate,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True)

preset = Synth_Presets()
synth = synthio.Synthesizer(sample_rate=sample_rate)
note = synthio.Note(frequency=synthio.midi_to_hz(scale.get_midi_note(1)), envelope=preset.envelope, waveform=preset.waveform)

audio.play(mixer)
mixer.voice[0].play(synth_wrapper.synth)
mixer.voice[0].level = 0.3
mixer.voice[1].play(synth_wrapper.recording_synths[0])
mixer.voice[1].level = 0.075
#mixer.voice[1].play(synth)



async def main_loop():
    last_move = 0
    is_recording = False
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
            if (not is_recording):
                synth_wrapper.record()
                is_recording=True
            else:
                is_recording=False
                synth_wrapper.end_record()
                synth_wrapper.start_playback()

            print("Selected:", menu.current())
            print("Volume:", menu.volume)


            while joystick.pressed():
                pass

            time.sleep(0.1)

        events = buttons.update()

        for eventraw in events:
            event = json.loads(eventraw)

            if event["type"] == "button-pressed":
                print("PLAY", eventraw)
                note = synth_wrapper.press(event["value"]["button"])
                print("Mixer playing: ", mixer.voice[0].playing)

                # synth.note_on(...)

            elif event["type"] == "button-released":
                synth_wrapper.release(event["value"]["button"])
                print("STOP", eventraw, "Held:", round(event["value"]["duration"], 2))

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

        await asyncio.sleep(0.02)

asyncio.run(main_loop())
