import math
import socket
import struct
import sys, os, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from base_server.base_server import BaseServer
import bisect
host = '0.0.0.0'
port = 5000
num_threads = 5



class TimeSeriesDB:
    def __init__(self) -> None:
        self.db = []

    def insert(self, timestamp, price):
        entry = {'timestamp': timestamp, 'price':price}
        bisect.insort(self.db, entry, key=self.by_timestamp) #insert item without sorting everytime

    def by_timestamp(self, entry):
        return entry['timestamp']

    def query(self, mintime, maxtime):
        aggregate = 0
        entry_count = 0
        for entry in self.db:
            if mintime <= entry['timestamp']  and entry['timestamp'] <= maxtime:
                aggregate+=entry['price']
                entry_count+=1
        if aggregate == 0:
            return 0
        mean = math.floor(aggregate/entry_count)
        return mean

def handle_connection(client: socket.socket, addr):

    print(f'connected to {addr}')
    try:
        db = TimeSeriesDB()
        with client, client.makefile('rwb') as conn:
            while True:
                raw_msg = conn.read(9)
                print(raw_msg)
                if not raw_msg:
                    conn.close()
                    print(f'connection closed {addr}')
                    return

                msg_type, val1, val2 = struct.unpack('>cii', raw_msg)

                if msg_type != b'I' and  msg_type != b'Q':
                    conn.close()
                    print(f'connection closed {addr}')
                    return

                if msg_type == b'I':
                    timestamp = val1
                    price = val2
                    entry = {'timestamp':timestamp, 'price':price}
                    print(f'inserted {entry}')
                    db.insert(timestamp, price)

                elif msg_type == b'Q':
                    mintime = val1
                    maxtime = val2
                    aggregate = db.query(mintime, maxtime)
                    conn.write(struct.pack('>i',aggregate))
                    conn.flush()
                    print(f'query result {aggregate}')

    except Exception  as e:
        print(f"exception occurred: {e}")
    finally:
        client.close()

def main():
    server = BaseServer(host, port, num_threads)
    server.start(handle_connection)

if __name__ == '__main__':
    main()
