import asyncio
import json
import sys
import serial
import serial.tools.list_ports
import websockets

#Set this to force a specific port. Left as None the bridge finds the Pico
#itself, which matters because the port name changes between machines and
#sometimes just from replugging - it has been usbmodem1301 and usbmodem1101 on
#this setup alone.
SERIAL_PORT = None
BAUD_RATE = 115200
WEBSOCKET_URI = "ws://127.0.0.1:8765"


def find_pico():
    """Return the serial port the Pico is on, or None if it cannot be found."""
    candidates = []
    for port in serial.tools.list_ports.comports():
        text = f"{port.device} {port.description} {port.hwid}".lower()
        #Raspberry Pi vendor id, or the usbmodem naming macOS gives CircuitPython
        if "2e8a" in text or "circuitpython" in text or "pico" in text:
            candidates.append(port.device)
        elif "usbmodem" in text:
            candidates.append(port.device)

    if not candidates:
        return None

    #Prefer /dev/cu.* over /dev/tty.* on macOS: opening tty.* blocks waiting for
    #carrier detect and will just hang.
    for device in candidates:
        if "cu." in device:
            return device
    return candidates[0]


#Seconds to wait before trying the websocket again after it drops.
RECONNECT_DELAY = 2

#Only these reach the website. Anything else the Pico prints - debug lines,
#recording status, tracebacks - is ignored rather than forwarded as garbage.
FORWARDED = {"button-pressed", "button-released", "volume", "instrument"}


def valid(message):
    """True if this is an event the website understands."""
    if not isinstance(message, dict):
        return False
    event_type = message.get("type")
    if event_type not in FORWARDED:
        return False
    try:
        if event_type in {"button-pressed", "button-released"}:
            return isinstance(message.get("value"), dict)
        if event_type == "volume":
            int(message.get("value"))
            return True
        if event_type == "instrument":
            return isinstance(message.get("value"), str)
    except (TypeError, ValueError):
        return False
    return False


async def pump(ser, ws):
    """
    Forward Pico events to the websocket until it drops.

    Returns instead of raising when the connection goes, so main() can just
    reconnect. Serial errors are survivable too - the Pico briefly drops its
    USB serial every time it auto-reloads.
    """
    while True:
        try:
            line = ser.readline().decode("utf-8", errors="replace").strip()
        except Exception as exc:
            print("Serial read error:", exc)
            await asyncio.sleep(0.1)
            continue

        #Give the event loop a turn - ser.readline() blocks up to its timeout
        await asyncio.sleep(0)

        if not line:
            continue

        print("Pico:", line)

        try:
            message = json.loads(line)
        except (json.JSONDecodeError, TypeError, ValueError):
            continue

        if not valid(message):
            continue

        try:
            await ws.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            return
        print("Sent to WebSocket:", message)


async def main():
    port = SERIAL_PORT or find_pico()

    if port is None:
        print("No Pico found. Plug it in, or set SERIAL_PORT at the top of this file.")
        print("Ports seen right now:")
        for p in serial.tools.list_ports.comports():
            print("   ", p.device, "-", p.description)
        sys.exit(1)

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
    except serial.SerialException as error:
        print(f"Could not open {port}: {error}")
        print("If a serial monitor is open on that port, close it first - only one")
        print("program can hold the port at a time.")
        sys.exit(1)

    print("Connected to Pico:", port)

    #Reconnect forever. A dropped websocket used to kill the bridge outright,
    #because ws.send() sat outside the try/except - one browser tab closing at
    #the wrong moment was enough to take the whole link down mid-demo.
    while True:
        try:
            async with websockets.connect(WEBSOCKET_URI) as ws:
                print("Connected to WebSocket server")
                await pump(ser, ws)
                print("WebSocket closed")
        except (OSError, websockets.exceptions.WebSocketException) as error:
            print(f"WebSocket unavailable ({error}) - is web/server/server.py running?")

        print(f"Retrying in {RECONNECT_DELAY}s...")
        await asyncio.sleep(RECONNECT_DELAY)


#Guard so this file can be imported (for find_pico, or a test) without the
#bridge starting up and grabbing the serial port.
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBridge stopped")
