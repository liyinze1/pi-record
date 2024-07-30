import socket
import time

status = b'r'

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
        sock.sendto(sn + status, addr)
    elif msg == b'r':
        sock.sendto(sn + status, addr)
    elif msg == b's':
        sock.sendto(sn + status, addr)