import math
import socket
import struct
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from base_server.base_server import BaseServer

host = '0.0.0.0'
port = 5000
num_threads = 5

def time_ascending_func(entry):
    return entry['timestamp']

class TimeSeriesDB:
    def __init__(self) -> None:
        self.db = []

    def insert(self, timestamp, price):
        entry = {'timestamp': timestamp, 'price':price}

        if self.db.count() == 0:
            self.db.append(entry)
            return

        if self.db[0]['timestamp'] >= entry['timestamp']:
            self.db.insert(0, entry)
            return

        self.db.append(entry)
        self.db.sort(key=time_ascending_func)

    def query(self, mintime, maxtime):
        aggregate = 0
        entry_count = 0
        for entry in self.db:
            if entry['timestamp'] >= mintime and entry['timestamp'] <= maxtime:
                aggregate+=entry['price']
                entry_count+=1

        mean = math.floor(aggregate/entry_count)
        return mean

def handle_connection(conn: socket.socket, addr):
    print(f'connected to {addr}')

    db = TimeSeriesDB()

    while True:
#        raw_msg = conn.recv(9)
#        print(raw_msg)

        msg_type = conn.recv(1)
        val1 = conn.recv(4)
        val2 = conn.recv(4)
        if not msg_type:
            conn.close()
            print(f'connection closed {addr}')
            return

#        msg_type, val1, val2 = struct.unpack('cii', raw_msg)
        if msg_type != b'I' and  msg_type != b'Q':
            conn.close()
            print(f'connection closed {addr}')
            return

        if msg_type == b'I':
            timestamp = int.from_bytes(val1, "big")
            price = int.from_bytes(val2, "big")
            entry = {'timestamp':timestamp, 'price':price}
            db.insert(entry)
            print(f'inserted {entry}')

        elif msg_type == b'Q':
            mintime = int.from_bytes(val1, "big")
            maxtime = int.from_bytes(val2, "big")
            aggregate = db.query(mintime, maxtime)
            conn.send(aggregate)
            print(f'query result {aggregate}')

def main():
    server = BaseServer(host, port, num_threads)
    server.start(handle_connection)

if __name__ == '__main__':
    main()