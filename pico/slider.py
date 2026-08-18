import board
import analogio

pot = analogio.AnalogIn(board.GP28)

#Measured with a calibration sweep, not assumed. This slider only swings
#between about 3120 and 50684 raw ADC counts - nowhere near the full 0..65535 -
#so the old 500/63000 guess mapped the whole physical travel onto roughly
#4%..80% of volume. It could never reach silent or full.
#The values below sit just INSIDE the measured ends so both extremes saturate.
#Re-run the calibration sweep and update these if the pot is ever replaced.
MIN = 3300
MAX = 50000

#The joystick shares the ADC with this slider, and the converter is multiplexed
#between them. Switching channels leaves the sample-and-hold holding charge from
#the previous pin, so the first few conversions after a switch read wrong -
#moving the joystick was swinging the volume by ~24% of its range on its own.
SETTLING_READS = 4      #thrown away, purely to let the mux settle
MEDIAN_READS = 11       #kept, median taken


def raw():
    for _ in range(SETTLING_READS):
        pot.value

    samples = sorted([pot.value for _ in range(MEDIAN_READS)])

    #Median, not mean. A single glitched conversion drags an average off far
    #enough to swing the volume; the median just ignores it.
    return samples[len(samples) // 2]


#Exponential smoothing on top of the median. The median kills single bad
#conversions; this rides out slower wander, like hum picked up on a
#high-impedance input. Lower = smoother but laggier. At one poll every 0.12s,
#0.25 settles in roughly half a second.
SMOOTHING = 0.25
_smoothed = None


def percent():
    global _smoothed

    value = raw()

    if value < MIN:
        value = MIN

    if value > MAX:
        value = MAX

    reading = int((value - MIN) * 100 / (MAX - MIN))

    if _smoothed is None:
        _smoothed = reading
    else:
        _smoothed += (reading - _smoothed) * SMOOTHING

    return int(_smoothed)