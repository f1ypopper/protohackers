import logging
import asyncio
import time
PROXY = "0.0.0.0"
PROXY_PORT = 5000

u8 = 1
u16 = 2
u32 = 4

async def read_int(reader: asyncio.StreamReader, num_bytes: int) -> int:
    return int.from_bytes(await reader.readexactly(num_bytes), 'big')

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    interval = 0
    heart_task = None
    async def heart_beat():
        logging.info(f"inside a heart_beat task with interval {interval}")
        start = time.time()
        while True:
            if interval != 0 and time.time() - start >= interval:
                writer.write((0x41).to_bytes(1, 'big'))
                await writer.drain()
                start = time.time()
                logging.info(f"sent heart beat at interval {interval}")

    msg_type = await read_int(reader, u8)
    logging.info(f"recieved msg {msg_type}")
    if msg_type == 0x40:
        interval = (await read_int(reader, u32))/10
        heart_task = asyncio.create_task(heart_beat())

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle_client, PROXY, PROXY_PORT)
    logging.info(f"proxy serving on {PROXY}:{PROXY_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())