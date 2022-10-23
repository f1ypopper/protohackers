import asyncio
import logging
import re
from weakref import proxy

PROXY = "0.0.0.0"
PROXY_PORT = 5000
UPSTREAM_SERVER = "chat.protohackers.com"
UPSTREAM_PORT = 16963
BOGUS_RE = r"7\w{25,35}"
TONY_BOGUS = "7YWHMfk9JZe0LM0g1ZauHuiSxhI"


async def handle_client(client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter):  
    addr = client_writer.get_extra_info('peername')
    logging.info(f"{addr} connected to the proxy server")
    proxy_reader, proxy_writer = await asyncio.open_connection(UPSTREAM_SERVER, UPSTREAM_PORT)

    async def handle_proxy_msg():
        proxy_msg = (await proxy_reader.readline()).decode()
        logging.info(f"{UPSTREAM_SERVER} received msg: {proxy_msg.strip()}")
        malicious_msg = re.sub(BOGUS_RE, TONY_BOGUS, proxy_msg)
        client_writer.write(malicious_msg.encode())
        logging.info(f"{addr} sent msg: {malicious_msg.strip()}")
        await client_writer.drain()

    async def handle_client_msg():
        client_msg = (await client_reader.readline()).decode()
        logging.info(f"{addr} received msg: {client_msg.strip()}")
        malicious_msg = re.sub(BOGUS_RE, TONY_BOGUS, client_msg)
        proxy_writer.write(malicious_msg.encode())
        logging.info(f"{UPSTREAM_SERVER} sent msg: {malicious_msg.strip()}")
        await proxy_writer.drain()

    while not proxy_reader.at_eof() or not  client_reader.at_eof():
        await handle_proxy_msg()
        await handle_client_msg()

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle_client, PROXY, PROXY_PORT)
    logging.info(f"proxy serving on {PROXY}:{PROXY_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())