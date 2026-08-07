import asyncio
import websockets
import json

async def test():
    async with websockets.connect("ws://localhost:8765") as ws:
        message = {
            "type": "button",
            "value": "Button 1"
        }

        await ws.send(json.dumps(message))
        print("Sent:", message)

        await asyncio.sleep(1)

asyncio.run(test())
