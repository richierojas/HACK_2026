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

                try:
                    if line.startswith("PLAY "):
                        message = json.loads(line[5:])  

                        if message.get("type") == "button-pressed":
                            button_number = message["value"]["button"]

                            web_message = {
                                "type": "button",
                                "value": f"Button {button_number}"
                            }

                            await ws.send(json.dumps(web_message))
                            print("Sent to WebSocket:", web_message)

                except (json.JSONDecodeError, KeyError):
                    pass

asyncio.run(main())