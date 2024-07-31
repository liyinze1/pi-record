import socket
import time

status = b'ready'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 22000))

while True:
    data, addr = sock.recvfrom(1024)
    print(data, addr)
    # sock.sendto(data, addr)
    
    sn = data[:1]
    msg = data[1:]
    print(sn + status)
    if msg == b'?':
        pass
    elif msg == b'r':
        pass
    elif msg == b's':
        pass
    sock.sendto(sn + status, addr)