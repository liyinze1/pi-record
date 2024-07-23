import socket


def message_handler(data):
    if data == b'?':
        return b'A'
    elif data == 'R':
        pass
    elif data == 'S':
        pass

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('0.0.0.0', 22000))
    s.connect(('172.27.182.13', 21000))
    print('successfully connected')
    while True:
        s.send(input().encode('utf-8'))