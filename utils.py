import subprocess
import time
import shlex

server_ip = '10.94.0.31'
vpn_network = '10.94.0'

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
        self.stream_args = shlex.split('/usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s:23000 -sdp_file /home/pi/24.sdp'%server_ip)
    
    def record(self):
        if self.record_thread is not None and self.record_thread.poll() is None:
            return 'it\'s already recording'
        self.record_thread = subprocess.Popen(self.record_args, stdout=subprocess.PIPE)
        self.stream_thread = subprocess.Popen(self.stream_args, stdin=self.record_thread.stdout)
        time.sleep(2)
        if self.record_thread.poll() is None:
            return 'recording...'
        else:
            return  'Failed\nlog:\t'
    
    def stop(self):
        if self.record_thread is None or self.record_thread.poll() is not None:
            return 'nothing to stop'
        else:
            self.stream_thread.kill()
            self.record_thread.kill()
            return 'stopped'