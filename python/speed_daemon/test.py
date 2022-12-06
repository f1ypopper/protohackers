import asyncio
import time

async def t_run(interval):
    async def heart_beat():
        while True:
            await
    while True:
        await asyncio.sleep(interval)
        print(f"hi from t_run {interval}")

async def main():
asyncio.run(main())