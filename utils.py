import subprocess
import time
import shlex
import yaml
from datetime import datetime
import os
import socket
import requests

f = open('config.yaml')
d = yaml.safe_load(f)
f.close()
vpn_network = d['vpn_network']
server_ip = d['server_ip']
save_local = d['save_local']
audio_folder = d['audio_folder']


if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)
    
def get_audio_filename(vin):
    now = datetime.now()
    file_name = 'vin-' + vin + '-' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.wav'
    return os.path.join(audio_folder, file_name)

def get_sdp_filename(vin):
    filename = 'vin-' + vin + '.sdp'
    return os.path.join(audio_folder, filename)

def report(vin, status):
    r = requests.get(url='http://' + server_ip + ':8000/report/' + vin + '/' + status)
    return r.text

class port_controll:
    
    def __init__(self):
        self.port_list = [i for i in range(23000, 24000, 2)]
        
    def get_port(self):
        for port in self.port_list:
            if self.check_port(port):
                self.port_list.remove(port)
                return port
        return -1
    
    def return_port(self, port):
        self.port_list.append(port)
    
    def check_port(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = False
        try:
            sock.bind((server_ip, port))
            result = True
        except:
            print("Port is in use")
        sock.close()
        return result

class car_table:
    
    def __init__(self, filename):
        self.filename = filename
        self.table = {}
        if os.path.exists(filename):
            f = open(filename, 'r')
            for line in f.read().splitlines():
                vin, status = line.split(',')
                self.table[vin] = status
            f.close()
        
    def update(self, vin, status):
        if (vin in self.table and self.table[vin] != status) or vin not in self.table:
            self.table[vin] = status
            f = open(self.filename, 'w')
            for v, s in self.table.items():
                f.write(v + ',' + s + '\n')
            f.close()
        return 'car ' + vin + ' has been updated to ' + status
        
class receive:
    
    def __init__(self, vin, port_controller):
        
        # port
        self.port_controller = port_controller
        self.port = port_controller.get_port()
        
        print('------------------------------------------')
        print('the selected port for %s is'%vin, self.port)
        print('------------------------------------------')
    
        # sdp
        sdp = 'SDP:\n' + \
        'v=0\n' + \
        'o=- 0 0 IN IP4 127.0.0.1\n' + \
        's=No Name\n' + \
        'c=IN IP4 %s\n'%server_ip + \
        't=0 0\n' + \
        'a=tool:libavformat 58.20.100\n' + \
        'm=audio %s RTP/AVP 97\n'%self.port + \
        'b=AS:4608\n' + \
        'a=rtpmap:97 L24/48000/4\n'
        
        self.sdp_filename = get_sdp_filename(vin)
        f = open(self.sdp_filename, 'w')
        f.write(sdp)
        f.close()
        
        # thread for receiving
        cmd = shlex.split('ffmpeg -protocol_whitelist file,http,rtp,tcp,udp -i %s -acodec pcm_s24le %s'%(self.sdp_filename, get_audio_filename(vin)))
        self.receive_thread = subprocess.Popen(cmd)
        
    def stop(self):
        self.receive_thread.kill()
        self.port_controller.return_port(self.port)
    
        

class vpn:
    
    def __init__(self):
        self.vpn_thread = None
        self.args = shlex.split('sudo openvpn --config /home/pi/audio-pi-1.ovpn')
        
    def connect(self):
        if self.check():
            return 'It\'s already connected'
        self.vpn_thread = subprocess.Popen(self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for i in range(5):
            time.sleep(2)
            if self.check():
                return 'Connected'
        self.vpn_thread.kill()
        return 'Failed, please try again later..'
    
    def check(self):
        process = subprocess.run(["ifconfig"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", timeout=1)
        return vpn_network in process.stdout
        

class record:
    
    def __init__(self):
        self.record_thread = None
        self.stream_thread = None
        self.record_args = shlex.split('/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4')
    
    def record(self, vin):
        if self.record_thread is not None and self.record_thread.poll() is None:
            return 'it\'s already recording'
        
        r = requests.get(url='http://' + server_ip + ':8000/receive/' + vin)
        self.port = r.text
        print('got port:', self.port)
        
        record_cmd = self.get_record_cmd()
        stream_cmd = self.get_stream_cmd(vin)
        
        self.record_thread = subprocess.Popen(record_cmd, stdout=subprocess.PIPE)
        self.stream_thread = subprocess.Popen(stream_cmd, stdin=self.record_thread.stdout)
        time.sleep(2)
        if self.record_thread.poll() is None:
            return 'recording...'
        else:
            return  'Failed\nlog:\t'
    
    def stop(self, vin):
        if self.record_thread is None or self.record_thread.poll() is not None:
            return 'nothing to stop'
        else:
            requests.post(url='http://' + server_ip + ':8000/stop/' + vin)
            self.stream_thread.kill()
            self.record_thread.kill()
            return 'stopped'
        
    def get_record_cmd(self):
        return shlex.split('/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4')
    
    def get_stream_cmd(self, vin):
        addr = server_ip + ':' + self.port
        if save_local:
            cmd = 'sudo /usr/bin/ffmpeg -re -i - -acodec copy %s -acodec pcm_s24be -f rtp rtp://%s'%(get_audio_filename(vin), addr)
        else:
            cmd = '/usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s'%(addr)
            
        print(vin)
        print(cmd)
        return shlex.split(cmd)