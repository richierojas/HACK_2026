import oled

# Instruments
MENU = [
    "PIANO",
    "BASS",
    "SYNTH",
    "ORGAN",
    "STRINGS",
    "BELL",
    "CHOIR",
    "LEAD",
    "PAD",
    "DRUMS"
]

selected = 0
volume = 75


def move_up():
    global selected

    if selected > 0:
        selected -= 1


def move_down():
    global selected

    if selected < len(MENU) - 1:
        selected += 1


def volume_up():
    global volume

    if volume < 100:
        volume += 1


def volume_down():
    global volume

    if volume > 0:
        volume -= 1


def current():
    return MENU[selected]


def draw():

    oled.clear()

    # ===== Title =====
    oled.text("ARTEMIS AUDIO", 12, 2)
    oled.line(0, 11, 127, 11)

    # Show 4 menu items
    start = max(0, selected - 1)

    if start > len(MENU) - 4:
        start = max(0, len(MENU) - 4)

    y = 16

    for i in range(start, min(start + 4, len(MENU))):

        if i == selected:

            # Highlight bar
            oled.fill_rect(0, y - 1, 128, 9, 1)

            # Inverted text
            oled.text(MENU[i], 6, y, 0)

        else:

            oled.text(MENU[i], 6, y, 1)

        y += 10

    # ===== Bottom Bar =====
    oled.line(0, 53, 127, 53)

    oled.text("VOL", 2, 56)

    # Volume outline
    oled.rect(24, 55, 70, 8)

    # Filled volume
    fill = int((68 * volume) / 100)

    if fill > 0:
        oled.fill_rect(25, 56, fill, 6)

    # Percentage
    oled.text(str(volume), 100, 56)

    oled.show()