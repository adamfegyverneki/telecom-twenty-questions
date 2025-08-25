import socket
import struct
import sys

if len(sys.argv) != 3:
    print("Usage: python3 client.py <hostname> <port>")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])

print(f"Starting client, connecting to {host}:{port}")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")
    s.connect((host, port))
    print("Connected to server")
except socket.error as e:
    print(f"Connection failed: {e}")
    sys.exit(1)

low = 1
high = 100
print(f"Starting binary search: low={low}, high={high}")

while low < high:
    mid = (low + high) // 2
    print(f"Sending guess: > {mid}")
    try:
        s.send(struct.pack('<ci', b'>', mid))
        print("Guess sent, waiting for response")
        data = s.recv(5)
        if not data:
            print("Server closed connection")
            s.close()
            sys.exit(0)
        print(f"Received {len(data)} bytes")
        char, _ = struct.unpack('<ci', data)
        print(f"Server response: {char.decode()}")
        if char in [b'Y', b'K', b'V']:
            print(f"Terminating with response: {char.decode()}")
            s.close()
            sys.exit(0)
        elif char == b'I':
            low = mid + 1
            print(f"Adjusting: low={low}, high={high}")
        elif char == b'N':
            high = mid
            print(f"Adjusting: low={low}, high={high}")
        else:
            print(f"Invalid server response: {char.decode()}")
            s.close()
            sys.exit(1)
    except (socket.error, struct.error) as e:
        print(f"Error during communication: {e}")
        s.close()
        sys.exit(1)

print(f"Final guess: = {low}")
try:
    s.send(struct.pack('<ci', b'=', low))
    print("Final guess sent, waiting for response")
    data = s.recv(5)
    if not data:
        print("Server closed connection")
        s.close()
        sys.exit(0)
    print(f"Received {len(data)} bytes")
    char, _ = struct.unpack('<ci', data)
    print(f"Server response: {char.decode()}")
    if char in [b'Y', b'K', b'V']:
        print(f"Terminating with response: {char.decode()}")
        s.close()
        sys.exit(0)
    else:
        print(f"Invalid server response: {char.decode()}")
        s.close()
        sys.exit(1)
except (socket.error, struct.error) as e:
    print(f"Error during final communication: {e}")
    s.close()
    sys.exit(1)