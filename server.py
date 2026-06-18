import asyncio
import websockets
import json
import base64
from pathlib import Path
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

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

pub_keys = load_json(KEYS_FILE)   # username -> encryption pub_key
verify_keys = load_json(BASE_DIR / "server_verify_keys.json")  # username -> verify_key
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
        if "verify_key" in msg and "signature" in msg:
            incoming_vk = msg["verify_key"]
            if username in verify_keys and verify_keys[username] != incoming_vk:
                await ws.send(json.dumps({"error": "key mismatch — wrong identity"}))
                return
            try:
                vk = VerifyKey(base64.b64decode(incoming_vk))
                vk.verify(username.encode(), base64.b64decode(msg["signature"]))
            except BadSignatureError:
                await ws.send(json.dumps({"error": "invalid signature"}))
                return
            if username not in verify_keys:
                verify_keys[username] = incoming_vk
                save_json(BASE_DIR / "server_verify_keys.json", verify_keys)
        pub_keys[username] = msg["pub_key"]
        save_json(KEYS_FILE, pub_keys)
        clients[username] = ws
        print(f"{username} connected")

        try:
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
                elif action == "get_notifications":
                    messages = queue.get(username, [])
                    count = {}
                    for m in messages:
                        f = m.get("from")
                        count[f] = count.get(f, 0) + 1
                    await ws.send(json.dumps(count))
                elif action == "ready":
                    for queued in queue.pop(username, []):
                        await ws.send(json.dumps(queued))
                    save_json(QUEUE_FILE, queue)
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
        except websockets.exceptions.ConnectionClosedError:
            pass
    finally:
        if username and username in clients:
            del clients[username]
            print(f"{username} disconnected")

async def main(port=2727):
    async with websockets.serve(handler, "0.0.0.0", port):
        print("server started")
        await asyncio.Future()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 2727
    asyncio.run(main(port))
 
 