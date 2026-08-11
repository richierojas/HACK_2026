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
import array
import math

import synthio
import asyncio
import audiobusio
import audiomixer

from sound.synth import Synth_Wrapper
from sound.scale import Scale
from sound.synth_presets import Synth_Presets

oled.init()

SAMPLE_RATE = 22050

LIVE_LEVEL_MAX = 0.3
RECORD_LEVEL_MAX = 0.15
VOLUME_CHANGE_THRESHOLD = 2 #percent
last_volume_percent = None
volume_mode = menu.volume_menu.items[1] #Active

octave_offset = 0

# region Instrument Presets
scale = Scale('C', 3, Scale.MAJOR)
scale_guitar = Scale('C', 2, Scale.MAJOR)
scale_bass = Scale('C', 0, Scale.MAJOR)

piano = Synth_Wrapper(scale, Synth_Presets.PIANO, sample_rate=SAMPLE_RATE)
guitar = Synth_Wrapper(scale_guitar, Synth_Presets.GUITAR, sample_rate=SAMPLE_RATE)
bass = Synth_Wrapper(scale_bass, Synth_Presets.BASS, sample_rate=SAMPLE_RATE)

instruments = { Synth_Presets.PIANO:piano, Synth_Presets.GUITAR:guitar, Synth_Presets.BASS:bass}
INSTRUMENT_NAMES = list(instruments.keys())
active_instrument = "PIANO"

voice_map = {} # name: {live:voice#, recording:voice#}
voice_index = 0
#initialize voice map
for name in INSTRUMENT_NAMES:
    instrument = instruments[name]

    live_voice = voice_index
    voice_index += 1
    #*only one recording per instrument for now
    rec_voice = voice_index
    voice_index += 1

    voice_map[name] = {"live":live_voice, "recording": rec_voice}
num_voices = voice_index
# endregion

# region Mixer setup
audio = audiobusio.I2SOut(
    bit_clock=board.GP1,
    word_select=board.GP2,
    data=board.GP0,
)
mixer = audiomixer.Mixer(
    voice_count=num_voices,
    sample_rate=SAMPLE_RATE,
    channel_count=1,
    bits_per_sample=16,
    samples_signed=True,
)
audio.play(mixer)

for name, wrapper in instruments.items():
    voices = voice_map[name]
    mixer.voice[voices["live"]].play(wrapper.synth)
    mixer.voice[voices["live"]].level = LIVE_LEVEL_MAX
    mixer.voice[voices["recording"]].play(wrapper.recording_synths[0])
    mixer.voice[voices["recording"]].level = RECORD_LEVEL_MAX
# endregion

#* Immediately changes volume to current slider upon change
def set_volume_mode(mode):
    """
    Switches volume between active, global, playbacks.
    """
    global volume_mode
    volume_mode = mode
    apply_volume(last_volume_percent)

def apply_volume(percent):
    fraction = percent / 100

    if volume_mode == "ACTIVE":
        voices = voice_map[active_instrument]
        mixer.voice[voices["live"]].level = fraction * LIVE_LEVEL_MAX

    elif volume_mode == "GLOBAL":
        for name in INSTRUMENT_NAMES:
            voices = voice_map[name]
            mixer.voice[voices["live"]].level = fraction * LIVE_LEVEL_MAX

    elif volume_mode == "PLAYBACK":
        for name in INSTRUMENT_NAMES:
            voices = voice_map[name]
            mixer.voice[voices["recording"]].level = fraction * RECORD_LEVEL_MAX

def get_active_instrument():
    return instruments[active_instrument]

def set_active_instrument(name):
    global active_instrument
    instrument = get_active_instrument()
    if instrument.is_recording:
        instrument.end_record()
        instrument.start_playback()
    active_instrument = name

# Menu selection
def select_and_handle():
    select_tuple = menu.select() #None if submenu, (menu, item_string) if item 
    print("Selected:", menu.current())
    if select_tuple is None:
        return
    item_menu = select_tuple[0]
    item = select_tuple[1]
    if(item_menu is menu.instruments_menu):
        set_active_instrument(item)
    elif(item_menu is menu.record_menu):
        if item == menu.record_menu.items[0]: #record/stop record
            toggle_record()
        elif item == menu.record_menu.items[1]: #play/pause record
            toggle_playback(active_instrument)
        elif item == menu.record_menu.items[2]: # pause all
            pause_all_playback()
        elif item == menu.record_menu.items[3]: #play all
            play_all_playback()
    elif(item_menu is menu.volume_menu):
        set_volume_mode(item)

# region Record/playback functions
def toggle_record():
    instrument = get_active_instrument()
    if not instrument.is_recording:
        instrument.record()
    else:
        instrument.end_record()
        instrument.start_playback()

def pause_all_playback():
    for instrument in INSTRUMENT_NAMES:
        pause_playback(instrument)

def play_all_playback():
    for instrument in INSTRUMENT_NAMES:
        play_playback(instrument)

#toggles pause/resume for individual instrument
def toggle_playback(instrument_name):
    instrument = instruments[instrument_name]
    if instrument.is_playback:
        pause_playback(instrument_name)
    else:
        play_playback(instrument_name)

def play_playback(instrument_name):
    instrument = instruments[instrument_name]
    instrument.start_playback() #resumes if already

def pause_playback(instrument_name):
    instrument = instruments[instrument_name]
    instrument.pause_playback()
# endregion

# region Handlers for joystick, button, and keypad
#Bottom three keypad kets are [(quick=up, long=back), select, move]
def on_keypad_pressed(key : str):
    if key == '*':
        pass #see keypad_released, short press moves up, long press moves back 
    elif key == '#':
        menu.move_down()
    elif key == '0':
        select_and_handle()
    else:
        try:
            keynumber = int(key)
            menu.move_to_selection(keynumber)
            select_and_handle()
        except ValueError:
            pass
    menu.draw()

def on_keypad_released(key : str, duration):
    if key == '*':
        if duration < 0.5:
            menu.move_up()
        else:
            menu.back()
    menu.draw()

def on_button_pressed(button_number : int):
    get_active_instrument().press(button_number, octave_offset=octave_offset)
    #instruments["PIANO"].press(button_number)
    print("Mixer playing: ", mixer.voice[0].playing)

def on_button_released(button_number : int, duration):
    get_active_instrument().release(button_number, octave_offset=octave_offset)

def on_joystick_pressed():
    toggle_record()

def on_joystick_up(joystick : joystick):
    amount = joystick.fraction_y() #0 to 1

def on_joystick_down(joystick : joystick):
    amount = abs(joystick.fraction_y()) #0 to 1

def on_joystick_right(joystick : joystick):
    global octave_offset
    #octave_offset = 1
    amount = joystick.fraction_x() #0 to 1

def on_joystick_left(joystick : joystick):
    global octave_offset
    #octave_offset = -1
    amount = abs(joystick.fraction_x()) #0 to 1
# endregion

def test_synth():
    samples_per_cycle = int(SAMPLE_RATE / 440)
    samples = array.array("h", [int(math.sin(2*math.pi*i/samples_per_cycle)*16000) for i in range(samples_per_cycle)])
    test_note = synthio.Note(frequency=440, waveform=memoryview(samples))
    piano.synth.press(test_note)

async def main_loop():
    global last_volume_percent

    menu.draw()
    last_move = 0
    while True:
        #only use slider for volume for now
        volume_percent = slider.percent()
        if last_volume_percent is None or abs(volume_percent - last_volume_percent) >= VOLUME_CHANGE_THRESHOLD:
            apply_volume(volume_percent)
            last_volume_percent = volume_percent
            menu.volume.value = volume_percent
            menu.draw()

        now = time.monotonic()

        # HANDLE JOYSTICK
        if joystick.up() and now - last_move > 0.20:
            on_joystick_up(joystick)
            last_move = now
        elif joystick.down() and now - last_move > 0.20:
            on_joystick_down(joystick)
            last_move = now
        elif joystick.right() and now - last_move > 0.20:
            on_joystick_right(joystick)
            last_move = now
        elif joystick.left() and now - last_move > 0.20:
            on_joystick_left(joystick)
            last_move = now
        if joystick.pressed():
            on_joystick_pressed()

            while joystick.pressed():
                await asyncio.sleep(0) #pass but async

            await asyncio.sleep(0.1)

        #HANDLE BUTTONS
        events = buttons.update()
        for eventraw in events:
            event = json.loads(eventraw)
            if event["type"] == "button-pressed":
                button_number = event["value"]["button"]
                print("PLAY", eventraw)
                on_button_pressed(button_number)
            elif event["type"] == "button-released":
                duration = event["value"]["duration"]
                button_number = event["value"]["button"]
                print("STOP", eventraw, "Held:", round(duration, 2))
                on_button_released(button_number, duration)

        #HANDLE KEYPAD
        events = matrix_keypad.update()
        for eventraw in events:
            event = json.loads(eventraw)
            if event["type"] == "keypad-pressed":
                key = event["value"]["key"]
                print("PRESSED", eventraw)
                on_keypad_pressed(key)
            elif event["type"] == "keypad-released":
                key = event["value"]["key"]
                duration = event["value"]["duration"]
                print("RELEASED:", eventraw)
                on_keypad_released(key, duration)

        await asyncio.sleep(0.02)

asyncio.run(main_loop())
