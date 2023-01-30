import subprocess
import time

class vpn:
    
    def __init__(self):
        self.vpn_thread = None
        self.command = 'sudo openvpn --config /home/pi/audio-pi-1.ovpn'
        
    def connect(self):
        if self.check():
            return 'It\'s already connected'
        self.vpn_thread = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if self.check():
            return 'connected!'
        else:
            return 'Failed\nlog:\t' + self.vpn_thread.stderr
        
    
    def check(self):
        process = subprocess.run(["ifconfig"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8", timeout=1)
        return '10.94.0.' in process.stdout
        

class record:
    
    def __init__(self):
        self.record_thread = None
        self.command = '/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4 | /usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://10.94.0.31:23000 -sdp_file /home/pi/24.sdp'
    
    def record(self):
        if self.record_thread is not None and self.record_thread.poll() is None:
            return 'it\'s already recording'
        self.record_thread = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)
        if self.record_thread.poll() is None:
            return 'recording...'
        else:
            return  'Failed\nlog:\t' + self.record_thread.stderr
    
    def stop(self):
        if self.record_thread is None or self.record_thread.poll() is not None:
            return 'nothing to stop'
        else:
            self.record_thread.kill()
            return 'stopped'