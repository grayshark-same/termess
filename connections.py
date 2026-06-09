import asyncio
import websockets
import base64
from nacl.public import PrivateKey, PublicKey, Box
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from storage import *
from prompt_toolkit.completion import NestedCompleter 
import time
from datetime import datetime, timezone, timedelta
import json

async def exchange_keys(ws):
    # загрузить свой приватный ключ
    my_pub_key, my_priv_key = get_keys()

    await ws.send(base64.b64encode(bytes(my_pub_key)).decode())
    their_pub_key_b64 = await ws.recv()
    their_pub_key = PublicKey(base64.b64decode(their_pub_key_b64))
    return Box(my_priv_key, their_pub_key)

async def chat(ws, username, box):
    completer = NestedCompleter.from_nested_dict({
        "/quit": None
    })
    session = PromptSession(completer=completer)
    stop = asyncio.Event()

    async def receive():
        try:
            async for raw in ws:
                msg = json.loads(raw)
                decrypted = box.decrypt(base64.b64decode(msg['text'])).decode()
                tz = timezone(timedelta(hours=int(load_config().get('tz', 0))))
                dt = datetime.fromtimestamp(msg["timestamp"], tz=tz)
                print(f"[{dt.strftime('%H:%M')}] {username or msg['from']}: {decrypted}")
                # print(f"debug: timestamp={msg['timestamp']}, tz={load_config().get('tz')}")
        except websockets.exceptions.ConnectionClosedError:
            print(f"\n{username} disconnected")

    async def send():
        with patch_stdout():
            try:
                # await ws.send(get_keys()[0])
                while True:
                    text = await session.prompt_async("> ")
                    if text.startswith('/quit'):
                        stop.set()
                        return
                    encrypted = base64.b64encode(box.encrypt(text.encode())).decode()
                    msg = {'type': 'message',
                           "from": load_config().get('username', 'anon'),
                           'to': username,
                           'text': encrypted,
                           'timestamp': int(time.time())
                           }
                    await ws.send(json.dumps(msg))
            except KeyboardInterrupt:
                stop.set()
    await asyncio.gather(receive(), send())


async def chat_server(ws, to, box):
    session = PromptSession()

    async def receive():
        try:
            async for raw in ws:
                msg = json.loads(raw)
                if "error" in msg:
                    print(f"[!] {msg['error']}")
                else:
                    decrypted = box.decrypt(base64.b64decode(msg["text"])).decode()
                    tz = timezone(timedelta(hours=int(load_config().get('tz', 0))))
                    dt = datetime.fromtimestamp(msg["timestamp"], tz=tz)
                    print(f"[{dt.strftime('%H:%M')}] {msg['from']}: {decrypted}")
        except websockets.exceptions.ConnectionClosedError:
            print("\ndisconnected from server")

    async def send():
        with patch_stdout():
            while True:
                text = await session.prompt_async("> ")
                if text.startswith('/quit'):
                    return
                encrypted = base64.b64encode(box.encrypt(text.encode())).decode()
                msg = {
                    "to": to,
                    "from": load_config().get('username'),
                    "text": encrypted,
                    "timestamp": int(time.time())
                }
                await ws.send(json.dumps(msg))

    await asyncio.gather(receive(), send())


async def listen(port, username):
    async def handler(ws):
        box = await exchange_keys(ws)
        print(f"connected")
        await chat(ws, username, box)
    async with websockets.serve(handler, "0.0.0.0", port):
        # print(f"listening port {port}...")
        await asyncio.Future()

async def connect_server(host, port, to):
    my_pub, my_priv = get_keys()
    me = load_config()["username"]
    try:
        async with websockets.connect(f"ws://{host}:{port}") as ws:
            await ws.send(json.dumps({
                "action": "register",
                "from": me,
                "pub_key": base64.b64encode(bytes(my_pub)).decode()
            }))
            
            await ws.send(json.dumps({"action": "get_key", "username": to}))
            resp = json.loads(await ws.recv())
            if "error" in resp:
                print(f"[!] {resp['error']}")
                return
            their_pub = PublicKey(base64.b64decode(resp["pub_key"]))
            box = Box(my_priv, their_pub)
            
            await chat_server(ws, to, box)
    except KeyError:
        print('something went wrong')
    except Exception as e:
        print(f'cannot connect to server: {e}')
async def connect(host, port, username):
    try:
        async with websockets.connect(f"ws://{host}:{port}") as ws:
            box = await exchange_keys(ws)
            print("connected")
            await chat(ws, username, box)
    except (ConnectionRefusedError, TimeoutError, OSError):
        print("waiting for connecting")
        await listen(port, username)