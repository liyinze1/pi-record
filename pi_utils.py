import subprocess
import yaml
import pi_mic
import logging
import os
import signal
import serial
import time
import atexit
import datetime
import threading

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

class ATCommandInterface:
    def __init__(self, port='/dev/ttyUSB2', baudrate=115200, timeout=1):
        """Initialize the serial connection."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"Connected to {port} at {baudrate} baud.")
        
        self.log = True
        self.thread = threading.Thread(target=self.start_logging)
        self.thread.start()
        
        # Register the close method to be called on program exit
        atexit.register(self.close)

    def send_command(self, command):
        self.ser.write(command)
        time.sleep(0.5)
        response = self.ser.read_all().decode('ascii', errors='ignore').strip()
        return response

    def close(self):
        """Close the serial connection."""
        if self.ser.is_open:
            self.ser.close()
            print("Connection closed.")
        self.log = False
        self.thread.join()

    def start_logging(self, filename='log.txt', interval=30):
        while self.log:
            t = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
            CSQ = self.send_command(b'AT+CSQ\r')
            COPS = self.send_command(b'AT+COPS?\r')
            CPSI = self.send_command(b'AT+CPSI?\r')
            with open(filename, 'a') as f:
                f.write(t + '\n' + CSQ + '\n' + COPS + '\n' + CPSI + '\n')
    
            time.sleep(interval)

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
            
    def check(self):
        '''
            return True if recording
        '''
        return self.record_thread is not None and self.record_thread.poll() is None
            
    def status(self):
        if self.check():
            return 'recording'
        else:
            return 'ready'

    def record(self, ip, port):
        
        if self.check():
            return 'recording'

        stream_cmd = '/usr/bin/arecord -D plughw:CARD=ADCX140,DEV=0 -f S32_LE -r 48000 -c 1 -d %d | /usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s:%d' % (self.timeout, ip, port)
        
        self.record_thread = subprocess.Popen(stream_cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, start_new_session=True)
        
        print('Start to record')
        print(stream_cmd)
        return 'recording'

    def stop(self):

        if self.check():
            # self.stream_thread.kill()
            # self.record_thread.kill()
            # self.led.off()
            os.killpg(os.getpgid(self.record_thread.pid), signal.SIGTERM)
        return 'stopped'
        

    