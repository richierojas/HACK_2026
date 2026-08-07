import serial
import json
import asyncio
import websockets

SERIAL_PORT = "/dev/cu.usbmodem1301"
BAUD_RATE = 115200
WEBSOCKET_URI = "ws://localhost:8765"


async def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

    print("Connected to Pico:", SERIAL_PORT)

    async with websockets.connect(WEBSOCKET_URI) as ws:
        print("Connected to WebSocket server")

        while True:
            line = ser.readline().decode("utf-8").strip()

            if line:
                print("Pico:", line)

                if "pressed on pin" in line:
                    button_name = line.split("  pressed")[0]

                    message = {
                        "type": "button",
                        "value": button_name
                    }

                    await ws.send(json.dumps(message))
                    print("Sent:", message)


asyncio.run(main())
