import asyncio
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
    logging.info("connected to upstream chat server")
    server_msg = await ureader.readline().decode()
    replaced_server_msg = re.sub(BOGUS_RE, TONY_BOGUS, server_msg)
    logging.info(f"[SERVER]{replaced_server_msg}")
    writer.write(replaced_server_msg.encode())
    await writer.drain()
    client_msg = await reader.readline().decode()
    replaced_client_msg = re.sub(BOGUS_RE, TONY_BOGUS, client_msg)
    logging.info(f"[CLIENT]{replaced_client_msg}")
    uwriter.write(replaced_client_msg.encode())
    await uwriter.drain()

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle, PROXY, PROXY_PORT)
    logging.info("proxy server ready")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())