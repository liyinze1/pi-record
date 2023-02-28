import subprocess
import time
import shlex
import yaml
from datetime import datetime
import os
import socket
import requests
import os
import signal

import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)

with open('config.yaml') as f:
    d = yaml.safe_load(f)
    vpn_network = d['vpn_network']
    server_ip = d['server_ip']
    save_local = d['save_local']
    audio_folder = d['audio_folder']
    vpn_start_cmd = d['vpn_start']
    local_only = d['local_only']

class car_table:

    def __init__(self, filename):
        self.filename = filename

    def update(self, vin, status):
        with open(self.filename, "a") as f:
              f.write(vin + ',' + status + '\n')
        return 'car ' + vin + ' has been updated to ' + status

if local_only:
    ct = car_table('car_table.csv')


if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)


def get_audio_filename(vin):
    now = datetime.now()
    file_name = 'vin-' + vin + '-' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.wav'
    return os.path.join(audio_folder, file_name)


def get_sdp_filename(vin):
    filename = 'vin-' + vin + '.sdp'
    return os.path.join(audio_folder, filename)

def report(vin, vin_file, status):
    if vin_file == None:
        return "no recording"
    if not(vin in vin_file):
        return "no recording for new vin"
    if local_only:
        return  ct.update(vin_file, status)
    else:
        r = requests.get(url='http://' + server_ip +
                        ':8000/report/' + vin_file + '/' + status)
        return r.text


class port_controll:

    def __init__(self):
        self.port_list = [i for i in range(23000, 23010, 2)]

    def get_port(self):
        logger.info("number of ports %s", len(self.port_list))
        for port in self.port_list:
            logger.info("checking  %s", port)
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
            # sock.bind((server_ip, port))
            sock.bind(('0.0.0.0', port))
            result = True
        except Exception as e:
            logger.info("Port is in use  %s", e)
        sock.close()
        return result





class receive:

    def __init__(self, vin, port_controller):

        # port
        self.port_controller = port_controller
        self.port = port_controller.get_port()

        logger.info('the selected port for %s is %s', vin, self.port)

        # sdp
        sdp = 'SDP:\n' + \
            'v=0\n' + \
            'o=- 0 0 IN IP4 127.0.0.1\n' + \
            's=No Name\n' + \
            'c=IN IP4 %s\n' % server_ip + \
            't=0 0\n' + \
            'a=tool:libavformat 58.20.100\n' + \
            'm=audio %s RTP/AVP 97\n' % self.port + \
            'b=AS:4608\n' + \
            'a=rtpmap:97 L24/48000/4\n'

        self.sdp_filename = get_sdp_filename(vin)
        f = open(self.sdp_filename, 'w')
        f.write(sdp)
        f.close()

        # thread for receiving
        cmd = 'ffmpeg -protocol_whitelist file,http,rtp,tcp,udp -i %s -acodec pcm_s24le %s' % (
            self.sdp_filename, get_audio_filename(vin))
        logger.info(cmd)
        cmd = shlex.split(cmd)
        self.receive_thread = subprocess.Popen(cmd)

    def stop(self):
        self.receive_thread.kill()
        logger.info("returning port %s", self.port)
        self.port_controller.return_port(self.port)


class vpn:

    def __init__(self):
        self.vpn_thread = None
        # self.args = shlex.split('sudo openvpn --config /home/pi/audio-pi-1.ovpn')

        self.args = shlex.split(vpn_start_cmd)

    def connect(self):
        logger.info("connecting vpn with %s", vpn_start_cmd)
        # if self.check():
        #    return 'It\'s already connected'
        try:
            self.vpn_thread = subprocess.Popen(
            self.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for i in range(5):
                time.sleep(1)
                if self.check():
                    return 'Connected'
            self.vpn_thread.kill()
        except:
            pass
        return 'Failed to conncet vpn, please try again later..'

    def check(self):
        try:
            r = requests.get(url='http://' + server_ip +
                             ':8000/check-vpn', timeout=2)
            res = r.text + '\n'
        except Exception as e:
            res = str(e) + '\n'

        process = subprocess.run(["ifconfig"], shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, encoding="utf-8", timeout=1)
        return res + process.stdout

    def shut_down(self):
        logger.info("shutting down")
        cmd = shlex.split('sudo shutdown now')
        try:
            self.vpn_thread = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return 'Initialted shutdown..'
        except:
            return 'cannot shutdown'       


class record:

    def __init__(self):
        self.record_thread = None
        self.record_filename = None
        # self.stream_thread = None
        # self.record_args = shlex.split('/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4')
        # self.record_args = shlex.split('/usr/bin/arecord -Dac108 -f S24_LE -r 48000 -c 4')

    def record(self, vin):
        if self.record_thread is not None and self.record_thread.poll() is None:
            return 'it\'s already recording'

        self.record_filename = get_audio_filename(vin)

        if local_only:
            logger.info('Local recording only')
            stream_cmd = '/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4 {}'.format(self.record_filename)
        else:
            r = requests.get(url='http://' + server_ip +
                             ':8000/receive/' + vin)
            self.port = r.text
            logger.info('got port: %s', self.port)
            stream_cmd = self.get_stream_cmd_new(vin)

        # record_cmd = self.get_record_cmd()
        # stream_cmd = self.get_stream_cmd(vin)

        logger.info(stream_cmd)

        self.record_thread = subprocess.Popen(stream_cmd,  shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, start_new_session=True)

        logger.info("recored thread %s", self.record_thread)

        # self.record_thread = subprocess.Popen(record_cmd, stdout=subprocess.PIPE)
        # self.stream_thread = subprocess.Popen(stream_cmd, stdin=self.record_thread.stdout)
        time.sleep(2)
        if self.record_thread.poll() is None:
            return 'recording...'
        else:
            return 'Failed\nlog:\t'

    def stop(self, vin):
        if self.record_thread is None or self.record_thread.poll() is not None:
            return 'nothing to stop'
        else:
            if not(local_only):
                requests.post(url='http://' + server_ip + ':8000/stop/' + vin)
            # self.stream_thread.kill()
            # self.record_thread.kill()
            os.killpg(os.getpgid(self.record_thread.pid), signal.SIGTERM)
            return 'stopped'

    def get_record_cmd(self):
        return shlex.split('/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4')

    def get_stream_cmd(self, vin):
        addr = server_ip + ':' + self.port
        if save_local:
            cmd = 'sudo /usr/bin/ffmpeg -re -i - -acodec copy %s -acodec pcm_s24be -f rtp rtp://%s'%(get_audio_filename(vin), addr)
        else:
            cmd = '/usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s' % (
                addr)

        logger.info("vin %s", vin)
        logger.info("command %s", cmd)
        return shlex.split(cmd)

    def get_stream_cmd_new(self, vin):
        addr = server_ip + ':' + self.port
        cmd = '/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4 | /usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s' % (
            addr)

        logger.info("vin %s", vin)
        logger.info("command %s", cmd)
        return cmd
