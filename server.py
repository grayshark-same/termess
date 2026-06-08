import asyncio
import websockets
import json

clients = {}  # username -> websocket

async def handler(ws):
    msg = json.loads(await ws.recv())
    username = msg["username"]
    clients[username] = ws
    print(f"{username} connected")
    
    try:
        async for raw in ws:
            msg = json.loads(raw)
            to = msg.get("to")
            if to in clients:
                await clients[to].send(raw)
            else:
                await ws.send(json.dumps({"error": f"{to} not online"}))
    finally:
        del clients[username]
        print(f"{username} disconnected")

async def main(port=2727):
    async with websockets.serve(handler, "0.0.0.0", port):
        print("server started")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())