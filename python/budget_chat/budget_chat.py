import types
import selectors
import socket

HOST = '0.0.0.0'
PORT = 5000
WELCOME_MESSAGE = "Welcome to the server! Enter your username"
server_fileno = int()
sel = selectors.DefaultSelector()
users = []

def check_username(username:str):
    if len(username) < 1:
        return False
    if not username.isalnum():
        return False
    return True

def readline(conn: socket.socket):
    line = bytes()
    while True:
        c = conn.recv(1)
        if c == b'\n' or c == b'\r':
            return line
        line+=c
    return line.decode()

def accept_new_connection(sock: socket.socket):
    conn, addr = sock.accept()
    conn.setblocking(False)
    #send the welcome message and get the username
    conn.sendall(WELCOME_MESSAGE.encode())
    username = readline(conn)
    print(username)
    if not check_username(username):
        print("invalid username closing connection ...")
        conn.close()
        return
    room_users_msg = f"* this room contains: {', '.join(users)}"
    conn.sendall(room_users_msg.encode())
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", username=username)
    sel.register(conn,selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
    users.append(username)
    print(f"new user added to {', '.join(users)}")

    events = sel.select()
    inform_new_user_msg = f"* {username} has joined the room"
    for key, mask in events:
        if mask & selectors.EVENT_READ:
            if key.fileobj != sock and key.fileobj != server_fileno:
                u = key.fileobj
                u.sendall(inform_new_user_msg.encode())


def service_connection(key: selectors.SelectorKey, mask):
    sock = key.fileobj
    data = key.data
    msg = str()
    if mask & selectors.EVENT_READ:
        msg = readline(sock)
    formatted_msg = str()
    if not msg:
        sock.close()
        formatted_msg = f"* {data.username} has left the room"
    else:
        formatted_msg = f"[{data.username}] {msg}"
    events = sel.select()
    for key, mask in events:
        if mask & selectors.EVENT_READ:
            if key.fileobj != sock and key.fileobj != server_fileno:
                conn = key.fileobj
                conn.sendall(formatted_msg.encode())


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.fileno
    server.bind((HOST, PORT))
    server.makefile('rwb')
    server.setblocking(False)
    server.listen(10)
    global server_fileno
    server_fileno = server.fileno
    print(f'server listening on {(HOST, PORT)}...')

    sel.register(server, selectors.EVENT_READ, None)
    try:
        while True:
            events = sel.select()
            for key, mask in events:
                if key.data is None:
                    accept_new_connection(key.fileobj)
                else:
                    service_connection(key, mask)

    except KeyboardInterrupt:
        print("server closed")
    finally:
        server.close()

if __name__ == '__main__':
    main()