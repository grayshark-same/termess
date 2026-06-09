import asyncio
import websockets
import json

clients = {}   # username -> ws
pub_keys = {}  # username -> pub_key
queue = {}     # username -> [messages]

async def handler(ws):
    username = None
    try:
        try:
            msg = json.loads(await ws.recv())
        except (json.JSONDecodeError, Exception):
            return
        if msg.get("action") != "register":
            return
        username = msg["from"]
        pub_keys[username] = msg["pub_key"]
        clients[username] = ws
        print(f"{username} connected")
        for queued in queue.pop(username, []):
            await ws.send(json.dumps(queued))

        async for raw in ws:
            msg = json.loads(raw)
            action = msg.get("action")
            if action == "get_key":
                target = msg["username"]
                key = pub_keys.get(target)
                if key:
                    await ws.send(json.dumps({"pub_key": key}))
                else:
                    await ws.send(json.dumps({"error": f"{target} not found"}))
            elif "to" in msg:
                to = msg["to"]
                if to in clients:
                    await clients[to].send(raw)
                else:
                    queue.setdefault(to, []).append(msg)
    finally:
        if username and username in clients:
            del clients[username]
            print(f"{username} disconnected")

async def main(port=2727):
    async with websockets.serve(handler, "0.0.0.0", port):
        print("server started")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
