import asyncio
import logging

PROXY = "0.0.0.0"
PORT = 5000

u8 = 1
u16 = 2
u32 = 4

Error = 0x10
Plate = 0x20
Ticket = 0x21
WantHeartbeat = 0x40
Heartbeat = 0x41
IAmCamera = 0x80
IAmDispatcher = 0x81

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    logging.info(f"accepted new connection from {writer.get_extra_info('peername')}")

    heart_beat_task = None
    heart_beat_interval = 0

    async def disconnect():
        pass

    async def read_int(size):
        integer = await reader.readexactly(size)
        return int.from_bytes(integer, 'big')

    async def read_str():
        length = await read_int(u8)
        string = await reader.readexactly(length)
        return string.decode()

    async def handle_camera_client():
        pass

    async def handle_dispatcher_client():
        pass
        
    async def heart_beat():
        if interval != 0:
            while not writer.is_closing():
                await asyncio.sleep(interval)
                writer.write(Heartbeat.to_bytes(1, 'big')) 
                await writer.drain()

    while not reader.at_eof():
        msg_type = await read_int(u8)
        if msg_type == IAmCamera:
            logging.info(f"camera client connected {writer.get_extra_info('peername')}")
            await handle_camera_client()
        elif msg_type == IAmDispatcher:
            logging.info(f"dispatcher client connected {writer.get_extra_info('peername')}")
            await handle_dispatcher_client()
        elif msg_type == WantHeartbeat:
            interval = (await read_int(u32))/10
            logging.info(f"heartbeat interval set {interval} seconds")
            heart_beat_task = asyncio.create_task(heart_beat())

async def main():
    server = await asyncio.start_server(handle_client, PROXY, PORT)
    logging.info(f"server running on {PROXY}:{PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())