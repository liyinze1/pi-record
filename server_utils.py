import socket
import threading
import yaml
import logging
import subprocess
import os
import shlex
import datetime
from tinydb import TinyDB, Query

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


f = open('devices.yaml', 'r')
d = yaml.safe_load(f)
f.close()
device_list = {}
for deive, ip in d.items():
    device_list[deive] = (ip, 22000)
    
audio_folder = './audio'

class Port_controller:

    def __init__(self):
        self.port_list = [i for i in range(23000, 23010, 2)]

    def get_port(self):
        logger.info("number of ports %s", len(self.port_list))
        for port in self.port_list:
            logger.info("checking  %s", port)
            if self.check_port(port):
                self.port_list.remove(port)
                return port
        raise Exception('port not found')

    def return_port(self, port):
        self.port_list.append(port)

    def check_port(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = False
        try:
            # sock.bind((server_ip, port))
            sock.bind(('0.0.0.0', port))
            result = True
        except Exception as e:
            logger.info("Port is in use  %s", e)
        sock.close()
        return result

class Receive:

    def __init__(self, vin, port):

        # port
        self.port = port

        logger.info('the selected port for %s is %s', vin, self.port)

        # sdp
        sdp = 'SDP:\n' + \
            'v=0\n' + \
            'o=- 0 0 IN IP4 127.0.0.1\n' + \
            's=No Name\n' + \
            'c=IN IP4 0.0.0.0\n' + \
            't=0 0\n' + \
            'a=tool:libavformat 58.20.100\n' + \
            'm=audio %s RTP/AVP 97\n' % self.port + \
            'b=AS:4608\n' + \
            'a=rtpmap:97 L24/48000/4\n'

        self.sdp_filename = self.get_sdp_filename(vin)
        f = open(self.sdp_filename, 'w')
        f.write(sdp)
        f.close()
        
        logger.info('port:%d'%self.port)

        self.audio_filename = self.get_audio_filename(vin)
        # thread for receiving
        cmd = 'ffmpeg -protocol_whitelist file,http,rtp,tcp,udp -i %s -acodec pcm_s24le %s' % (
            self.sdp_filename, self.audio_filename)
        logger.info(cmd)
        cmd = shlex.split(cmd)
        self.receive_thread = subprocess.Popen(cmd)

    def stop(self):
        self.receive_thread.kill()
        logger.info("returning port %s", self.port)
        return 'ok'
    
    def get_sdp_filename(self, vin):
        filename = vin + '.sdp'
        return os.path.join(audio_folder, filename)
    
    def get_audio_filename(self, vin):
        now = datetime.datetime.now()
        file_name = vin + '-' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.wav'
        return os.path.join(audio_folder, file_name)

class Pi_controller():
    
    def __init__(self, host='0.0.0.0', port=22000):
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
        if dest not in self.sn_dict:
            self.sn_dict[dest] = 0
            self.event_dict[dest] = threading.Event()
            # time.sleep(0.1)
        
        self.sn_dict[dest] += 1
        self.sn_dict[dest] %= 128
        
        sn = self.sn_dict[dest].to_bytes(1, 'big')
        
        print('------------- sending', data, 'to', dest, 'sn=', sn[0], '-------------')
        
        for i in range(retry):
            try:
                print('Try', i+1)
                self.sock.sendto(sn + data, dest)
                # break
                self.event_dict[dest].wait(timeout=timeout)
                if self.event_dict[dest].is_set():
                    print('Correct SN received')
                    return self.receive_dict[dest]
                else:
                    print('Timeout')
                    self.event_dict[dest].clear()
            except Exception as e:
                print('Error', e)
        print('Already tried', retry, 'times...')
        return None
    
    def status(self, dest):
        return self.send(b'?', dest, timeout=1, retry=3)
    
    def record(self, dest, port):
        return self.send(b'r' + int.to_bytes(port, length=2, byteorder='big'), dest, timeout=3, retry=3)
    
    def stop(self, dest):
        return self.send(b's', dest, timeout=3, retry=3)

    def _receive_message(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            print('received message', data, addr)
            if addr not in self.sn_dict:
                print(addr, 'not in dictionary')
            elif self.sn_dict[addr] == data[0]:
                self.receive_dict[addr] = data[1:]
                self.event_dict[addr].set()


class VehicleDatabase:
    def __init__(self, db_path='label.json'):
        # Load existing database or create a new one if it doesn't exist
        self.db = TinyDB(db_path)
    
    def update(self, vin, status):
        # Check if the record with the specified VIN already exists
        query = Query()
        if self.db.contains(query.vin == vin):
            # If it exists, update it with the new status
            self.db.update({'vin': vin, 'status': status}, query.vin == vin)
        else:
            # Otherwise, insert a new entry
            self.db.insert({'vin': vin, 'status': status})