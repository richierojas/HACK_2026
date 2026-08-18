#!/bin/bash
# Copy pico/ onto the CIRCUITPY drive and prove the files really landed.
#
# Why this exists: a plain `cp` to CIRCUITPY is not reliable on macOS. The OS
# caches FAT blocks while CircuitPython independently remounts its own
# filesystem every time it auto-reloads. A stale cached block can get flushed
# back over a file you just wrote, silently reverting it -- and because the
# same stale cache serves your next read, `diff` reports success on a file that
# is actually old on the board.
#
# The fix is to unmount and remount between writing and verifying, which forces
# macOS to drop its cache and read the real contents off the device.
#
# Usage:  ./deploy.sh

set -u

REPO="$(cd "$(dirname "$0")" && pwd)"
SRC="$REPO/pico"
DST="/Volumes/CIRCUITPY"

FILES=(
    buttons.py code.py font5x7.py joystick.py
    menu.py oled.py slider.py
    sound/__init__.py sound/note.py sound/scale.py
    sound/synth.py sound/synth_presets.py
    sound/sound_files/bassc3.raw
    sound/sound_files/guitarc3.raw
    sound/sound_files/pianoc1.raw
)

if [ ! -d "$DST" ]; then
    echo "CIRCUITPY is not mounted. Plug in the Pico and try again."
    exit 1
fi

NODE=$(diskutil info "$DST" 2>/dev/null | awk -F: '/Device Node/{gsub(/ /,"",$2); print $2}')
if [ -z "$NODE" ]; then
    echo "Could not find the CIRCUITPY device node."
    exit 1
fi
echo "CIRCUITPY at $NODE"

echo
echo "== copying =="
for f in "${FILES[@]}"; do
    mkdir -p "$DST/$(dirname "$f")"
    cp "$SRC/$f" "$DST/$f" || { echo "  FAILED to copy $f"; exit 1; }
    echo "  sent  $f"
done

sync
sleep 1

echo
echo "== dropping the OS cache so verification is honest =="
diskutil unmount "$DST" >/dev/null 2>&1 || { echo "  could not unmount (a file or Finder window may be open on it)"; exit 1; }
sleep 2
diskutil mount "$NODE" >/dev/null 2>&1 || { echo "  could not remount $NODE"; exit 1; }
sleep 2

echo
echo "== verifying against the real device contents =="
FAILED=()
for f in "${FILES[@]}"; do
    case "$f" in
        *.raw) cmp -s "$SRC/$f" "$DST/$f" ;;
            *) diff -qwB "$SRC/$f" "$DST/$f" >/dev/null 2>&1 ;;
    esac

    if [ $? -eq 0 ]; then
        echo "  ok    $f"
    else
        echo "  BAD   $f"
        FAILED+=("$f")
    fi
done

echo
if [ ${#FAILED[@]} -eq 0 ]; then
    echo "ALL ${#FILES[@]} FILES VERIFIED ON DEVICE"
    exit 0
fi

echo "THESE DID NOT LAND: ${FAILED[*]}"
echo "Re-run ./deploy.sh. If a file keeps failing, close any editor tab or"
echo "Finder window open on CIRCUITPY and try once more."
exit 1
