import asyncio
import websockets
import base64
from nacl.public import PrivateKey, PublicKey, Box
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from storage import *

async def exchange_keys(ws):
    # загрузить свой приватный ключ
    my_pub_key, my_priv_key = get_keys()

    await ws.send(base64.b64encode(bytes(my_pub_key)).decode())
    their_pub_key_b64 = await ws.recv()
    their_pub_key = PublicKey(base64.b64decode(their_pub_key_b64))
    return Box(my_priv_key, their_pub_key)

async def chat(ws, username, box):
    session = PromptSession()
    stop = asyncio.Event()

    async def receive():
        try:
            async for msg in ws:
                decrypted = box.decrypt(base64.b64decode(msg)).decode()
                print(f"{username}: {decrypted}")
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
                    await ws.send(encrypted)
            except KeyboardInterrupt:
                stop.set()
    await asyncio.gather(receive(), send())


async def listen(port, username):
    async def handler(ws):
        box = await exchange_keys(ws)
        print(f"connected")
        await chat(ws, username, box)
    async with websockets.serve(handler, "0.0.0.0", port):
        # print(f"listening port {port}...")
        await asyncio.Future()


async def connect(host, port, username):
    try:
        async with websockets.connect(f"ws://{host}:{port}") as ws:
            box = await exchange_keys(ws)
            print("connected")
            await chat(ws, username, box)
    except (ConnectionRefusedError, TimeoutError, OSError):
        print("waiting for connecting")
        await listen(port, username)