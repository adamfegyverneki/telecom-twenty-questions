import socket
import struct
import select
import random
import sys

if len(sys.argv) != 3:
    print("Usage: python3 server.py <hostname> <port>")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])

secret = random.randint(1, 100)
game_over = False

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    server_sock.bind((host, port))
    server_sock.listen(5)
except socket.error as e:
    print(f"Server setup failed: {e}")
    sys.exit(1)

clients = []
print(f"Server started, secret number is {secret}")

while True:
    try:
        read_socks, _, _ = select.select([server_sock] + clients, [], [])
        for sock in read_socks:
            if sock is server_sock:
                client_sock, addr = server_sock.accept()
                print(f"New client connected: {addr}")
                clients.append(client_sock)
            else:
                try:
                    data = sock.recv(5)
                    if not data:
                        print(f"Client {sock.getpeername()} disconnected")
                        sock.close()
                        clients.remove(sock)
                        continue
                    if len(data) != 5:
                        print(f"Invalid message length from {sock.getpeername()}: {len(data)}")
                        sock.close()
                        clients.remove(sock)
                        continue
                    char, num = struct.unpack('<ci', data)
                    print(f"Received from {sock.getpeername()}: {char.decode()} {num}")
                    if game_over:
                        response = b'V'
                    else:
                        if char == b'<':
                            response = b'I' if secret < num else b'N'
                        elif char == b'>':
                            response = b'I' if secret > num else b'N'
                        elif char == b'=':
                            if secret == num:
                                response = b'Y'
                                game_over = True
                            else:
                                response = b'K'
                        else:
                            print(f"Invalid char from {sock.getpeername()}: {char}")
                            sock.close()
                            clients.remove(sock)
                            continue
                    print(f"Sending to {sock.getpeername()}: {response.decode()}")
                    sock.send(struct.pack('<ci', response, 0))
                except (socket.error, struct.error) as e:
                    print(f"Client {sock.getpeername()} error: {e}")
                    sock.close()
                    clients.remove(sock)
    except KeyboardInterrupt:
        print("Shutting down server")
        for sock in clients:
            sock.close()
        server_sock.close()
        sys.exit(0)