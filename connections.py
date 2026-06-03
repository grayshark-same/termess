import asyncio
import websockets
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout

async def chat(ws, username):
    session = PromptSession()
    stop = asyncio.Event()

    async def receive():
        try:
            async for msg in ws:
                print(f"\n{username}: {msg}")
        except websockets.exceptions.ConnectionClosedError:
            print(f"\n{username} disconnected")

    async def send():
        with patch_stdout():
            try:
                while True:
                    text = await session.prompt_async("> ")
                    if text.startswith('/quit'):
                        stop.set()
                        return
                    await ws.send(text)
            except KeyboardInterrupt:
                stop.set()
    await asyncio.gather(receive(), send())


async def listen(port, username):
    async def handler(ws):
        print(f"connected")
        await chat(ws, username)
    async with websockets.serve(handler, "0.0.0.0", port):
        # print(f"listening port {port}...")
        await asyncio.Future()


async def connect(host, port, username):
    try:
        async with websockets.connect(f"ws://{host}:{port}") as ws:
            print("connected")
            await chat(ws, username)
    except (ConnectionRefusedError, TimeoutError, OSError):
        print("waiting for connecting")
        await listen(port, username)