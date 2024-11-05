import subprocess
import yaml
import pi_mic
import logging
import threading
import os
import signal

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)



class Pi_recorder:

    def __init__(self):
        self.record_thread = None
        # self.record_filename = None
        # self.timer = None
        # self.kill_timer = False
        
        pi_mic.initialize()
        
        with open('pi.yaml', 'r') as f:
            data = yaml.safe_load(f)
            self.timeout = data['timeout']
            
    def status(self):
        if self.record_thread is not None and self.record_thread.poll() is None:
            return b'recording'
        else:
            return b'ready'

    def record(self, ip, port):
        

        stream_cmd = '/usr/bin/arecord -D plughw:CARD=ADCX140,DEV=0 -f S32_LE -r 48000 -c 4 -d %d | /usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s:%d' % (self.timeout, ip, port)
        
        self.record_thread = subprocess.Popen(stream_cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, start_new_session=True)
        
        print('Start to record')
        
        return b'recording'

    def stop(self):

        # self.stream_thread.kill()
        # self.record_thread.kill()
        # self.led.off()
        os.killpg(os.getpgid(self.record_thread.pid), signal.SIGTERM)
        return b'stopped'
        

    