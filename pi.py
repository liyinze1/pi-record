import socket
import time
import pi_utils

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 22000))

pi_recorder = pi_utils.Pi_recorder()

while True:
    status = b''
    
    data, addr = sock.recvfrom(1024)
    ip = addr[0]

    sn = data[:1]
    cmd = data[1:2]
    msg = data[2:]
    
    print(addr, 'sn:', sn, 'cmd:', cmd, 'msg:', msg)
    
    if cmd == b'?':
        status = pi_recorder.status()
    elif cmd == b'r':
        # pass the ip address and the port
        port = int.from_bytes(msg, 'big')
        print('Get port number:', port)
        status = pi_recorder.record(ip, port)
    elif cmd == b's':
        status = pi_recorder.stop()
    
    print(sn + status)
    sock.sendto(sn + status, addr)