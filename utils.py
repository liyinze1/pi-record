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
    audio_folder = d['audio_folder']
    vpn_start_cmd = d['vpn_start']

class car_table:
    def __init__(self, filename):
        self.filename = filename

    def update(self, vin, status):
        with open(self.filename, "a") as f:
            f.write(vin + ',' + status + '\n')
        return 'car ' + vin + ' has been updated to ' + status

if not os.path.exists(audio_folder):
    os.makedirs(audio_folder)

# pi, server
def get_audio_filename(vin):
    now = datetime.now()
    file_name = 'vin-' + vin + '-' + now.strftime('%Y%m%d%H%M%S') + '.wav'
    return os.path.join(audio_folder, file_name)

# server
def get_sdp_filename(vin):
    filename = 'vin-' + vin + '.sdp'
    return os.path.join(audio_folder, filename)

# pi
def report_to_server(vin, status):
    r = requests.get(url='http://' + server_ip +
                        ':8000/report/' + vin + '/' + status)
    return r.text

# pi, server
def check_last_audio():
    audios = [audio for audio in os.listdir(audio_folder) if audio.endswith('wav')]
    audios.sort(key=lambda x: int(x.split('-')[2]))
    return audios[-1]

def delete_last_audio(audio_name):
    try:
        os.system('rm -f %s' % os.path.join(audio_folder, audio_name))
        return 'Successfully deleted'
    except OSError as e:
        return 'Failed to delete'

# server
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

# server
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
        
        logger.info('port:%d'%self.port)

        self.audio_filename = get_audio_filename(vin)
        # thread for receiving
        cmd = 'ffmpeg -protocol_whitelist file,http,rtp,tcp,udp -i %s -acodec pcm_s24le %s' % (
            self.sdp_filename, self.audio_filename)
        logger.info(cmd)
        cmd = shlex.split(cmd)
        self.receive_thread = subprocess.Popen(cmd)

    def stop(self):
        self.receive_thread.kill()
        logger.info("returning port %s", self.port)
        self.port_controller.return_port(self.port)
        
    def stop_test(self):
        self.receive_thread.wait()
        self.receive_thread.kill()
        import soundfile as sf
        data, sr = sf.read(self.audio_filename)
        loss_rate = 1 - len(data) / (48e4)
        f.close()
        self.port_controller.return_port(self.port)
        return '%.2f%%' % (loss_rate * 100)
        

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

        # process = subprocess.run(["ifconfig"], shell=True, stdout=subprocess.PIPE,
        #                          stderr=subprocess.PIPE, encoding="utf-8", timeout=1)
        return res

    def shut_down(self):
        logger.info("shutting down")
        cmd = shlex.split('sudo shutdown now')
        try:
            self.vpn_thread = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return 'Initialted shutdown..'
        except:
            return 'cannot shutdown'
    
    def reboot(self):
        logger.info("rebooting")
        cmd = shlex.split('sudo reboot')
        try:
            self.vpn_thread = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return 'Initialted reboot'
        except:
            return 'cannot reboot'

class record:

    def __init__(self):
        self.record_thread = None
        self.record_filename = None

    def record(self, vin, save_location):
        if self.record_thread is not None and self.record_thread.poll() is None:
            return 'already recording'
        
        if save_location is not 'pi':
            try:
                requests.get(url='http://' + server_ip + ':8000/check-vpn', timeout=2)
            except Exception as e:
                return 'bad connection to server'

        self.vin = vin
        self.save_location = save_location
        stream_cmd = self.get_stream_cmd(vin, save_location)

        if save_location == 'test':
            # wait for server to start recieving
            time.sleep(3)
        
        self.record_thread = subprocess.Popen(stream_cmd, shell=True, stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE, start_new_session=True)

        logger.info("recored thread %s", self.record_thread)
        # self.record_thread = subprocess.Popen(record_cmd, stdout=subprocess.PIPE)
        # self.stream_thread = subprocess.Popen(stream_cmd, stdin=self.record_thread.stdout)
        # time.sleep(2)
        if self.record_thread.poll() is None:
            return 'recording...'
        else:
            return 'Failed\nlog:\t'

    def stop(self):
        if self.record_thread is None or self.record_thread.poll() is not None:
            return 'nothing to stop'
        else:
            if self.save_location in ('server', 'both'):
                requests.post(url='http://' + server_ip + ':8000/stop/' + self.vin)
            # self.stream_thread.kill()
            # self.record_thread.kill()
            os.killpg(os.getpgid(self.record_thread.pid), signal.SIGTERM)
            return self.vin + ' has been stopped'
        
    def stop_test(self):
        self.record_thread.wait()
        # get loss rate
        r = requests.get(url='http://' + server_ip + ':8000/stop-test')
        return r.text

    def get_stream_cmd(self, vin, save_location):        
        self.record_filename = get_audio_filename(vin)
        if save_location == 'pi':
            # locally
            cmd = '/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4 {}'.format(self.record_filename)
        else:
            # get port number from server
            r = requests.get(url='http://' + server_ip +
                             ':8000/receive/' + vin)
            port = r.text
            logger.info('got port: %s', port)
            addr = server_ip + ':' + port
            
            if save_location == 'server':
                # server only
                cmd = '/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4 | /usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s' % (addr)
            elif save_location == 'both':
                # save both
                cmd = '/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4 | /usr/bin/ffmpeg -re -i - -acodec copy %s -acodec pcm_s24be -f rtp rtp://%s' % (self.record_filename, addr)
            else:
                # test 10s
                cmd = '/usr/bin/arecord -Dac108 -f S32_LE -r 48000 -c 4 -d 10 | /usr/bin/ffmpeg -re -i - -acodec pcm_s24be -f rtp rtp://%s' % (addr)
        
        logger.info("vin %s", vin)
        logger.info("command %s", cmd)
        return cmd
