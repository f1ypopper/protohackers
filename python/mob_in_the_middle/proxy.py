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
    state = 'RUNNING'
    async def disconnect():
        state = 'STOP'

    async def handle_proxy_msg():
        while True:
            proxy_msg = (await proxy_reader.readline()).decode()
            if not proxy_msg:
                await disconnect()
            logging.info(f"{UPSTREAM_SERVER} received msg: {proxy_msg.strip()}")
            malicious_msg = re.sub(BOGUS_RE, TONY_BOGUS, proxy_msg)
            client_writer.write(malicious_msg.encode())
            await client_writer.drain()
            logging.info(f"{addr} sent msg: {malicious_msg.strip()}")

    async def handle_client_msg():
        while True:
            client_msg = (await client_reader.readline()).decode()
            if not client_msg:
                await disconnect()
            logging.info(f"{addr} received msg: {client_msg.strip()}")
            malicious_msg = re.sub(BOGUS_RE, TONY_BOGUS, client_msg)
            proxy_writer.write(malicious_msg.encode())
            await proxy_writer.drain()
            logging.info(f"{UPSTREAM_SERVER} sent msg: {malicious_msg.strip()}")

    client_task = asyncio.create_task(handle_client_msg())
    proxy_task = asyncio.create_task(handle_proxy_msg())

    while True:
        if state == 'STOP':
            handle_client_msg.cancel()
            handle_proxy_msg.cancel()
            await asyncio.gather(client_task)
            await asyncio.gather(proxy_task)
            await client_writer.drain()
            await proxy_writer.drain()
            client_writer.close()
            proxy_writer.close()
            logging.info(f'{addr} disconnected')
            break

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle_client, PROXY, PROXY_PORT)
    logging.info(f"proxy serving on {PROXY}:{PROXY_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
