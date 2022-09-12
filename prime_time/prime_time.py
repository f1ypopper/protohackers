import socket
import json
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from itertools import count

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from base_server.base_server import BaseServer

host = '0.0.0.0'
port = 5000


SEED = 22801763489  # One-billionth prime number


class PrimeTest:
    def __init__(self):
        self.__P = {}
        self.__gen = self.__primes()
        self.__top = 0

    @staticmethod
    def __primes():
        ps = defaultdict(list)
        for i in count(2):
            if i not in ps:
                yield i
                ps[i**2].append(i)
            else:
                for n in ps[i]:
                    ps[i + (n if n == 2 else 2 * n)].append(n)
                del ps[i]

    def __next_prime(self) -> int:
        i = next(self.__gen)
        self.__P[i] = None
        self.__top = max(self.__top, i)
        return i

    def is_prime(self, n) -> bool:
        # Is it a known prime?
        if type(n) == float:
            return False

        if n in self.__P:
            return True

        # Is it a known composite?
        if n <= self.__top and n not in self.__P:
            return False

        # Trial division
        for p in self.__P:
            if p * p >= n:
                return True
            if n % p == 0:
                return False

        # Make new primes on the fly until sqrt
        while True:
            p = self.__next_prime()
            if p * p >= n:
                return True
            if n % p == 0:
                return False


pt = PrimeTest()

def handle_connection(conn:socket.socket, addr):
    print(f"connected to {addr}")

    while True:
        recv_data = b''
        #Read the JSON request until the newline or until EOF
        while True:
            c = conn.recv(1)
            if c:
                if c == b'\n':
                    break
                recv_data+=c
            else:
                conn.close()
                print(f"connection closed {addr}")
                return

        #Write the JSON response
        res = {}

        try:
            j_req = json.loads(recv_data)
            num_types = [int, float]
            if j_req.get("method") == None or j_req.get("number") == None:
                res["method"] = "malformed request"
            elif j_req["method"] != "isPrime" or type(j_req["number"]) not in num_types:
                res["method"] = "malformed request"
            elif pt.is_prime(j_req["number"]):
                res["method"] = "isPrime"
                res["prime"] = True
            else:
                res["method"] = "isPrime"
                res["prime"] = False

        except:
            res["method"] = "malformed request"
            raw_response = json.dumps(res)+"\n"
            conn.send(raw_response.encode())
            print(res)
            conn.close()
            return

        print(j_req)

        raw_response = json.dumps(res)+"\n"
        conn.send(raw_response.encode())
        print(res)

def main():
    num_threads = 5
    server = BaseServer(host, port, num_threads)
    server.start(handle_connection)

#    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            #server.bind((host, port))
            #server.listen()
            #print(f"server listening on {(host,port)}")
            #while True:
                #conn, addr = server.accept()
                #executor.submit(handle_connection, conn, addr)
    #print("server shutting down")

if __name__ == '__main__':
    main()