import socket
import threading
import time
import yaml

def import_device():
    f = open('devices.yaml', 'r')
    d = yaml.safe_load(f)
    f.close()
    return d

class Pi_controller():
    
    def __init__(self, host='127.0.0.1', port=22000):
        self.addr = (host, port)
        self.event_dict = {tuple: threading.Event}
        self.sn_dict = {tuple: int}
        self.receive_dict = {tuple: bytes}
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.addr)
        
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # print('--------', self.sock.connect(self.addr))
        
        self.receive_thread = threading.Thread(target=self._receive_message)
        self.receive_thread.start()
        
    def send(self, data, dest, timeout=1, retry=3):
        if dest not in self.event_dict:
            self.event_dict[dest] = threading.Event()
            self.sn_dict[dest] = 0
        
        self.sn_dict[dest] += 1
        self.sn_dict[dest] %= 128
        
        sn = self.sn_dict[dest].to_bytes(1, 'big')
        
        print('sending', data, 'to', dest, 'sn=', sn[0])
        
        for _ in range(retry):
            try:
                self.sock.sendto(sn + data, dest)
                # break
                self.event_dict[dest].wait(timeout=timeout)
                if self.event_dict[dest].is_set():
                    print("Correct SN received")
                    return self.receive_dict[dest]
                else:
                    print("Timeout or incorrect SN, resending message")
                    self.event_dict[dest].clear()
            except:
                print("Timeout, resending message")
        print('Already tried', retry, 'times...')
        return None
    
    def status(self, dest):
        return self.send(b'?', dest, timeout=1, retry=3)
    
    def record(self, dest):
        return self.send(b'r', dest, timeout=3, retry=3)
    
    def stop(self, dest):
        return self.send(b's', dest, timeout=3, retry=3)

    def _receive_message(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            print('received message', data, addr)
            if self.sn_dict[addr] == data[0]:
                self.receive_dict[addr] = data[1:]
                self.event_dict[addr].set()
    