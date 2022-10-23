import asyncio
import logging
import re

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
        while True:
            proxy_msg = (await proxy_reader.readline()).decode()
            logging.info(f"{UPSTREAM_SERVER} received msg: {proxy_msg.strip()}")
            #malicious_msg = re.sub(BOGUS_RE, TONY_BOGUS, proxy_msg)
            malicious_msg = proxy_msg
            client_writer.write(malicious_msg.encode())
            await client_writer.drain()
            logging.info(f"{addr} sent msg: {malicious_msg.strip()}")

    async def handle_client_msg():
        while True:
            client_msg = (await client_reader.readline()).decode()
            logging.info(f"{addr} received msg: {client_msg.strip()}")
            #malicious_msg = re.sub(BOGUS_RE, TONY_BOGUS, client_msg)
            malicious_msg = client_msg
            proxy_writer.write(malicious_msg.encode())
            await proxy_writer.drain()
            logging.info(f"{UPSTREAM_SERVER} sent msg: {malicious_msg.strip()}")

    while not proxy_reader.at_eof() or not  client_reader.at_eof():
        client_task = asyncio.create_task(handle_client_msg())
        proxy_task = asyncio.create_task(handle_proxy_msg())
async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle_client, PROXY, PROXY_PORT)
    logging.info(f"proxy serving on {PROXY}:{PROXY_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
