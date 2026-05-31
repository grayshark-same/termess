import asyncio
import websockets

async def listen(port):
    async def handler(ws):
        async for msg in ws:
            print(f"получено: {msg}")
            await ws.send(f"echo: {msg}")
    
    async with websockets.serve(handler, "0.0.0.0", port):
        print(f"слушаю порт {port}...")
        await asyncio.Future()

async def connect(host, port):
    async with websockets.connect(f"ws://{host}:{port}") as ws:
        while True:
            msg = input("> ")
            await ws.send(msg)
            reply = await ws.recv()
            print(reply)