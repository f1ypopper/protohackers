from asyncio.log import logger
import socket
import logging
HOST = '0.0.0.0'
PORT = 5000

logging.basicConfig(level=logging.DEBUG)

db = {}
db['version'] = 'Key-DB 1.0'

def parse_insert(data: str):
    return data.split('=')
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    logging.info("server running...")
    while True:
        conn, addr = server.accept()
        logging.info(f"accepted conn from {addr}")
        packet = conn.recv(999)
        if not packet:
            conn.close()
            logging.info(f"connection closed {addr}")
        packet = packet.decode()
        if '=' in packet:
            key, value = parse_insert(packet)
            if key != 'version':
                db[key] = value
        else:
            conn.send(db[packet])
    server.close()
if __name__ == '__main__':
    main()