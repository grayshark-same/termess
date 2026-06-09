import asyncio
import websockets
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
KEYS_FILE = BASE_DIR / "server_keys.json"
QUEUE_FILE = BASE_DIR / "server_queue.json"

clients = {}  # username -> ws

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

pub_keys = load_json(KEYS_FILE)
queue = load_json(QUEUE_FILE)

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
        save_json(KEYS_FILE, pub_keys)
        clients[username] = ws
        print(f"{username} connected")
        for queued in queue.pop(username, []):
            await ws.send(json.dumps(queued))
        if username in queue:
            save_json(QUEUE_FILE, queue)

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
                    try:
                        await clients[to].send(raw)
                    except websockets.exceptions.ConnectionClosed:
                        queue.setdefault(to, []).append(msg)
                        save_json(QUEUE_FILE, queue)
                else:
                    queue.setdefault(to, []).append(msg)
                    save_json(QUEUE_FILE, queue)
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
