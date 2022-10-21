import asyncio
from asyncore import write
from dis import disco
import logging
import re

PROXY = "0.0.0.0"
PROXY_PORT = 5000
UPSTREAM_SERVER = "chat.protohackers.com"
UPSTREAM_PORT = 16963
BOGUS_RE = "7\w{25,35}"
TONY_BOGUS = "7YWHMfk9JZe0LM0g1ZauHuiSxhI"

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    ureader, uwriter = await asyncio.open_connection(UPSTREAM_SERVER, UPSTREAM_PORT)
    async def disconnect():
        await uwriter.drain()
        await writer.drain()
        writer.close()
        uwriter.close()
        logging.info("connection closed")
        return 
    try:
        while not reader.at_eof() or not ureader.at_eof():
            server_msg = await ureader.readline()
            if not server_msg:
                await disconnect()
            replaced_server_msg = re.sub(BOGUS_RE, TONY_BOGUS, server_msg.decode())
            logging.info(f"[SERVER]{replaced_server_msg.strip()}")
            writer.write(replaced_server_msg.encode())
            await writer.drain()
            client_msg = await reader.readline()
            if not client_msg:
                await disconnect()
            replaced_client_msg = re.sub(BOGUS_RE, TONY_BOGUS, client_msg.decode())
            logging.info(f"[CLIENT]{replaced_client_msg.strip()}")
            uwriter.write(replaced_client_msg.encode())
            await uwriter.drain()
    except ValueError:
        pass
    finally:
        await uwriter.drain()
        await writer.drain()
        writer.close()
        uwriter.close()
        logging.info("connection closed") 

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle, PROXY, PROXY_PORT)
    logging.info("proxy server ready")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())