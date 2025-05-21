import socket
import yaml
import logging
import subprocess
import os
import shlex
import datetime
from tinydb import TinyDB, Query
import requests
from flask import jsonify

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)


f = open('devices.yaml', 'r')
device_list = yaml.safe_load(f)
f.close()
audio_folder = './audio'

def get_audio_filename(vin):
    audiofiles = sorted(os.listdir(audio_folder), reverse=True)
    for audiofile in audiofiles:
        if audiofile.startswith(vin) and (audiofile.endswith('.wav') or audiofile.endswith('.aac')):
            return audiofile
    return ''

class Port_controller:

    def __init__(self):
        self.port_list = [i for i in range(23000, 23010, 2)]

    def get_port(self):
        logger.info("number of ports %d" % len(self.port_list))
        for port in self.port_list:
            logger.info("checking %d" % port)
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
            logger.info("Port is in use: %d" % e)
        sock.close()
        return result

class Receive:

    def __init__(self, vin, port, protocol='rtp'):

        # port
        self.port = port

        print('the port is', port)

        self.audio_filename = self.get_audio_filename(vin)

        if protocol == 'rtp':
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
                'a=rtpmap:97 L24/48000/2\n'

            self.sdp_filename = self.get_sdp_filename(vin)
            f = open(self.sdp_filename, 'w')
            f.write(sdp)
            f.close()

            # thread for receiving
            cmd = 'ffmpeg -protocol_whitelist file,http,rtp,tcp,udp -i %s -acodec pcm_s24le %s' % (self.sdp_filename, self.audio_filename)
        else:
            cmd = 'ffmpeg -f s32le -ac 2 -ar 48000 -i \'tcp://0.0.0.0:%d?listen=1\' -acodec copy %s' % (port, self.audio_filename)
        
        print(cmd)
        cmd = shlex.split(cmd)
        self.receive_thread = subprocess.Popen(cmd)

    def stop(self):
        self.receive_thread.kill()
        print("returning port", self.port)
        return 'ok'
    
    def get_sdp_filename(self, vin):
        filename = vin + '.sdp'
        return os.path.join(audio_folder, filename)
    
    def get_audio_filename(self, vin):
        now = datetime.datetime.now()
        file_name = vin + '-' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.wav'
        return os.path.join(audio_folder, file_name)

class Pi_controller:

    def get_url(self, dest):
        return 'https://%s:22000' % dest

    def status(self, dest):
        try:
            response = requests.get(
                self.get_url(dest) + '/status',
                verify=False,
                timeout=5
            )
            if response.status_code == 200:
                print(response.json())
                return jsonify(response.json())
            else:
                print('Failed to get status:', response.status_code)
                return 'offline'
        except requests.exceptions.RequestException as e:
            print(f'Error getting status: {e}')
            return 'offline'

    def record(self, dest, port, protocol, test=False):
        try:
            response = requests.post(
                self.get_url(dest) + '/record',
                json={'port': port, 'protocol': protocol, 'test': test},
                verify=False,
                timeout=5
            )
            if response.status_code == 200:
                print('Recording started:', response.json())
                return response.json()['status']
            else:
                print('Failed to start recording:', response.status_code)
                return {'error': 'Failed to start recording', 'status_code': response.status_code}
        except requests.exceptions.RequestException as e:
            print(f'Error starting record: {e}')
            return {'error': str(e)}
        

    def stop(self, dest):
        '''Send a POST request to the /stop endpoint.'''
        try:
            response = requests.post(
                self.get_url(dest) + '/stop',
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                print('Recording stopped:', response.json())
                return response.json()['status']
            else:
                print('Failed to stop recording:', response.status_code)
                return {'error': 'Failed to stop recording', 'status_code': response.status_code}
        except requests.exceptions.RequestException as e:
            print(f'Error stopping record: {e}')
            return {'error': str(e)}

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