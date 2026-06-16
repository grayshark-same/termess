from storage import * 
from connections import *
import asyncio
from plyer import notification

last_count = 0 
async def run():
    while True:
        global last_count
        notifs = await get_notifications()
        current_count = 0 
        for _, count in notifs.items():
            current_count += count
        # print(current_count)
        if last_count < current_count:
            msg = ", ".join(f"{s}: {c}" for s, c in notifs.items() if c > 0)
            notification.notify(title="termess", message=msg or "new messages")
        last_count = current_count
        await asyncio.sleep(60)

asyncio.run(run())