from asyncio.log import logger
import socket
import logging
from struct import pack
HOST = '0.0.0.0'
PORT = 5000

logging.basicConfig(level=logging.DEBUG)

db = {}
db['version'] = 'Key-DB 1.0'

def parse_insert(data: str):
    return data.split('=',1)

def format_key_value(key:str, value:str):
    return key+"="+value

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    logging.info("server running...")
    while True:
        packet, addr = server.recvfrom(1000)
        packet = packet.decode()
        if '=' in packet:
            key, value = parse_insert(packet)
            if key != "version":
                db[key] = value
                logging.info(f"inserted {key}={value}")
        else:
            value = None
            try:
                value = db[packet]
                logging.info(f"retrieved {packet}={value}")
            except:
                logging.info(f"key:{packet} not found")
                value = ""
            msg = format_key_value(packet, value)
            server.sendto(msg.encode(), addr)

    server.close()
if __name__ == '__main__':
    main()