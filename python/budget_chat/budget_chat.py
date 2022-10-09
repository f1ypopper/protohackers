import socket
import selectors
from stream import StreamReader

HOST = '0.0.0.0'
PORT = 5000
sel = selectors.DefaultSelector()
clients = {}

def create_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.setblocking(False)
    server.listen(10)
    sel.register(server, selectors.EVENT_READ)
    return server

def room_users():
    usernames = [reader.username for reader in clients.values() if reader.username]
    return "* This room contains: "+", ".join(usernames)

def usr_msg(username, msg):
    return f"[{username}] {msg}"

def close_conn(fileobj):
    sel.unregister(fileobj)
    del clients[fileobj]
    fileobj.close()
    print("connection closed")

def check_username(username: str):
    if not username.isalnum():
        return False
    if len(username) < 1:
        return False
    return True

def main():
    server = create_server()
    print(f"server listening on {HOST}:{PORT}")

    while True:
        events = sel.select()
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                if key.fileobj == server:
                    conn, addr = server.accept()
                    conn.setblocking(False)
                    sel.register(conn, selectors.EVENT_READ)
                    print(f"accepted connection from {addr}")
                    conn.send(b"Welcome to the server! Enter your username\n")
                    clients[conn] = StreamReader(conn,'')
                else:
                    stream = clients[key.fileobj]
                    data = stream.readline()
                    msg = ""
                    if not data:
                        close_conn(key.fileobj)
                        msg = f"* {stream.username} has left the room\n"
                    else:
                        if not stream.username:
                            username = data.decode().rstrip()
                            if not check_username(username):
                                close_conn(key.fileobj)
                            key.fileobj.send((room_users()+"\n").encode())
                            stream.username = username
                            msg = f"* {username} has joined the room\n"
                        else:
                            msg = usr_msg(stream.username, data.decode().rstrip())+"\n"

                    for client, data in clients.items():
                        if client != key.fileobj and data.username:
                            client.send(msg.encode())

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("server closing...")