import socket
import time
import pi_utils

status = b'ready'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 22000))

pi_recorder = pi_utils.Pi_recorder()

while True:
    data, addr = sock.recvfrom(1024)
    ip = addr[0]
    print(data, addr)
    sn = data[:1]
    cmd = data[1:2]
    msg = data[2:].decode('ascii')
    
    print(sn + status)
    if cmd == b'?':
        status = pi_recorder.status()
    elif cmd == b'r':
        # pass the ip address and the port
        status = pi_recorder.record(ip, msg)
    elif cmd == b's':
        status = pi_recorder.stop()
    sock.sendto(sn + status, addr)