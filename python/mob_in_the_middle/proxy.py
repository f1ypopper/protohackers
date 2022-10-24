import asyncio
import logging
import re

#todo: better regex matching
PROXY = "0.0.0.0"
PROXY_PORT = 5000
UPSTREAM_SERVER = "chat.protohackers.com"
UPSTREAM_PORT = 16963
BOGUS_RE = r"^7(\w{25,36})$"
TONY_BOGUS = "7YWHMfk9JZe0LM0g1ZauHuiSxhI"


def create_mal_msg(msg: str):
    split_msg = msg.split(' ')
    mal_msg = [re.sub(BOGUS_RE, TONY_BOGUS, word) for word in split_msg]
    return ' '.join(mal_msg)

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while not reader.at_eof():
        proxy_msg = (await reader.readline()).decode()
        if not proxy_msg:
            break
        logging.info(f"{UPSTREAM_SERVER} received msg: {proxy_msg.strip()}")
        malicious_msg = create_mal_msg(proxy_msg) 
        writer.write(malicious_msg.encode())

    await writer.drain()
    writer.close()
    logging.info("connection closed")

async def handle_client(client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter):  
    addr = client_writer.get_extra_info('peername')
    logging.info(f"{addr} connected to the proxy server")
    proxy_reader, proxy_writer = await asyncio.open_connection(UPSTREAM_SERVER, UPSTREAM_PORT)
    asyncio.gather(handle(proxy_reader, client_writer), handle(client_reader, proxy_writer))
#    async def handle_proxy_msg():
#        while True:
#            proxy_msg = (await proxy_reader.readline()).decode()
#            logging.info(f"{UPSTREAM_SERVER} received msg: {proxy_msg.strip()}")
#            malicious_msg = create_mal_msg(proxy_msg) 
#            if not malicious_msg:
#                raise asyncio.CancelledError
#            client_writer.write(malicious_msg.encode())
#            await client_writer.drain()
#            logging.info(f"{addr} sent msg: {malicious_msg.strip()}")
#
#    async def handle_client_msg():
#        while True:
#            client_msg = (await client_reader.readline()).decode()
#            malicious_msg = create_mal_msg(client_msg)
#            if not malicious_msg:
#                raise asyncio.CancelledError
#            proxy_writer.write(malicious_msg.encode())
#            await proxy_writer.drain()
#            logging.info(f"{addr} received msg: {client_msg.strip()}")
#            logging.info(f"{UPSTREAM_SERVER} sent msg: {malicious_msg.strip()}")

#    client_task = asyncio.create_task(handle_client_msg())
#    proxy_task = asyncio.create_task(handle_proxy_msg())
#    try:
#        await client_task
#        await proxy_task
#    except asyncio.CancelledError:
#        client_task.cancel()
#        proxy_task.cancel()
#        await client_writer.drain()
#        await proxy_writer.drain()
#        client_writer.close()
#        proxy_writer.close()
#        logging.info("client closed")

async def main():
    logging.basicConfig(level=logging.DEBUG)
    server = await asyncio.start_server(handle_client, PROXY, PROXY_PORT)
    logging.info(f"proxy serving on {PROXY}:{PROXY_PORT}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())