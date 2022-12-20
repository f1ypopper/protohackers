import asyncio
import logging
import struct
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

async def read_int(reader: asyncio.StreamReader, int_size):
    return int.from_bytes(await reader.readexactly(int_size),byteorder='big')

async def read_str(reader: asyncio.StreamReader):
    str_len = await read_int(reader, u8)
    return (await reader.readexactly(str_len)).decode()

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        while True:
            msg_type = await read_int(reader, u8)
    except EOFError:
        pass

async def main():
    server = await asyncio.start_server(handle_client, PROXY, PORT)
    logging.info(f"started server on {PROXY}:{PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())