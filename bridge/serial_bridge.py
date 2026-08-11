import asyncio
import json
import serial
import websockets

SERIAL_PORT = "/dev/cu.usbmodem1301"
BAUD_RATE = 115200
WEBSOCKET_URI = "ws://127.0.0.1:8765"


async def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    print("Connected to Pico:", SERIAL_PORT)

    async with websockets.connect(WEBSOCKET_URI) as ws:
        print("Connected to WebSocket server")

        while True:
            try:
                line = ser.readline().decode("utf-8", errors="replace").strip()
            except Exception as exc:
                print("Serial read error:", exc)
                await asyncio.sleep(0.1)
                continue

            if not line:
                continue

            print("Pico:", line)

            try:
                message = json.loads(line)
            except (json.JSONDecodeError, TypeError, ValueError):
                continue

            if not isinstance(message, dict):
                continue

            event_type = message.get("type")
            if event_type not in {"button-pressed", "button-released", "volume", "instrument"}:
                continue

            try:
                if event_type in {"button-pressed", "button-released"}:
                    if not isinstance(message.get("value"), dict):
                        continue
                elif event_type == "volume":
                    int(message.get("value"))
                elif event_type == "instrument":
                    if not isinstance(message.get("value"), str):
                        continue
            except (TypeError, ValueError):
                continue

            await ws.send(json.dumps(message))
            print("Sent to WebSocket:", message)


asyncio.run(main())