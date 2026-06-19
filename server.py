import asyncio
import websockets
import json
import base64
from pathlib import Path
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import aiosqlite

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "server.db"

clients = {}  # username -> ws

async def init_db(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            pub_key TEXT NOT NULL,
            verify_key TEXT NOT NULL
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            to_ TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT NOT NULL,
            sender TEXT NOT NULL,
            to_ TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
    """)
    await db.commit()

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

        async with aiosqlite.connect(DB_PATH) as db:
            await init_db(db)

            if "verify_key" in msg and "signature" in msg:
                incoming_vk = msg["verify_key"]
                async with db.execute("SELECT verify_key FROM users WHERE username = ?", (username,)) as cur:
                    row = await cur.fetchone()
                if row and row[0] != incoming_vk:
                    await ws.send(json.dumps({"error": "key mismatch — wrong identity"}))
                    return
                try:
                    vk = VerifyKey(base64.b64decode(incoming_vk))
                    vk.verify(username.encode(), base64.b64decode(msg["signature"]))
                except BadSignatureError:
                    await ws.send(json.dumps({"error": "invalid signature"}))
                    return
                if not row:
                    await db.execute(
                        "INSERT INTO users (username, pub_key, verify_key) VALUES (?, ?, ?)",
                        (username, msg["pub_key"], incoming_vk)
                    )
                else:
                    await db.execute(
                        "UPDATE users SET pub_key = ? WHERE username = ?",
                        (msg["pub_key"], username)
                    )
                await db.commit()

            clients[username] = ws
            print(f"{username} connected")

            try:
                async for raw in ws:
                    msg = json.loads(raw)
                    action = msg.get("action")
                    if action == "get_key":
                        target = msg["username"]
                        async with db.execute("SELECT pub_key FROM users WHERE username = ?", (target,)) as cur:
                            row = await cur.fetchone()
                        if row:
                            await ws.send(json.dumps({"pub_key": row[0]}))
                        else:
                            await ws.send(json.dumps({"error": f"{target} not found"}))
                    elif action == "get_notifications":
                        async with db.execute("SELECT message FROM queue WHERE to_ = ?", (username,)) as cur:
                            rows = await cur.fetchall()
                        count = {}
                        for (raw_msg,) in rows:
                            m = json.loads(raw_msg)
                            f = m.get("from")
                            count[f] = count.get(f, 0) + 1
                        await ws.send(json.dumps(count))
                    elif action == "ready":
                        async with db.execute("SELECT id, message FROM queue WHERE to_ = ?", (username,)) as cur:
                            rows = await cur.fetchall()
                        for _, raw_msg in rows:
                            await ws.send(raw_msg)
                        await db.execute("DELETE FROM queue WHERE to_ = ?", (username,))
                        await db.commit()
                    elif "to" in msg:
                        to = msg["to"]
                        sender = msg.get("from", username)
                        ts = msg.get("timestamp", 0)
                        chat_id = "_".join(sorted([sender, to]))
                        if to in clients:
                            try:
                                await clients[to].send(raw)
                            except websockets.exceptions.ConnectionClosed:
                                await db.execute(
                                    "INSERT INTO queue (to_, message) VALUES (?, ?)",
                                    (to, raw)
                                )
                                await db.commit()
                        else:
                            await db.execute(
                                "INSERT INTO queue (to_, message) VALUES (?, ?)",
                                (to, raw)
                            )
                            await db.commit()
                        await db.execute(
                            "INSERT INTO messages (chat_id, sender, to_, message, timestamp) VALUES (?, ?, ?, ?, ?)",
                            (chat_id, sender, to, raw, ts)
                        )
                        await db.commit()
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
