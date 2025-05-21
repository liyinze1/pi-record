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
import requests
import RPi.GPIO as GPIO
from datetime import datetime

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

f = open('devices.yaml', 'r')
device_list = yaml.safe_load(f)
f.close()
audio_folder = './audio'

class Ink_screen_controller:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200, timeout=1):
        """Initialize the serial connection."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            print(f"Connected to {port} at {baudrate} baud.")
        except Exception as e:
            print('error', e)
            
    def update_message(self, msg):
        """Update the ink screen with the given message."""
        msg = 'M' + msg + datetime.now().strftime(' updated_at:%Y-%m-%d-%H:%M:%S')
        self.ser.write(msg.encode('ascii'))
        
    def update_token(self, token):
        """Update the ink screen with the given token."""
        msg = 'T' + token
        print('writing to E-INK:', msg)
        self.ser.write(msg.encode('ascii'))

class ATCommandInterface:
    def __init__(self, port='/dev/ttyUSB2', baudrate=115200, timeout=1):
        """Initialize the serial connection."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        try:
            self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
            print(f"Connected to {port} at {baudrate} baud.")
            self.log = True
            self.thread = threading.Thread(target=self.start_logging)
            self.thread.start()
            # Register the close method to be called on program exit
            atexit.register(self.close)
        except Exception as e:
            print('error', e)
            
        self.mode_verbose = ''
        self.mode = ''

    def send_command(self, command):
        self.ser.write(command)
        time.sleep(1)
        response = self.ser.read_all().decode('ascii', errors='ignore').strip()
        return response

    def close(self):
        """Close the serial connection."""
        if self.ser.is_open:
            self.ser.close()
            print("Connection closed.")
        self.log = False
        self.thread.join()
        
    def get_ip(self):
        try:
            ip = requests.get('https://api.ipify.org').content.decode('utf8')
            return True, ip
        except Exception as e:
            return False, f'Error starting record: {e}'

    def start_logging(self, filename='log.txt', interval=30):
        while self.log:
            t = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
            
            connection, ip = self.get_ip()
            
            CREG = self.send_command(b'AT+CREG?\r').partition('\n')[0]
            time.sleep(0.2)
            CSQ = self.send_command(b'AT+CSQ\r').partition('\n')[0]
            time.sleep(0.2)
            COPS = self.send_command(b'AT+COPS?\r').partition('\n')[0]
            time.sleep(0.2)
            CPSI = self.send_command(b'AT+CPSI?\r').partition('\n')[0]
            
            print('CREG:', CREG)
            print('CSQ:', CSQ)
            print('COPS:', COPS)
            print('CPSI:', CPSI)
                
            
            t = 'time: ' + t
            ip = 'ip: ' + ip
            msg = '<br>'.join([t, ip, CREG, CSQ, COPS, CPSI])
            self.mode_verbose = msg
            self.mode = CPSI.split(':')[1].split(',')[0].strip()
            # with open(filename, 'a') as f:
            #     f.write(msg)
            time.sleep(interval)

class LED_controller:
    
    def __init__(self):
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BOARD)
            self.pin_red = 13
            self.pin_green = 15 
        elif GPIO.getmode() == GPIO.BCM:
            self.pin_red = 27
            self.pin_green = 22
        elif GPIO.getmode() == GPIO.BOARD:
            self.pin_red = 13
            self.pin_green = 15
        GPIO.setup(self.pin_red, GPIO.OUT)
        GPIO.setup(self.pin_green, GPIO.OUT)
        
    def ready(self):
        GPIO.output(self.pin_red, GPIO.HIGH)
        GPIO.output(self.pin_green, GPIO.LOW)
        
    def record(self):
        GPIO.output(self.pin_red, GPIO.LOW)
        GPIO.output(self.pin_green, GPIO.HIGH)
        
    def off(self):
        GPIO.output(self.pin_red, GPIO.LOW)
        GPIO.output(self.pin_green, GPIO.LOW)
        
        
class Pi_recorder:

    def __init__(self):
        
        os.system('ffmpeg') # warm up ffmpeg
        
        self.record_thread = None
        pi_mic.initialize()
        self.at = ATCommandInterface()
        self.ink = Ink_screen_controller()
        
        self.led = LED_controller()
        
        with open('pi.yaml', 'r') as f:
            data = yaml.safe_load(f)
            self.timeout = data['timeout']
            
        self.get_token()
        self.led.ready()
            
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
        
    def mode(self):
        return self.at.mode
    
    def mode_verbose(self):
        return self.at.mode_verbose

    def record(self, ip, port, protocol, test):
        
        print('ip:', ip, 'port:', port, 'protocol:', protocol, 'test:', test)
        
        if self.check():
            return 'recording'
        
        if protocol == 'rtp':
            if test:
                stream_cmd = '/usr/bin/ffmpeg -re -i sine.wav -acodec pcm_s24be -f rtp rtp://%s:%d' % (ip,port)
            else:
                stream_cmd = '/usr/bin/arecord -D plughw:CARD=ADCX140,DEV=0 -f S32_LE -r 48000 -c 2 -d %d | /usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s:%d' % (self.timeout, ip, port)
        else:
            if test:
                stream_cmd = '/usr/bin/ffmpeg -re -i sine.wav -acodec copy -f s32le tcp://%s:%d' % (ip,port)
            else:
                stream_cmd = '/usr/bin/arecord -D plughw:CARD=ADCX140,DEV=0 -f S32_LE -r 48000 -c 2 -d %d | /usr/bin/ffmpeg -re -i - -acodec copy -f s32le tcp://%s:%d' % (self.timeout, ip, port)
        
        
        self.record_thread = subprocess.Popen(stream_cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, start_new_session=True)
        
        print('Start to record')
        print(stream_cmd)
        self.ink.update_message('Recording ... ' + self.at.mode)
        self.led.record()
        return 'recording'
    
    def stop(self):

        if self.check():
            # self.stream_thread.kill()
            # self.record_thread.kill()
            # self.led.off()
            os.killpg(os.getpgid(self.record_thread.pid), signal.SIGTERM)
        self.ink.update_message('Stopped ...' + self.at.mode)
        self.led.ready()
        return 'stopped'
        
    def get_token(self):
        self.ink.update_message('Booting please wait...')
        while True:
            try:
                token = requests.get('https://%s:9925/token'% (device_list['cloud']), verify=False, timeout=5).json()['token']
                if token:
                    break
            except Exception as e:
                print('error', e)
            print('Retrying to get token in 5s...')
            time.sleep(5)
        print('token:', token)
        self.ink.update_token(token)
        time.sleep(1)
        self.ink.update_message('Ready ...' + self.at.mode)

