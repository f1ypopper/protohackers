import socket
import selectors
import types
import json

sel = selectors.DefaultSelector()

def accept_wrapper(sock: socket.socket):
    conn, addr = sock.accept()
    print(f"accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print(f"closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:
#            print(f"echoing {data.outb!r} to {data.addr}")
            req = json.loads(data.outb)
            print(req)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

host = '0.0.0.0'
port = 5000


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print(f"listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)

except KeyboardInterrupt:
    print("closing server")
finally:
    sel.close()