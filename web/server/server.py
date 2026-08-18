import asyncio
import websockets
import json
from datetime import datetime

# Store all messages
chat_logs = []
# Store all connected clients
connected_clients = set()


def print_chat_logs():
    print("\n" + "="*60)
    print("CHAT LOGS")
    print("="*60)
    if not chat_logs:
        print("No messages yet")
    else:
        for i, log in enumerate(chat_logs, 1):
            print(f"{i}. [{log['timestamp']}] {log['message']}")
    print("="*60 + "\n")


async def handle_client(websocket):
    print(f"Client connected from {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                messageDetails = json.loads(message)
            except json.JSONDecodeError:
                print(f"Ignoring malformed message: {message}")
                continue
            # .get() rather than [] - a message missing "type" or "value" used
            # to raise KeyError, which escaped the ConnectionClosed handler
            # below and killed that client's connection outright.
            if not isinstance(messageDetails, dict):
                print(f"Ignoring non-object message: {message}")
                continue

            event_type = messageDetails.get("type")
            value = messageDetails.get("value")
            if event_type is None:
                print(f"Ignoring message with no type: {message}")
                continue

            # Store in chat logs
            chat_logs.append({
                "type": event_type,
                "message": value,
                "timestamp": timestamp
            })
            print(f"Received: {message}")
            # Broadcast the message to all connected clients
            response = {
                "status": "received",
                "type": event_type,
                "value": value,
                "timestamp": timestamp
            }
            # Send to all connected clients. Iterate over a copy: a slow or
            # dead client must not stop the others from being served, and the
            # set is mutated below.
            disconnected = set()
            for client in list(connected_clients):
                try:
                    await client.send(json.dumps(response))
                except Exception:
                    # Any send failure means that client is gone - not just
                    # ConnectionClosed. Drop it and carry on serving the rest.
                    disconnected.add(client)
            # Remove disconnected clients
            for client in disconnected:
                connected_clients.discard(client)
    except websockets.exceptions.ConnectionClosed:
        print(f"Client {websocket.remote_address} disconnected")
    finally:
        connected_clients.discard(websocket)


async def main():
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
